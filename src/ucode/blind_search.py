"""Uncertainty-blind, deterministic coding-agent action controller.

A matched-budget negative control: it can GENERATE, REPAIR, TEST, retrieve
context or request static analysis, and can release/abstain. Unlike BES it
cannot consume predicted patch quality, diagnostic sensitivity/specificity,
Bayesian likelihoods, or evaluator-only functional correctness outcomes.

Its schedule is frozen before running a task. This is a reproducible
FIXED-SCHEDULE baseline, *not* a faithful implementation of published MCTS,
RETRACE, or the strongest possible uncertainty-free search algorithm.
No third-party code, model or hidden correctness oracle is run here.
"""
from dataclasses import dataclass
from math import isfinite
import re
from typing import Sequence

from .vector_policy import DIAGNOSTICS, GENERATORS, ResourceVector

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class BlindAction:
    action_id: str
    kind: str
    cost: ResourceVector
    priority: int

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("action ID must be a nonblank string")
        if self.action_id in ("release", "abstain"):
            raise ValueError("terminal names reserved")
        if self.kind not in DIAGNOSTICS | GENERATORS:
            raise ValueError("unknown action category")
        if not isinstance(self.cost, ResourceVector) or self.cost.is_free():
            raise ValueError("action must have nonzero five-component cost")
        if type(self.priority) is not int or self.priority < 0:
            raise ValueError("priority must be predetermined nonnegative integer")


@dataclass(frozen=True)
class VisibleObservation:
    action_id: str
    candidate_sha256: str
    positive: bool

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id:
            raise ValueError("diagnostic ID required")
        if not isinstance(self.candidate_sha256, str) or not _SHA256.fullmatch(
                self.candidate_sha256):
            raise ValueError("observation must bind a candidate SHA256")
        if type(self.positive) is not bool:
            raise ValueError("visible diagnostic result must be boolean")


@dataclass(frozen=True)
class BlindState:
    """Policy-visible data only; no latent/estimated success probability."""
    remaining: ResourceVector
    candidate_sha256: str | None = None
    attempted: tuple[str, ...] = ()
    observations: tuple[VisibleObservation, ...] = ()

    def __post_init__(self):
        if not isinstance(self.remaining, ResourceVector):
            raise ValueError("remaining five-vector budget required")
        if self.candidate_sha256 is not None and (
                not isinstance(self.candidate_sha256, str)
                or not _SHA256.fullmatch(self.candidate_sha256)):
            raise ValueError("candidate patch must be SHA256 fingerprint")
        if not isinstance(self.attempted, tuple):
            raise ValueError("attempted actions must be frozen tuple")
        if len(set(self.attempted)) != len(self.attempted) or any(
                not isinstance(s, str) or not s for s in self.attempted):
            raise ValueError("attempted action IDs must be unique and nonblank")
        if not isinstance(self.observations, tuple):
            raise ValueError("visible diagnostics must be frozen tuple")
        if len({o.action_id for o in self.observations}) != len(self.observations):
            raise ValueError("duplicate diagnostic observation")
        for o in self.observations:
            if not isinstance(o, VisibleObservation) or o.action_id not in self.attempted:
                raise ValueError("observation must refer to prior action")
            if self.candidate_sha256 is None or o.candidate_sha256 != self.candidate_sha256:
                raise ValueError("stale or unbound candidate diagnostic not allowed")


@dataclass(frozen=True)
class BlindPolicy:
    """Predeclared fixed schedule with conservative visible-evidence release gate."""
    min_positive_tests: int = 1

    def __post_init__(self):
        if type(self.min_positive_tests) is not int or self.min_positive_tests < 1:
            raise ValueError("positive test count must be predetermined positive integer")


@dataclass(frozen=True)
class BlindDecision:
    action: str
    kind: str
    budget_after_first: ResourceVector
    justification: str

    @property
    def terminal(self) -> bool:
        return self.kind in ("release", "abstain")


def _catalog(actions: Sequence[BlindAction]) -> tuple[BlindAction, ...]:
    actions = tuple(actions)
    if len(actions) > 32:
        raise ValueError("bounded scheduling allows at most 32 actions")
    if any(not isinstance(a, BlindAction) for a in actions):
        raise ValueError("typed blind actions required")
    ids = [a.action_id for a in actions]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate action identity")
    return actions


