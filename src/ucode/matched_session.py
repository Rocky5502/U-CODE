"""Shared *offline* action and candidate archive for matched-policy references.

Both uncertainty-free beam search and conditional evidence planning use this
exact typed candidate/diagnostic action ledger. These calls never execute a
repository, an LLM, or any evaluator oracle. Reported resource use is not
trusted hardware telemetry: a separate attested sandbox must enforce it.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Sequence

from .optimized_search import (
    SearchAction, SearchCandidate, SearchObservation, SearchPolicy, SearchState,
    choose_search,
)
from .vector_policy import DIAGNOSTICS, GENERATORS, RESOURCE_FIELDS, ResourceVector


@dataclass(frozen=True)
class SharedReceipt:
    action_id: str
    kind: str
    target_sha256: str | None
    resulting_sha256: str | None
    visible_positive: bool | None
    reserved_cost: ResourceVector
    reported_cost: ResourceVector

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id:
            raise ValueError("receipt action identity required")
        if self.kind not in DIAGNOSTICS | GENERATORS:
            raise ValueError("receipt action kind invalid")
        if not isinstance(self.reserved_cost, ResourceVector) or (
            not isinstance(self.reported_cost, ResourceVector)
        ):
            raise ValueError("receipt requires five-vector resource costs")
        if self.reserved_cost.is_free():
            raise ValueError("reservation cannot be free")
        if self.reported_cost.is_free():
            raise ValueError("purchased tool needs nonzero reported consumption")
        for candidate_sha in (self.target_sha256, self.resulting_sha256):
            if candidate_sha is not None and (
                not isinstance(candidate_sha, str) or len(candidate_sha) != 64
                or any(ch not in "0123456789abcdef" for ch in candidate_sha)):
                raise ValueError("receipt candidate identity must be SHA256")
        if self.kind in DIAGNOSTICS | {"repair"} and self.target_sha256 is None:
            raise ValueError("diagnostic or repair receipt needs target candidate")
        if self.kind in DIAGNOSTICS:
            if type(self.visible_positive) is not bool or self.resulting_sha256 is not None:
                raise ValueError("diagnostic receipt requires visible boolean only")
        elif self.visible_positive is not None:
            raise ValueError("candidate action cannot import evaluator outcome")


@dataclass(frozen=True)
class SharedSession:
    """Policy-neutral patch archive; no prior or gold label in public state."""
    initial_budget: ResourceVector
    state: SearchState
    receipts: tuple[SharedReceipt, ...] = ()
    max_candidates: int = 8

    def __post_init__(self):
        if not isinstance(self.initial_budget, ResourceVector) or not isinstance(
                self.state, SearchState):
            raise ValueError("shared session requires typed budget and archive")
        if type(self.max_candidates) is not int or not 1 <= self.max_candidates <= 32:
            raise ValueError("shared candidate cap must be 1..32")
        if not isinstance(self.receipts, tuple) or any(
                not isinstance(r, SharedReceipt) for r in self.receipts):
            raise ValueError("immutable typed receipts required")
        if len(self.state.candidates) > self.max_candidates:
            raise ValueError("archive exceeds shared candidate cap")
        if tuple(r.action_id for r in self.receipts) != self.state.attempted:
            raise ValueError("receipt/action chronology mismatch")
        sums = {f: sum(getattr(r.reported_cost, f) for r in self.receipts)
                for f in RESOURCE_FIELDS}
        if any(abs(getattr(self.initial_budget, f) - sums[f]
                   - getattr(self.state.remaining, f)) > 1e-7
               for f in RESOURCE_FIELDS):
            raise ValueError("reported five-resource ledger does not reconcile")
        ids = {r.action_id: r for r in self.receipts}
        for r in self.receipts:
            if r.resulting_sha256 is not None and not any(
                    c.sha256 == r.resulting_sha256 for c in self.state.candidates):
                raise ValueError("receipt declares missing generated candidate")
        for c in self.state.candidates:
            if c.created_by != "initial":
                r = ids[c.created_by]
                if r.kind not in GENERATORS or r.resulting_sha256 != c.sha256:
                    raise ValueError("candidate must match generating receipt SHA")
                if r.kind == "repair" and r.target_sha256 != c.parent_sha256:
                    raise ValueError("repair receipt parent mismatch")
                if r.kind == "generate" and c.parent_sha256 is not None:
                    raise ValueError("generated candidate cannot claim repair parent")
        for o in self.state.observations:
            r = ids[o.action_id]
            if (r.kind != o.kind or r.target_sha256 != o.candidate_sha256
                    or r.visible_positive is not o.positive):
                raise ValueError("diagnostic observation does not match receipt")

    @classmethod
    def empty(cls, budget: ResourceVector, max_candidates: int = 8):
        return cls(budget, SearchState(budget), (), max_candidates)

    @property
    def reported_consumption(self):
        return ResourceVector(**{
            f: getattr(self.initial_budget, f) - getattr(self.state.remaining, f)
            for f in RESOURCE_FIELDS
        })

    @property
    def trace_sha256(self):
        """Deterministic visible-only digest; no oracle fields."""
        rows = []
        for r in self.receipts:
            rows.append({
                "action_id": r.action_id, "kind": r.kind,
                "target_sha256": r.target_sha256,
                "resulting_sha256": r.resulting_sha256,
                "visible_positive": r.visible_positive,
                "reserved_cost": {k: getattr(r.reserved_cost, k) for k in RESOURCE_FIELDS},
                "reported_cost": {k: getattr(r.reported_cost, k) for k in RESOURCE_FIELDS},
            })
        obj = {"initial_budget": {k: getattr(self.initial_budget, k)
                                  for k in RESOURCE_FIELDS}, "actions": rows}
        return sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()


@dataclass(frozen=True)
class SharedDecision:
    action_id: str
    kind: str
    target_sha256: str | None
    reserved_cost: ResourceVector

    @property
    def terminal(self):
        return self.kind in ("release", "abstain")


def _common_catalog(actions: Sequence[SearchAction]) -> tuple[SearchAction, ...]:
    items = tuple(actions)
    if len(items) > 10 or any(not isinstance(a, SearchAction) for a in items):
        raise ValueError("shared model supports at most ten typed actions")
    if len(set(a.action_id for a in items)) != len(items):
        raise ValueError("duplicate action IDs")
    return tuple(sorted(items, key=lambda a: a.action_id))


def baseline_shared_decision(session: SharedSession,
                             actions: Sequence[SearchAction],
                             policy: SearchPolicy) -> SharedDecision:
    """Use target-aware public matched search on the shared archive.

    The lazy import avoids a module cycle: the common opportunity expander
    also depends on this policy-neutral execution ledger. The legacy
    optimized_search.choose_search remains independently available.
    """
    from .matched_opportunities import choose_matched_baseline
    return choose_matched_baseline(session, actions, policy)


def commit_shared(
    session: SharedSession,
    actions: Sequence[SearchAction],
    decision: SharedDecision,
    *,
    reported_cost: ResourceVector,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
) -> SharedSession:
    """Append a policy-selected visible action and charge reported consumption.

    The chosen action must exist in a frozen catalog, remain unused, and
    have an affordable *reservation* before execution. Externally reported
    actual cost may exceed the nominal reservation, but must still fit every
    remaining hard cap. This function does not prove such reports are honest.
    The upstream policy adapter must validate decision selection separately.
    """
    if not isinstance(session, SharedSession) or not isinstance(decision, SharedDecision):
        raise TypeError("typed shared session and decision required")
    catalog = _common_catalog(actions)
    index = {a.action_id: a for a in catalog}
    if decision.terminal or decision.action_id not in index:
        raise ValueError("terminal or unknown action cannot be committed")
    action = index[decision.action_id]
    if decision.kind != action.kind or decision.reserved_cost != action.cost:
        raise ValueError("action identity/kind/reservation mismatch")
    if action.action_id in session.state.attempted:
        raise ValueError("single-use action replay")
    if not isinstance(reported_cost, ResourceVector):
        raise ValueError("typed reported consumption required")
    if not session.state.remaining.affordable(action.cost):
        raise ValueError("reserved action exceeds remaining hard cap")
    if not session.state.remaining.affordable(reported_cost):
        raise ValueError("reported consumption exceeds remaining hard cap")
    st = session.state
    target = decision.target_sha256
    known = {c.sha256 for c in st.candidates}
    if action.kind == "generate" and target is not None and target not in known:
        raise ValueError("generation context must reference archived candidate")
    if action.kind in DIAGNOSTICS | {"repair"} and target not in known:
        raise ValueError("diagnostic/repair needs selected archived candidate")
    archive, evidence, active = st.candidates, st.observations, st.active_sha256
    if action.kind in DIAGNOSTICS:
        if type(observed_positive) is not bool or new_candidate_sha256 is not None:
            raise ValueError("only visible boolean diagnostic permitted")
        evidence += (SearchObservation(action.action_id, target, action.kind,
                                       observed_positive),)
        active = target
    else:
        if observed_positive is not None:
            raise ValueError("candidate producer cannot import oracle verdict")
        if new_candidate_sha256 is not None:
            # SearchCandidate validates fingerprint; failed production is None.
            if new_candidate_sha256 in known:
                raise ValueError("duplicate or replayed candidate SHA")
            if len(archive) >= session.max_candidates:
                raise ValueError("archive capacity exceeded")
            archive += (SearchCandidate(
                new_candidate_sha256, action.action_id,
                target if action.kind == "repair" else None,
            ),)
            active = new_candidate_sha256
    receipt = SharedReceipt(action.action_id, action.kind, target,
                            new_candidate_sha256, observed_positive,
                            action.cost, reported_cost)
    next_state = SearchState(
        st.remaining.subtract(reported_cost), archive, active,
        st.attempted + (action.action_id,), evidence,
    )
    return SharedSession(session.initial_budget, next_state,
                         session.receipts + (receipt,), session.max_candidates)


def record_baseline_shared(session: SharedSession,
                           actions: Sequence[SearchAction],
                           policy: SearchPolicy,
                           decision: SharedDecision,
                           *, reported_cost: ResourceVector,
                           observed_positive: bool | None = None,
                           new_candidate_sha256: str | None = None) -> SharedSession:
    """Reject manually forged/off-policy search steps."""
    if decision != baseline_shared_decision(session, actions, policy):
        raise ValueError("unselected baseline decision")
    return commit_shared(session, actions, decision,
                         reported_cost=reported_cost,
                         observed_positive=observed_positive,
                         new_candidate_sha256=new_candidate_sha256)



@dataclass(frozen=True)
class MatchedSessionStart:
    """Necessary initial opportunity equality; no actual execution attestation."""
    action_opportunity_sha256: str
    action_count: int
    max_candidates: int
    initial_budget: ResourceVector
    scope: str = "MATCHED_OFFLINE_START_ONLY_NO_MODEL_OR_SANDBOX_PROOF"


def audit_shared_start(
    treatment: SharedSession,
    baseline: SharedSession,
    treatment_actions: Sequence[SearchAction],
    baseline_actions: Sequence[SearchAction],
) -> MatchedSessionStart:
    """Fail before any step if comparator starts with different opportunities.

    Checks candidate identity/parent/creation, exact action types/nominal
    vectors, initial five-dimensional caps, and shared archive capacity.
    It does NOT establish matching future sampling draws, prompts, training,
    measured resource enforcement, sealed oracles, or external code rights.
    """
    if not isinstance(treatment, SharedSession) or not isinstance(
            baseline, SharedSession):
        raise ValueError("two typed sessions required")
    if (treatment.initial_budget != baseline.initial_budget or
            treatment.state.remaining != baseline.state.remaining):
        raise ValueError("different initial five-resource budgets")
    if treatment.max_candidates != baseline.max_candidates:
        raise ValueError("different candidate archive capacity")
    if (treatment.receipts or baseline.receipts or
            treatment.state.attempted or baseline.state.attempted or
            treatment.state.observations or baseline.state.observations):
        raise ValueError("fair-start audit must precede policy execution")
    if (treatment.state.candidates != baseline.state.candidates or
            treatment.state.active_sha256 != baseline.state.active_sha256):
        raise ValueError("different initial candidate archive or active candidate")
    a, b = _common_catalog(treatment_actions), _common_catalog(baseline_actions)
    ta = tuple((x.action_id, x.kind, x.cost) for x in a)
    tb = tuple((x.action_id, x.kind, x.cost) for x in b)
    if ta != tb:
        raise ValueError("different action IDs, kinds, or five-dimensional costs")
    immutable = {
        "actions": [{"action_id": x.action_id, "kind": x.kind,
                     "cost": {k: getattr(x.cost, k) for k in RESOURCE_FIELDS}} for x in a],
        "initial_budget": {k: getattr(treatment.initial_budget, k)
                           for k in RESOURCE_FIELDS},
        "max_candidates": treatment.max_candidates,
        "candidate_archive": [
            {"sha256": c.sha256, "created_by": c.created_by,
             "parent_sha256": c.parent_sha256}
            for c in treatment.state.candidates
        ],
        "active_sha256": treatment.state.active_sha256,
    }
    digest = sha256(json.dumps(immutable,sort_keys=True,
                               separators=(",",":")).encode()).hexdigest()
    return MatchedSessionStart(digest,len(a),treatment.max_candidates,
                               treatment.initial_budget)
