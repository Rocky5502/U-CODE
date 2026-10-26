"""Finite-horizon JOINT candidate-archive conditional evidence search (offline).

Unlike conditional_archive.py, this exact bounded recursion can test different
patches and can generate/repair a SYMBOLIC future patch then test it later.
Exactness is only with respect to the supplied finite factorized transition
model, NOT general coding-agent/POMDP optimality. All priors, conditional
kernels and producer forecasts must be fitted on disjoint training data and
frozen before any held-out trial. No external execution or oracle access.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Sequence

from .conditional_bes import ConditionalKernel, Observation, _probability
from .matched_session import SharedDecision, SharedSession, _common_catalog, commit_shared
from .matched_opportunities import Opportunity, _expand_keys, _key, matched_opportunities
from .optimized_search import SearchAction
from .vector_policy import DIAGNOSTICS, GENERATORS, ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class SymbolicCandidateKey:
    """Branch-local hypothetical patch, NEVER a real executable SHA256."""
    action_id: str
    branch: int
    parent: object | None = None


@dataclass(frozen=True)
class CandidateBelief:
    sha256: str
    prior: float
    profile: str

    def __post_init__(self):
        if (not isinstance(self.sha256, str) or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)):
            raise ValueError("real candidate belief requires SHA256")
        _probability(self.prior, "frozen candidate prior")
        if not isinstance(self.profile, str) or not self.profile:
            raise ValueError("nonempty frozen diagnostic profile required")


@dataclass(frozen=True)
class ProducerOutcome:
    probability: float
    new_prior: float | None
    new_profile: str | None = None

    def __post_init__(self):
        _probability(self.probability, "producer outcome probability")
        if self.new_prior is None:
            if self.new_profile is not None:
                raise ValueError("failed producer cannot create diagnostic profile")
        else:
            _probability(self.new_prior, "hypothetical new candidate prior")
            if not isinstance(self.new_profile, str) or not self.new_profile:
                raise ValueError("successful producer needs frozen profile")


@dataclass(frozen=True)
class ProducerForecast:
    action_id: str
    kind: str
    target_profile: str | None
    target_history: tuple[Observation, ...]
    outcomes: tuple[ProducerOutcome, ...]

    def __post_init__(self):
        if self.kind not in GENERATORS or not self.action_id:
            raise ValueError("producer forecast action invalid")
        if self.kind == "generate" and (
            self.target_profile is not None or self.target_history
        ):
            raise ValueError("generate forecast must be target-free")
        if self.kind == "repair" and (
            not isinstance(self.target_profile, str) or not self.target_profile
        ):
            raise ValueError("repair forecast must be target-profile conditioned")
        if not isinstance(self.target_history, tuple) or any(
            not isinstance(h, Observation) for h in self.target_history
        ):
            raise ValueError("producer forecast needs typed visible history")
        if not isinstance(self.outcomes, tuple) or not self.outcomes or any(
            not isinstance(o, ProducerOutcome) for o in self.outcomes
        ):
            raise ValueError("nonempty typed producer outcomes required")
        if abs(sum(o.probability for o in self.outcomes) - 1.0) > 1e-9:
            raise ValueError("producer probabilities must sum to one")


@dataclass(frozen=True)
class FrozenJointInputs:
    initial: tuple[CandidateBelief, ...]
    kernels: tuple[tuple[str, ConditionalKernel], ...] = ()
    producers: tuple[ProducerForecast, ...] = ()
    prices: ResourcePrices = ResourcePrices()
    rule: ReleaseRule = ReleaseRule(max_predicted_failure=0.1)
    horizon: int = 2
    max_states: int = 30000

    def __post_init__(self):
        if not isinstance(self.initial, tuple) or any(
            not isinstance(x, CandidateBelief) for x in self.initial
        ) or len({x.sha256 for x in self.initial}) != len(self.initial):
            raise ValueError("unique typed real candidate beliefs required")
        if not isinstance(self.kernels, tuple) or any(
            not isinstance(p, str) or not isinstance(k, ConditionalKernel)
            for p, k in self.kernels
        ) or len({p for p, _ in self.kernels}) != len(self.kernels):
            raise ValueError("unique frozen diagnostic profiles required")
        if not isinstance(self.producers, tuple) or any(
            not isinstance(f, ProducerForecast) for f in self.producers
        ):
            raise ValueError("typed producer forecasts required")
        fkeys = [(f.action_id, f.kind, f.target_profile, f.target_history)
                 for f in self.producers]
        if len(fkeys) != len(set(fkeys)):
            raise ValueError("duplicate target/history-conditioned producer forecast")
        if not isinstance(self.prices, ResourcePrices) or not isinstance(
            self.rule, ReleaseRule
        ) or self.rule.unit_cost_penalty != 0:
            raise ValueError("typed prices and once-only cost penalty required")
        if type(self.horizon) is not int or not 1 <= self.horizon <= 4:
            raise ValueError("joint planning horizon must be 1..4")
        if type(self.max_states) is not int or not 1 <= self.max_states <= 100000:
            raise ValueError("joint planning state cap must be 1..100000")


@dataclass(frozen=True)
class _Candidate:
    key: object
    parent: object | None
    belief: float
    profile: str
    history: tuple[Observation, ...] = ()


@dataclass(frozen=True)
class JointPlan:
    decision: SharedDecision
    expected_proxy_utility: float
    stop_utility: float
    expanded_states: int
    interpretation: str = "SYNTHETIC_JOINT_FINITE_FACTORISED_ARCHIVE_MODEL_NOT_EMPIRICAL"


def _update(p: float, row, positive: bool) -> float:
    mass = (p * row.positive_if_acceptable
            + (1.0-p) * row.positive_if_unacceptable)
    if positive:
        if mass <= 0:
            raise ValueError("zero-probability positive observation")
        return min(1.0, max(0.0, p*row.positive_if_acceptable/mass))
    if mass >= 1:
        raise ValueError("zero-probability negative observation")
    return min(1.0, max(0.0, p*(1-row.positive_if_acceptable)/(1-mass)))


def plan_joint_archive(
    session: SharedSession, actions: Sequence[SearchAction],
    inputs: FrozenJointInputs,
) -> JointPlan:
    """Choose from a single shared action-target menu; fail on model gaps.

    Every feasible opportunity is evaluated, even if its predicted value is
    low. Missing conditional rows or producer forecasts fail CLOSED instead
    of giving treatment a smaller tool menu than the uncertainty-free policy.
    """
    if not isinstance(session, SharedSession) or not isinstance(
        inputs, FrozenJointInputs
    ):
        raise TypeError("typed shared session and frozen model required")
    catalog = _common_catalog(actions)
    _ = matched_opportunities(session, catalog)
    real = {c.sha256: c for c in session.state.candidates}
    beliefs = {b.sha256: b for b in inputs.initial}
    if set(real) != set(beliefs):
        raise ValueError("real candidate priors must exactly match shared archive")
    kernels = dict(inputs.kernels)
    forecasts = {
        (f.action_id, f.kind, f.target_profile, f.target_history): f
        for f in inputs.producers
    }
    tools = {a.action_id: a for a in catalog}
    for f in inputs.producers:
        if f.action_id not in tools or f.kind != tools[f.action_id].kind:
            raise ValueError("producer forecast/action catalog mismatch")
    candidates = []
    for sha in sorted(real):
        b = beliefs[sha]
        history = tuple(
            Observation(o.action_id, o.positive)
            for o in session.state.observations if o.candidate_sha256 == sha
        )
        p = b.prior
        for index, obs in enumerate(history):
            if b.profile not in kernels:
                raise ValueError("missing frozen kernel for existing evidence")
            row = kernels[b.profile].get(obs.action_id, history[:index])
            p = _update(p, row, obs.positive)
        candidates.append(_Candidate(sha, real[sha].parent_sha256,
                                     p, b.profile, history))
    expanded = [0]

    @lru_cache(maxsize=None)
    def solve(
        archive: tuple[_Candidate, ...], used: frozenset[str],
        budget: ResourceVector, depth: int,
    ):
        expanded[0] += 1
        if expanded[0] > inputs.max_states:
            raise ValueError("joint search state cap exceeded")
        stops = [(terminal_value(c.belief, inputs.rule), _key(c.key), c.key)
                 for c in archive]
        best_stop = max((v for v, _, _ in stops), default=0.0)
        best_val, best_op = best_stop, None
        if depth == 0:
            return best_val, best_op
        keys = tuple(c.key for c in archive)
        for op in _expand_keys(keys, used, budget, session.max_candidates, catalog):
            next_budget = budget.subtract(op.cost)
            next_used = used | {op.action_id}
            if op.kind in DIAGNOSTICS:
                target = next(c for c in archive if c.key == op.target)
                if target.profile not in kernels:
                    raise ValueError("missing frozen kernel for feasible diagnostic")
                row = kernels[target.profile].get(op.action_id, target.history)
                positive_mass = (target.belief*row.positive_if_acceptable
                                 + (1-target.belief)*row.positive_if_unacceptable)
                branches = ((True, positive_mass), (False, 1-positive_mass))
                future = 0.0
                for positive, mass in branches:
                    if mass <= 0:
                        continue
                    next_candidate = _Candidate(
                        target.key, target.parent,
                        _update(target.belief, row, positive),
                        target.profile,
                        target.history + (Observation(op.action_id, positive),),
                    )
                    next_archive = tuple(
                        next_candidate if c.key == target.key else c
                        for c in archive
                    )
                    future += mass * solve(next_archive, next_used, next_budget,
                                           depth-1)[0]
            else:
                target = (next((c for c in archive if c.key == op.target), None)
                          if op.kind == "repair" else None)
                fkey = (op.action_id, op.kind,
                        target.profile if target is not None else None,
                        target.history if target is not None else ())
                if fkey not in forecasts:
                    raise ValueError("missing target-conditioned producer forecast")
                future = 0.0
                for index, outcome in enumerate(forecasts[fkey].outcomes):
                    if outcome.probability <= 0:
                        continue
                    new_archive = archive
                    if outcome.new_prior is not None:
                        key = SymbolicCandidateKey(
                            op.action_id, index, target.key if target else None
                        )
                        new_archive += (_Candidate(
                            key, target.key if target else None,
                            outcome.new_prior, outcome.new_profile, (),
                        ),)
                    future += outcome.probability * solve(
                        new_archive, next_used, next_budget, depth-1
                    )[0]
            score = future - op.cost.total_price(inputs.prices)
            if (score > best_val + 1e-12 or
                (abs(score-best_val) <= 1e-12 and best_op is not None
                 and op.sort_key < best_op.sort_key)):
                best_val, best_op = score, op
        return best_val, best_op

    root = tuple(candidates)
    stop_values = [(terminal_value(c.belief, inputs.rule), _key(c.key), c.key)
                   for c in root]
    stop = max((v for v, _, _ in stop_values), default=0.0)
    eligible = sorted((k, key) for v, k, key in stop_values
                      if v > 0 and abs(v-stop) <= 1e-12)
    stop_target = eligible[0][1] if eligible else None
    value, chosen = solve(root, frozenset(session.state.attempted),
                          session.state.remaining, inputs.horizon)
    if chosen is None:
        terminal = "release" if stop_target is not None else "abstain"
        decision = SharedDecision(terminal, terminal, stop_target, ResourceVector())
    else:
        decision = chosen.as_decision()
    return JointPlan(decision, value, stop, expanded[0])


def record_joint_archive(
    session: SharedSession, actions: Sequence[SearchAction],
    inputs: FrozenJointInputs, decision: SharedDecision, *,
    reported_cost: ResourceVector,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
) -> SharedSession:
    if decision != plan_joint_archive(session, actions, inputs).decision:
        raise ValueError("unselected joint-archive decision")
    return commit_shared(
        session, actions, decision, reported_cost=reported_cost,
        observed_positive=observed_positive,
        new_candidate_sha256=new_candidate_sha256,
    )