def choose_blind(
    state: BlindState,
    actions: Sequence[BlindAction],
    policy: BlindPolicy = BlindPolicy(),
) -> BlindDecision:
    """Deterministic visible-feedback controller with hard resource ceilings.

    Policy:
    - no candidate: lowest-priority affordable GENERATE;
    - negative diagnostic: lowest-priority affordable REPAIR, else abstain;
    - enough positive TESTS on current candidate: release;
    - otherwise: lowest-priority affordable next TEST, STATIC_ANALYSIS,
      RETRIEVE (fixed priority schedule); if none, abstain.
    The action selection uses NO posterior or forecast fields. A positive
    retrieve/static-analysis observation does not itself justify release.
    """
    if not isinstance(state, BlindState) or not isinstance(policy, BlindPolicy):
        raise TypeError("typed state and frozen blind policy required")
    catalog = _catalog(actions)
    attempted = set(state.attempted)
    unused = sorted((a for a in catalog if a.action_id not in attempted
                     and state.remaining.affordable(a.cost)),
                    key=lambda a: (a.priority, a.action_id))
    def decision(a):
        return BlindDecision(
            a.action_id, a.kind, state.remaining.subtract(a.cost),
            "frozen cost-feasible schedule; no predictive uncertainty input",
        )
    def stop(kind, reason):
        return BlindDecision(kind, kind, state.remaining, reason)
    if state.candidate_sha256 is None:
        return next((decision(a) for a in unused if a.kind=="generate"),
                    stop("abstain", "no affordable candidate generation"))
    if any(not x.positive for x in state.observations):
        return next((decision(a) for a in unused if a.kind=="repair"),
                    stop("abstain", "negative visible diagnostic with no repair"))
    passed = sum(a.kind=="test" for a in catalog
                 for o in state.observations
                 if o.action_id==a.action_id and o.positive)
    if passed >= policy.min_positive_tests:
        return stop("release", "fixed count of positive visible tests; not correctness proof")
    # Generate/repair are never selected without negative evidence once
    # candidate exists. This schedule is not an adaptive value-of-search policy.
    return next((decision(a) for a in unused if a.kind in DIAGNOSTICS),
                stop("abstain", "insufficient visible test evidence within budget"))


def record_blind(
    state: BlindState,
    actions: Sequence[BlindAction],
    decision: BlindDecision,
    *,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
    policy: BlindPolicy = BlindPolicy(),
) -> BlindState:
    """Record one visible action. Terminals are not actions to record.

    Enforce the frozen decision so post-hoc users cannot insert a favorable
    gold label or cheaper tool cost in the visible trace.
    """
    catalog = _catalog(actions)
    expected = choose_blind(state, catalog, policy)
    if decision != expected or decision.terminal:
        raise ValueError("unselected, terminal or altered action cannot be recorded")
    action = next(a for a in catalog if a.action_id==decision.action)
    if action.kind in DIAGNOSTICS:
        if type(observed_positive) is not bool or new_candidate_sha256 is not None:
            raise ValueError("diagnostic requires ONLY a visible boolean result")
        if state.candidate_sha256 is None:
            raise ValueError("cannot diagnose absent patch")
        candidate = state.candidate_sha256
        observations = state.observations + (
            VisibleObservation(action.action_id, candidate, observed_positive),)
    else:
        if observed_positive is not None:
            raise ValueError("generation/repair cannot carry hidden oracle result")
        if not isinstance(new_candidate_sha256, str) or not _SHA256.fullmatch(
                new_candidate_sha256):
            raise ValueError("new code artifact must have SHA256 digest")
        if action.kind=="repair" and new_candidate_sha256==state.candidate_sha256:
            raise ValueError("repair must produce a changed candidate artifact")
        candidate = new_candidate_sha256
        # Diagnostics about an older patch must NEVER apply to a new patch.
        observations = ()
    return BlindState(decision.budget_after_first, candidate,
                      state.attempted+(action.action_id,), observations)


def blind_catalog_from_public_manifest(
    payload: list[dict],
) -> tuple[BlindAction, ...]:
    """Parse allowlisted schedule only; reject oracle/forecast fields.

    Do not feed this a full tool trace. The manifest explicitly excludes
    any forecast confidence, oracle label, solution hash, or test answer.
    """
    allowed = {"action_id", "kind", "priority", "cost"}
    if not isinstance(payload, list):
        raise ValueError("action catalog must be a list")
    parsed = []
    for item in payload:
        if not isinstance(item, dict) or set(item) != allowed:
            raise ValueError("unknown/absent action fields or potential oracle leak")
        costs = item["cost"]
        keys = {"tokens", "test_calls", "gpu_seconds",
                "cpu_seconds", "wall_seconds"}
        if not isinstance(costs, dict) or set(costs) != keys:
            raise ValueError("all five resource components required")
        parsed.append(BlindAction(item["action_id"],item["kind"],
                                  ResourceVector(**costs),item["priority"]))
    return _catalog(parsed)
