"""Exact bounded correlation-aware whole-archive evidence planning (OFFLINE).

Finite joint truth atoms permit a diagnostic on one patch to update beliefs
about *other* patches. Conditional diagnostic likelihoods depend on the
target's truth and its own visible history; producer outcomes may depend on
the repair parent's truth. This is exact only for that explicitly specified
finite model, NOT a calibrated risk certificate, generic POMDP solution,
independent metering, or observed coding-agent effectiveness.

No real patch generation, tool execution, model inference or hidden oracle.
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from .conditional_bes import ConditionalKernel, Observation, _probability
from .joint_conditional_bes import SymbolicCandidateKey
from .matched_opportunities import _expand_keys, _key, matched_opportunities
from .matched_session import SharedDecision, SharedSession, _common_catalog, commit_shared
from .optimized_search import SearchAction
from .vector_policy import DIAGNOSTICS, GENERATORS, ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class TruthAtom:
    """Probability of one vector of LATENT acceptability bits (not gold labels)."""
    bits: tuple[bool, ...]
    probability: float

    def __post_init__(self):
        if not isinstance(self.bits, tuple) or any(
            type(bit) is not bool for bit in self.bits
        ):
            raise ValueError("latent truth atom needs boolean tuple")
        _probability(self.probability, "joint atom probability")
        if self.probability <= 0:
            raise ValueError("joint atom must have positive support mass")


@dataclass(frozen=True)
class CandidateProfile:
    sha256: str
    profile: str

    def __post_init__(self):
        if (not isinstance(self.sha256, str) or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)):
            raise ValueError("candidate profile requires real SHA256")
        if not isinstance(self.profile, str) or not self.profile.strip():
            raise ValueError("candidate requires nonempty diagnostic profile")


@dataclass(frozen=True)
class CorrelatedProducerRow:
    """Frozen P(produced, child truth | repair-parent truth, visible history).

    'Produced' is the publicly observed fact of a new patch artifact.
    The child's correctness bit remains LATENT, never a visible outcome.
    For target-free generation, both parent-conditioned probabilities must
    agree: it is explicitly independent of the existing truth vector.
    """
    action_id: str
    kind: str
    target_profile: str | None
    target_history: tuple[Observation, ...]
    produced_if_parent_true: float
    produced_if_parent_false: float
    child_true_if_parent_true: float
    child_true_if_parent_false: float
    child_profile: str

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id:
            raise ValueError("producer action ID required")
        if self.kind not in GENERATORS:
            raise ValueError("producer kind must generate or repair")
        if not isinstance(self.target_history, tuple) or any(
            not isinstance(o, Observation) for o in self.target_history
        ):
            raise ValueError("producer history must be typed tuple")
        if self.kind == "generate":
            if self.target_profile is not None or self.target_history:
                raise ValueError("target-free generation cannot use target history")
            if (self.produced_if_parent_true != self.produced_if_parent_false
                or self.child_true_if_parent_true != self.child_true_if_parent_false):
                raise ValueError("target-free generation must be truth-independent")
        elif not isinstance(self.target_profile, str) or not self.target_profile:
            raise ValueError("repair needs target profile")
        for field in ("produced_if_parent_true", "produced_if_parent_false",
                      "child_true_if_parent_true", "child_true_if_parent_false"):
            _probability(getattr(self, field), field)
        if not isinstance(self.child_profile, str) or not self.child_profile:
            raise ValueError("producer needs child diagnostic profile")


@dataclass(frozen=True)
class FrozenCorrelatedInputs:
    """Joint prior is PRE-diagnostic, conditional on PUBLIC roster/production.

    Profiles and truth atom bits use lexicographic SHA256 order. The frozen
    prior must not be estimated from sealed held-out evaluator labels.
    """
    profiles: tuple[CandidateProfile, ...]
    prior: tuple[TruthAtom, ...]
    kernels: tuple[tuple[str, ConditionalKernel], ...] = ()
    producers: tuple[CorrelatedProducerRow, ...] = ()
    prices: ResourcePrices = ResourcePrices()
    rule: ReleaseRule = ReleaseRule(max_predicted_failure=0.1)
    horizon: int = 2
    max_states: int = 30000
    max_atoms: int = 256

    def __post_init__(self):
        if not isinstance(self.profiles, tuple) or any(
            not isinstance(p, CandidateProfile) for p in self.profiles
        ):
            raise ValueError("typed candidate profiles required")
        names = tuple(p.sha256 for p in self.profiles)
        if names != tuple(sorted(set(names))) or len(names) > 8:
            raise ValueError("unique SHA-sorted profiles; max eight candidates")
        if (not isinstance(self.prior, tuple) or not self.prior
            or any(not isinstance(a, TruthAtom) for a in self.prior)
            or any(len(a.bits) != len(names) for a in self.prior)
            or len({a.bits for a in self.prior}) != len(self.prior)):
            raise ValueError("unique typed joint atoms must match profile width")
        if abs(sum(a.probability for a in self.prior) - 1) > 1e-9:
            raise ValueError("joint prior probabilities must sum to one")
        if not isinstance(self.kernels, tuple) or any(
            not isinstance(p, str) or not p or not isinstance(k, ConditionalKernel)
            for p, k in self.kernels
        ) or len({p for p, _ in self.kernels}) != len(self.kernels):
            raise ValueError("unique typed frozen diagnostic kernels required")
        if not isinstance(self.producers, tuple) or any(
            not isinstance(p, CorrelatedProducerRow) for p in self.producers
        ):
            raise ValueError("typed frozen producer rows required")
        keys = [(p.action_id, p.kind, p.target_profile, p.target_history)
                for p in self.producers]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate producer forecast context")
        if not isinstance(self.prices, ResourcePrices) or not isinstance(
            self.rule, ReleaseRule
        ) or self.rule.unit_cost_penalty != 0:
            raise ValueError("typed prices and once-only planning costs required")
        if type(self.horizon) is not int or not 1 <= self.horizon <= 4:
            raise ValueError("horizon must be 1..4")
        if type(self.max_states) is not int or not 1 <= self.max_states <= 100000:
            raise ValueError("state cap must be 1..100000")
        if type(self.max_atoms) is not int or not 1 <= self.max_atoms <= 512:
            raise ValueError("atom cap must be 1..512")
        if len(self.prior) > self.max_atoms:
            raise ValueError("initial joint support exceeds atom cap")


@dataclass(frozen=True)
class _Candidate:
    key: object
    parent: object | None
    profile: str
    history: tuple[Observation, ...] = ()


@dataclass(frozen=True)
class CorrelatedPlan:
    decision: SharedDecision
    expected_proxy_utility: float
    stop_utility: float
    posterior_marginals: tuple[tuple[str, float], ...]
    expanded_states: int
    interpretation: str = "FINITE_SYNTHETIC_CORRELATED_TRUTH_MODEL_NOT_EMPIRICAL"


def _posterior_branch(
    atoms: tuple[TruthAtom, ...], index: int, row,
    positive: bool, max_atoms: int,
) -> tuple[float, tuple[TruthAtom, ...]]:
    weighted = []
    for atom in atoms:
        chance = (row.positive_if_acceptable if atom.bits[index]
                  else row.positive_if_unacceptable)
        mass = atom.probability * (chance if positive else 1-chance)
        if mass > 0:
            weighted.append((atom.bits, mass))
    total = sum(m for _, m in weighted)
    if total == 0:
        return 0.0, ()
    if len(weighted) > max_atoms:
        raise ValueError("joint hypothesis atom cap exceeded")
    return total, tuple(TruthAtom(bits, mass/total) for bits, mass in weighted)


def _producer_branches(
    atoms: tuple[TruthAtom, ...], index: int | None,
    row: CorrelatedProducerRow, max_atoms: int,
) -> tuple[tuple[float, tuple[TruthAtom, ...]],
           tuple[float, tuple[TruthAtom, ...]]]:
    failed, produced = [], []
    for atom in atoms:
        parent_true = atom.bits[index] if index is not None else False
        chance = (row.produced_if_parent_true if parent_true
                  else row.produced_if_parent_false)
        child_p = (row.child_true_if_parent_true if parent_true
                   else row.child_true_if_parent_false)
        if atom.probability*(1-chance) > 0:
            failed.append((atom.bits, atom.probability*(1-chance)))
        for truth, weight in ((True, child_p), (False, 1-child_p)):
            mass = atom.probability*chance*weight
            if mass > 0:
                produced.append((atom.bits + (truth,), mass))

    def normalize(weighted):
        total = sum(w for _, w in weighted)
        if not total:
            return 0.0, ()
        if len(weighted) > max_atoms:
            raise ValueError("joint hypothesis atom cap exceeded")
        return total, tuple(TruthAtom(bits, weight/total)
                            for bits, weight in weighted)
    return normalize(failed), normalize(produced)


def plan_correlated_archive(
    session: SharedSession, actions: Sequence[SearchAction],
    inputs: FrozenCorrelatedInputs,
) -> CorrelatedPlan:
    """Exact bounded dynamic program under a frozen correlated truth model.

    Every publicly feasible opportunity and every reachable positive-mass
    branch must have a model; missing rows fail CLOSED, not by removing
    treatment actions. The baseline is never passed this private model.
    """
    if not isinstance(session, SharedSession) or not isinstance(
        inputs, FrozenCorrelatedInputs
    ):
        raise TypeError("typed session and frozen correlated inputs required")
    catalog = _common_catalog(actions)
    matched_opportunities(session, catalog)
    real = {c.sha256: c for c in session.state.candidates}
    if set(real) != {p.sha256 for p in inputs.profiles}:
        raise ValueError("joint profiles must exactly match real archive")
    if session.max_candidates > 8:
        raise ValueError("correlated reference requires matched archive cap <=8")
    kernels = dict(inputs.kernels)
    forecasts = {
        (p.action_id, p.kind, p.target_profile, p.target_history): p
        for p in inputs.producers
    }
    catalog_by_id = {a.action_id: a for a in catalog}
    for p in inputs.producers:
        if (p.action_id not in catalog_by_id
            or catalog_by_id[p.action_id].kind != p.kind):
            raise ValueError("producer forecast/action catalog mismatch")
    archive = tuple(_Candidate(p.sha256, real[p.sha256].parent_sha256, p.profile)
                    for p in inputs.profiles)
    atoms = tuple(sorted(inputs.prior, key=lambda a: a.bits))
    # Replay only policy-visible diagnostics, chronologically, with exact
    # conditional contexts. Every outcome also updates correlated siblings.
    for observed in session.state.observations:
        index = next((i for i, c in enumerate(archive)
                      if c.key == observed.candidate_sha256), None)
        if index is None:
            raise ValueError("visible diagnostic references absent candidate")
        target = archive[index]
        if target.profile not in kernels:
            raise ValueError("missing frozen kernel for visible evidence")
        row = kernels[target.profile].get(observed.action_id, target.history)
        mass, updated = _posterior_branch(
            atoms, index, row, observed.positive, inputs.max_atoms)
        if mass == 0:
            raise ValueError("observed evidence has zero probability under joint prior")
        atoms = updated
        archive = tuple(
            _Candidate(c.key, c.parent, c.profile,
                       c.history + (Observation(observed.action_id,
                                                observed.positive),))
            if i == index else c
            for i, c in enumerate(archive)
        )
    root_marginals = tuple(
        (c.key, sum(a.probability for a in atoms if a.bits[i]))
        for i, c in enumerate(archive)
    )
    expansions = [0]

    def stopping(arch, distribution):
        values = [(terminal_value(
            sum(a.probability for a in distribution if a.bits[i]), inputs.rule),
            _key(c.key), c.key) for i, c in enumerate(arch)]
        stop = max((v for v, _, _ in values), default=0.0)
        eligible = sorted((k, key) for v, k, key in values
                          if v > 0 and abs(v-stop) <= 1e-12)
        return stop, eligible[0][1] if eligible else None

    @lru_cache(maxsize=None)
    def solve(arch, distribution, used, budget, depth):
        expansions[0] += 1
        if expansions[0] > inputs.max_states:
            raise ValueError("correlated joint state cap exceeded")
        best, _ = stopping(arch, distribution)
        choice = None
        if depth == 0:
            return best, choice
        for op in _expand_keys(
            tuple(c.key for c in arch), used, budget,
            session.max_candidates, catalog
        ):
            next_used = used | {op.action_id}
            next_budget = budget.subtract(op.cost)
            future = 0.0
            if op.kind in DIAGNOSTICS:
                index = next(i for i, c in enumerate(arch) if c.key == op.target)
                target = arch[index]
                if target.profile not in kernels:
                    raise ValueError("missing frozen kernel for feasible diagnostic")
                row = kernels[target.profile].get(op.action_id, target.history)
                for positive in (True, False):
                    mass, updated = _posterior_branch(
                        distribution, index, row, positive, inputs.max_atoms)
                    if mass == 0:
                        continue
                    next_arch = tuple(
                        _Candidate(c.key, c.parent, c.profile,
                                   c.history + (Observation(op.action_id, positive),))
                        if i == index else c for i, c in enumerate(arch)
                    )
                    future += mass * solve(
                        next_arch, updated, next_used, next_budget, depth-1
                    )[0]
            else:
                index = (next(i for i, c in enumerate(arch)
                              if c.key == op.target)
                         if op.kind == "repair" else None)
                target = arch[index] if index is not None else None
                fkey = (op.action_id, op.kind,
                        target.profile if target else None,
                        target.history if target else ())
                if fkey not in forecasts:
                    raise ValueError("missing target-conditioned correlated producer")
                row = forecasts[fkey]
                failure, success = _producer_branches(
                    distribution, index, row, inputs.max_atoms)
                if failure[0]:
                    future += failure[0] * solve(
                        arch, failure[1], next_used, next_budget, depth-1
                    )[0]
                if success[0]:
                    key = SymbolicCandidateKey(
                        op.action_id, 0, target.key if target else None)
                    next_arch = arch + (_Candidate(
                        key, target.key if target else None, row.child_profile),)
                    future += success[0] * solve(
                        next_arch, success[1], next_used, next_budget, depth-1
                    )[0]
            score = future - op.cost.total_price(inputs.prices)
            if (score > best + 1e-12 or
                (abs(score-best) <= 1e-12 and choice is not None
                 and op.sort_key < choice.sort_key)):
                best, choice = score, op
        return best, choice

    stop, target = stopping(archive, atoms)
    value, op = solve(
        archive, atoms, frozenset(session.state.attempted),
        session.state.remaining, inputs.horizon
    )
    if op is None:
        kind = "release" if target is not None else "abstain"
        decision = SharedDecision(kind, kind, target, ResourceVector())
    else:
        decision = op.as_decision()
    return CorrelatedPlan(decision, value, stop, root_marginals, expansions[0])


def record_correlated_archive(
    session: SharedSession, actions: Sequence[SearchAction],
    inputs: FrozenCorrelatedInputs, decision: SharedDecision, *,
    reported_cost: ResourceVector,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
) -> SharedSession:
    if decision != plan_correlated_archive(session, actions, inputs).decision:
        raise ValueError("unselected correlated-archive decision")
    return commit_shared(
        session, actions, decision, reported_cost=reported_cost,
        observed_positive=observed_positive,
        new_candidate_sha256=new_candidate_sha256,
    )
