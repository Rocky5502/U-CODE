"""Candidate-archived history-conditional BES *adapter*, not joint Bayes search.

This policy uses the SAME action/patch/evidence ledger as uncertainty-free
beam search. It computes per-SHA conditional diagnostic look-ahead and a
one-step candidate-creation forecast; it is NOT a fully joint multicandidate
Bellman planner. Predictions are externally supplied TRAIN-only hypotheses,
never real inferred truths or evaluator labels.
"""
from dataclasses import dataclass
from typing import Sequence

from .budgeted_belief_search import CandidateAction
from .conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalState,
    Observation, plan_conditional, record_conditional,
)
from .matched_session import (
    SharedDecision, SharedSession, _common_catalog, commit_shared,
)
from .optimized_search import SearchAction
from .vector_policy import DIAGNOSTICS, GENERATORS, ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class ConditionalArchiveInputs:
    """Frozen policy-private forecasts keyed by candidate content digest."""
    priors: tuple[tuple[str, float], ...]
    kernels: tuple[tuple[str, ConditionalKernel], ...] = ()
    generation: tuple[CandidateAction, ...] = ()
    prices: ResourcePrices = ResourcePrices()
    rule: ReleaseRule = ReleaseRule(max_predicted_failure=0.1)
    horizon: int = 2
    max_candidates: int = 8

    def __post_init__(self):
        if not isinstance(self.priors, tuple) or not isinstance(self.kernels, tuple):
            raise ValueError("immutable priors and kernels required")
        if len(set(k for k, _ in self.priors)) != len(self.priors):
            raise ValueError("duplicate content-keyed prior")
        if len(set(k for k, _ in self.kernels)) != len(self.kernels):
            raise ValueError("duplicate content-keyed diagnostic kernel")
        if any(not isinstance(v, ConditionalKernel) for _, v in self.kernels):
            raise ValueError("typed conditional kernels required")
        if not isinstance(self.generation, tuple) or any(
                not isinstance(g, CandidateAction) for g in self.generation):
            raise ValueError("typed frozen candidate forecasts required")
        if len(set(g.action_id for g in self.generation)) != len(self.generation):
            raise ValueError("duplicate candidate forecast action")
        if type(self.horizon) is not int or not 1 <= self.horizon <= 4:
            raise ValueError("conditional horizon 1..4 required")
        if type(self.max_candidates) is not int or not 1 <= self.max_candidates <= 32:
            raise ValueError("candidate capacity 1..32 required")
        if not isinstance(self.prices, ResourcePrices) or not isinstance(
                self.rule, ReleaseRule):
            raise ValueError("typed risk rule and vector prices required")


@dataclass(frozen=True)
class ArchivePlan:
    decision: SharedDecision
    expected_proxy_utility: float
    baseline_stop_utility: float
    expanded_states: int
    interpretation: str = "SYNTHETIC_CONDITIONAL_PER_PATCH_NOT_JOINT_SEARCH"


def _posterior(session: SharedSession, candidate_sha: str,
               inputs: ConditionalArchiveInputs,
               catalog: tuple[SearchAction, ...]) -> ConditionalState:
    p = dict(inputs.priors)
    k = dict(inputs.kernels)
    if candidate_sha not in p:
        raise ValueError("missing frozen pre-outcome prior for archived candidate")
    # Validate prior even for candidates with no observations.
    state = ConditionalState(p[candidate_sha], session.initial_budget)
    observations = [o for o in session.state.observations
                    if o.candidate_sha256 == candidate_sha]
    if observations:
        if candidate_sha not in k:
            raise ValueError("missing frozen conditional kernel for existing evidence")
        action_index = {a.action_id: a for a in catalog}
        for obs in observations:
            act = action_index[obs.action_id]
            if act.kind not in DIAGNOSTICS or act.kind != obs.kind:
                raise ValueError("diagnostic action/catalog identity mismatch")
            probe = ConditionalProbe(act.action_id, act.kind, act.cost)
            state = record_conditional(state, probe, k[candidate_sha], obs.positive)
    # ConditionalBayes update above has *its own synthetic per-patch* costs.
    # Shared global reported consumption is authoritative for eligibility.
    return ConditionalState(state.prior, session.state.remaining, state.history)


