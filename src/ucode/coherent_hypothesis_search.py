"""Coherent hypothesis-aware evidence search: finite synthetic Bayes reference.

Scientific problem: an evidence channel's calibration may itself be unknown.
A one-step scenario-wise value audit treats each candidate kernel as if its
identity were known during downstream release decisions. That is unsuitable
when a single, persistent UNKNOWN kernel generates the visible observations.

This algorithm maintains P(kernel identity, patch acceptable | observed data)
and makes terminal decisions with a frozen all-surviving-model risk gate or
a mixture-only gate. The kernel identity remains latent; it is never passed
from a hidden evaluator or directly observed by the runtime policy.

No LLM, external repository, execution, actual confidence set, statistical
guarantee, or physical five-resource meter. This is a bounded ONE-CANDIDATE,
DIAGNOSTICS-ONLY research reference, not a complete U-CODE coding agent.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from math import isfinite
import re
from typing import Sequence

from .conditional_bes import (
    ConditionalKernel, ConditionalProbe, Observation,
)
from .vector_policy import ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value

_TOL = 1e-9
_MAX_HYPOTHESES = 8
_MAX_PROBES = 6
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def kernel_fingerprint(kernel: ConditionalKernel) -> str:
    """Canonical fingerprint of ALL frozen likelihood rows.

    Includes each action, ordered visible history and both likelihoods.
    Row-list permutations do not change the SHA256 digest. Fingerprints
    bind trusted *in-process inputs*; they are NOT source attestations
    or evidence of calibrated probabilities.
    """
    if not isinstance(kernel, ConditionalKernel):
        raise TypeError("typed frozen conditional kernel required")
    rows = []
    for r in kernel.rows:
        rows.append([
            r.action_id,
            [[o.action_id, o.positive] for o in r.history],
            float(r.positive_if_acceptable).hex(),
            float(r.positive_if_unacceptable).hex(),
        ])
    packed = json.dumps(
        ["ucode-mcea-kernel-v1", sorted(
            rows, key=lambda x: json.dumps(x, separators=(",", ":"),
                                          ensure_ascii=False))],
        ensure_ascii=False, separators=(",", ":"),
    )
    return sha256(packed.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceHypothesis:
    """One prospectively frozen model of diagnostic observations."""

    scenario_id: str
    kernel: ConditionalKernel

    def __post_init__(self):
        if (type(self.scenario_id) is not str
                or not self.scenario_id.strip()
                or len(self.scenario_id) > 128):
            raise ValueError("bounded nonempty evidence hypothesis ID required")
        if not isinstance(self.kernel, ConditionalKernel):
            raise TypeError("typed frozen conditional kernel required")


@dataclass(frozen=True)
class CoherentBeliefState:
    """Policy-visible joint model/acceptability beliefs, not an oracle label.

    For each frozen scenario the pair is (P(theta,Y=0|h),
    P(theta,Y=1|h)). Scenario posterior weights are their sums.
    All values are frozen pre-outcome predictions, never gold truth.
    """

    scenario_ids: tuple[str, ...]
    joint: tuple[tuple[float, float], ...]
    budget: ResourceVector
    history: tuple[Observation, ...] = ()
    kernel_fingerprints: tuple[str, ...] = ()

    def __post_init__(self):
        if (type(self.scenario_ids) is not tuple
                or not 1 <= len(self.scenario_ids) <= _MAX_HYPOTHESES
                or any(type(x) is not str or not x.strip()
                       for x in self.scenario_ids)
                or len(set(self.scenario_ids)) != len(self.scenario_ids)):
            raise ValueError("1..8 distinct scenario identities required")
        if (type(self.joint) is not tuple
                or len(self.joint) != len(self.scenario_ids)):
            raise ValueError("one typed joint-mass pair per scenario required")
        for item in self.joint:
            if (type(item) is not tuple or len(item) != 2
                    or any(type(v) not in (int, float) or not isfinite(v)
                           or not 0 <= v <= 1 for v in item)):
                raise ValueError("joint probabilities must be valid finite mass pairs")
        if abs(sum(sum(item) for item in self.joint) - 1) > _TOL:
            raise ValueError("joint model-truth mass must sum to one")
        if not isinstance(self.budget, ResourceVector):
            raise TypeError("typed remaining five-resource vector required")
        if (type(self.kernel_fingerprints) is not tuple
                or len(self.kernel_fingerprints) != len(self.scenario_ids)
                or any(type(d) is not str or not _DIGEST.fullmatch(d)
                       for d in self.kernel_fingerprints)):
            raise ValueError("frozen kernel fingerprint required for each scenario")
        if (type(self.history) is not tuple
                or any(not isinstance(h, Observation) for h in self.history)
                or len({h.action_id for h in self.history}) != len(self.history)):
            raise ValueError("chronological unique visible observations required")

    @property
    def probability_acceptable(self) -> float:
        return sum(item[1] for item in self.joint)

    @property
    def scenario_weights(self) -> tuple[float, ...]:
        return tuple(sum(item) for item in self.joint)


@dataclass(frozen=True)
class CoherentEvidencePlan:
    action: str
    expected_proxy_utility: float
    stop_utility: float
    predicted_failure_probability: float
    scenario_posterior_weights: tuple[tuple[str, float], ...]
    budget_after_first: ResourceVector
    expanded_states: int
    release_gate: str
    interpretation: str = "FINITE_SYNTHETIC_HYPOTHESIS_BAYES_NOT_CALIBRATED"
    real_task_results: int = 0


def initial_coherent_state(
    prior_acceptable: float,
    hypotheses: Sequence[EvidenceHypothesis],
    prior_weights: Sequence[float],
    budget: ResourceVector,
) -> CoherentBeliefState:
    """Freeze P(theta,Y) = P(theta)*P(Y) as the initial independent prior.

    Independence of initial model identity and correctness is an explicit
    RESTRICTION. Real model/patch correlation would need a separately
    preregistered joint prior, which this constructor does not estimate.
    """
    if (type(prior_acceptable) not in (int, float)
            or not isfinite(prior_acceptable)
            or not 0 <= prior_acceptable <= 1):
        raise ValueError("finite pre-outcome acceptable prior required")
    models = tuple(hypotheses)
    weights = tuple(prior_weights)
    if (not 1 <= len(models) <= _MAX_HYPOTHESES
            or any(not isinstance(h, EvidenceHypothesis) for h in models)
            or len(weights) != len(models)
            or len({h.scenario_id for h in models}) != len(models)):
        raise ValueError("nonempty distinct frozen hypotheses and aligned weights required")
    if any(type(w) not in (int, float) or not isfinite(w) or w <= 0
           for w in weights) or abs(sum(weights)-1) > _TOL:
        raise ValueError("strictly positive normalized scenario prior weights required")
    return CoherentBeliefState(
        tuple(h.scenario_id for h in models),
        tuple(((1-prior_acceptable)*w, prior_acceptable*w) for w in weights),
        budget,
        kernel_fingerprints=tuple(kernel_fingerprint(h.kernel) for h in models),
    )


def _aligned_models(
    state: CoherentBeliefState,
    hypotheses: Sequence[EvidenceHypothesis],
) -> tuple[ConditionalKernel, ...]:
    frozen = tuple(hypotheses)
    if (len(frozen) != len(state.scenario_ids)
            or any(not isinstance(h, EvidenceHypothesis) for h in frozen)):
        raise ValueError("complete typed frozen hypothesis ensemble required")
    lookup = {h.scenario_id: h.kernel for h in frozen}
    if len(lookup) != len(frozen) or set(lookup) != set(state.scenario_ids):
        raise ValueError("scenario identities must match frozen belief state exactly")
    aligned = tuple(lookup[x] for x in state.scenario_ids)
    if tuple(kernel_fingerprint(k) for k in aligned) != state.kernel_fingerprints:
        raise ValueError(
            "frozen kernel fingerprint drift after model-truth belief was constructed"
        )
    return aligned


def _joint_observation(
    joint: tuple[tuple[float, float], ...],
    action_id: str,
    history: tuple[Observation, ...],
    kernels: tuple[ConditionalKernel, ...],
    positive: bool,
) -> tuple[float, tuple[tuple[float, float], ...]]:
    weighted = []
    for (bad, good), kernel in zip(joint, kernels):
        if bad + good == 0:
            weighted.append((0.0, 0.0))
            continue  # zero-posterior scenarios cannot affect reachable branches
        row = kernel.get(action_id, history)  # missing reachable row fails CLOSED
        bad_likelihood = row.positive_if_unacceptable
        good_likelihood = row.positive_if_acceptable
        if not positive:
            bad_likelihood = 1-bad_likelihood
            good_likelihood = 1-good_likelihood
        weighted.append((bad*bad_likelihood, good*good_likelihood))
    mass = sum(sum(pair) for pair in weighted)
    if not isfinite(mass):
        raise ValueError("nonfinite joint evidence probability")
    if mass <= 0:
        return 0.0, ()
    return mass, tuple((a/mass,b/mass) for a,b in weighted)


def record_coherent_observation(
    state: CoherentBeliefState,
    probe: ConditionalProbe,
    hypotheses: Sequence[EvidenceHypothesis],
    observed_positive: bool,
) -> CoherentBeliefState:
    """Consume only a public action result and its nominal five-vector cost."""
    if not isinstance(state, CoherentBeliefState):
        raise TypeError("typed policy-visible coherent state required")
    if not isinstance(probe, ConditionalProbe) or type(observed_positive) is not bool:
        raise TypeError("typed probe and binary visible result required")
    if probe.action_id in {h.action_id for h in state.history}:
        raise ValueError("globally repeated diagnostic action")
    if not state.budget.affordable(probe.cost):
        raise ValueError("diagnostic exceeds hard resource cap")
    models = _aligned_models(state, hypotheses)
    likelihood, posterior = _joint_observation(
        state.joint, probe.action_id, state.history,
        models, observed_positive,
    )
    if likelihood == 0:
        raise ValueError("observed outcome impossible under all frozen hypotheses")
    return CoherentBeliefState(
        state.scenario_ids, posterior, state.budget.subtract(probe.cost),
        state.history + (Observation(probe.action_id, observed_positive),),
        state.kernel_fingerprints,
    )


def _terminal(
    joint: tuple[tuple[float, float], ...],
    rule: ReleaseRule,
    gate: str,
) -> float:
    bad = sum(x[0] for x in joint)
    good = sum(x[1] for x in joint)
    if gate == "all_surviving_models":
        for neg, pos in joint:
            total = neg + pos
            if total > 0 and neg / total > rule.max_predicted_failure + 1e-12:
                return 0.0
    return terminal_value(good/(bad+good), rule)


def plan_coherent_evidence(
    state: CoherentBeliefState,
    probes: Sequence[ConditionalProbe],
    hypotheses: Sequence[EvidenceHypothesis],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    horizon: int = 2,
    max_states: int = 10000,
    release_gate: str = "all_surviving_models",
) -> CoherentEvidencePlan:
    """Bayes-adaptive *fixed latent-model* diagnostic choice.

    P(theta,Y|h) is propagated along EVERY visible outcome branch; the
    same latent theta persists across all steps. We optimize EXPECTED
    utility under the predeclared joint prior, NOT maximin across models.

    An optional all-surviving-model gate vetoes release if any still-
    possible model predicts failure probability above the rule's ceiling.
    This is a conservative finite-hypothesis preference, NOT risk
    coverage outside the list or a frequentist selective-risk guarantee.
    """
    if not isinstance(state, CoherentBeliefState):
        raise TypeError("typed coherent model-truth belief state required")
    if not isinstance(prices, ResourcePrices) or not isinstance(rule, ReleaseRule):
        raise TypeError("typed resource prices and terminal release rule required")
    if rule.unit_cost_penalty != 0:
        raise ValueError("five-vector cost is charged once; no duplicate scalar penalty")
    if type(horizon) is not int or not 1 <= horizon <= 4:
        raise ValueError("finite horizon must be 1..4")
    if type(max_states) is not int or not 1 <= max_states <= 100000:
        raise ValueError("state expansion cap must be 1..100000")
    if release_gate not in ("all_surviving_models","mixture_only"):
        raise ValueError("unknown prospectively frozen release gate")
    models = _aligned_models(state, hypotheses)
    proposals = tuple(probes)
    if len(proposals) > _MAX_PROBES or any(
            not isinstance(a, ConditionalProbe) for a in proposals):
        raise TypeError("at most six typed diagnostic probes allowed")
    keys = [a.action_id for a in proposals]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate diagnostic action IDs")
    # Fixed lexical ordering guarantees deterministic ties independent of
    # caller action-catalog order. Each action ID is globally single-use.
    proposals = tuple(sorted(proposals, key=lambda a:a.action_id))
    cost_by_id = {a.action_id:a.cost for a in proposals}
    price_by_id = {k:v.total_price(prices) for k,v in cost_by_id.items()}
    counter=[0]

    @lru_cache(maxsize=None)
    def solve(joint,history,budget,depth):
        counter[0]+=1
        if counter[0]>max_states:
            raise ValueError("coherent hypothesis search state cap exceeded")
        best = _terminal(joint,rule,release_gate)
        selected = None
        if depth==0:
            return best, selected
        used = {x.action_id for x in history}
        for probe in proposals:
            if probe.action_id in used or not budget.affordable(probe.cost):
                continue
            # Both conditional likelihood branches are enumerated using
            # SAME persistent latent theta; never resample per branch.
            future=0.0
            for positive in (True,False):
                mass,next_joint=_joint_observation(
                    joint,probe.action_id,history,models,positive)
                if not mass:
                    continue
                future+=mass*solve(
                    next_joint,
                    history+(Observation(probe.action_id,positive),),
                    budget.subtract(probe.cost),depth-1,
                )[0]
            score=future-price_by_id[probe.action_id]
            if score>best+1e-12:
                selected,best=probe,score
        return best,selected

    stop=_terminal(state.joint,rule,release_gate)
    value,selected=solve(state.joint,state.history,state.budget,horizon)
    action=selected.action_id if selected else ("release" if stop>0 else "abstain")
    after=state.budget.subtract(selected.cost) if selected else state.budget
    return CoherentEvidencePlan(
        action,value,stop,1-state.probability_acceptable,
        tuple(zip(state.scenario_ids,state.scenario_weights)),
        after,counter[0],release_gate,
    )