def plan_conditional_archive(
    session: SharedSession,
    actions: Sequence[SearchAction],
    inputs: ConditionalArchiveInputs,
) -> ArchivePlan:
    """One-step generation forecast vs candidate-specific diagnostic search.

    Terminal value = MAX frozen predicted net release utility over archived
    patches. Evidence planning on each patch is conditional and depth-bounded,
    but ignores future diagnostics on OTHER patches. The current best
    other patch is an explicitly branchwise available outside option.
    Generation forecasts
    value the best new candidate vs retaining incumbent and do not generate
    actual patches. Never call this full multi-candidate Bellman optimality.
    """
    if not isinstance(session, SharedSession) or not isinstance(
            inputs, ConditionalArchiveInputs):
        raise TypeError("typed session and frozen model input required")
    if session.max_candidates != inputs.max_candidates:
        raise ValueError("matched archive cap differs")
    catalog = _common_catalog(actions)
    attempted = set(session.state.attempted)
    hashes = {c.sha256 for c in session.state.candidates}
    if set(dict(inputs.priors)) != hashes:
        raise ValueError("priors must exactly match archived candidate SHAs")
    if set(dict(inputs.kernels)) - hashes:
        raise ValueError("kernel references unknown archived candidate")
    forecasts = {a.action_id: a for a in inputs.generation}
    tools = {a.action_id: a for a in catalog}
    for fid, f in forecasts.items():
        if fid not in tools or f.kind != tools[fid].kind or f.cost != tools[fid].cost:
            raise ValueError("candidate forecast/action opportunity mismatch")
    if inputs.rule.unit_cost_penalty != 0:
        raise ValueError("planning resource prices must be charged only once")
    posterior = {sha: _posterior(session, sha, inputs, catalog)
                 for sha in sorted(hashes)}
    scores = {sha: terminal_value(state.prior, inputs.rule)
              for sha, state in posterior.items()}
    best_stop = max(scores.values(), default=0.0)
    best_sha = min((sha for sha, v in scores.items()
                    if abs(v-best_stop) <= 1e-12), default=None)
    best = SharedDecision("release" if best_stop > 0 else "abstain",
                          "release" if best_stop > 0 else "abstain",
                          best_sha if best_stop > 0 else None,
                          ResourceVector())
    best_score = best_stop
    expanded = 0

    # Candidate-specific diagnostics have exact conditional evidence history.
    # Each action is globally single-use regardless of target candidate.
    for sha, state in posterior.items():
        applicable = tuple(ConditionalProbe(a.action_id, a.kind, a.cost)
                           for a in catalog if a.kind in DIAGNOSTICS and (
                               a.action_id not in attempted or
                               a.action_id in {o.action_id for o in state.history}))
        if not applicable:
            continue
        if sha not in dict(inputs.kernels):
            # A kernel is mandatory only when a *feasible new diagnostic*
            # is available; not when all diagnostics have been spent.
            if any(p.action_id not in attempted and session.state.remaining.affordable(p.cost)
                   for p in applicable):
                raise ValueError("missing frozen kernel for feasible diagnostic")
            continue
        # Archive-preserving per-patch evidence: after EACH observable
        # outcome the policy can still release the best OTHER existing patch.
        # max(E[local value], incumbent) is mathematically WRONG because
        # it fails to evaluate the surviving incumbent on each branch.
        # This assumes diagnostics on this candidate do NOT update other
        # candidates; joint cross-candidate correlation needs the separate
        # correlated_archive_bes planner instead.
        incumbent_other = max(
            (v for other_sha, v in scores.items() if other_sha != sha),
            default=0.0,
        )
        plan = plan_conditional(
            state, applicable, dict(inputs.kernels)[sha], inputs.prices,
            inputs.rule, horizon=inputs.horizon,
            outside_option=incumbent_other,
        )
        expanded += plan.states_expanded
        if plan.action in ("release", "abstain"):
            continue
        act = tools[plan.action]
        global_value = plan.expected_net_utility
        proposal = SharedDecision(act.action_id, act.kind, sha, act.cost)
        if global_value > best_score + 1e-12 or (
                abs(global_value-best_score) <= 1e-12 and
                best.kind not in ("release", "abstain") and
                (proposal.action_id, sha) < (best.action_id, best.target_sha256)):
            best, best_score = proposal, global_value

    # Generation / repair preserve old archived candidates; prices paid once.
    if len(hashes) < session.max_candidates:
        for a in catalog:
            if a.kind not in GENERATORS or a.action_id in attempted or (
                    not session.state.remaining.affordable(a.cost)):
                continue
            if a.action_id not in forecasts:
                # Never invent an unprovided candidate-outcome distribution.
                continue
            targets = [None] if a.kind == "generate" else sorted(hashes)
            for target in targets:
                score = sum(
                    sc.probability * max(
                        best_stop,
                        terminal_value(sc.new_prior, inputs.rule)
                        if sc.new_prior is not None else best_stop,
                    ) for sc in forecasts[a.action_id].scenarios
                ) - a.cost.total_price(inputs.prices)
                expanded += 1
                proposal = SharedDecision(a.action_id, a.kind, target, a.cost)
                if score > best_score + 1e-12 or (
                    abs(score-best_score) <= 1e-12 and
                    best.kind not in ("release", "abstain") and
                    (proposal.action_id, proposal.target_sha256 or "") <
                    (best.action_id, best.target_sha256 or "")):
                    best, best_score = proposal, score

    return ArchivePlan(best, best_score, best_stop, expanded)


def record_conditional_archive(
    session: SharedSession, actions: Sequence[SearchAction],
    inputs: ConditionalArchiveInputs, decision: SharedDecision,
    *, reported_cost: ResourceVector,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
) -> SharedSession:
    """Enforce selected policy action; patch-prior refresh remains external."""
    if decision != plan_conditional_archive(session, actions, inputs).decision:
        raise ValueError("unselected conditional archive decision")
    return commit_shared(
        session, actions, decision, reported_cost=reported_cost,
        observed_positive=observed_positive,
        new_candidate_sha256=new_candidate_sha256,
    )
