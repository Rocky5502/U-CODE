"""Synthetic-only action-ID / candidate-provenance replay bridge.

Bridges matched_opportunities.py's unique action IDs and candidate-target
menu to a public, frozen response book and SharedSession receipts. This does
NOT use an LLM, run source code, authenticate a resource meter or evaluate a
hidden oracle. The eight named policies are NOT implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .matched_session import SharedDecision, SharedSession, commit_shared
from .matched_opportunities import matched_opportunities, opportunity_digest
from .optimized_search import SearchAction
from .vector_policy import DIAGNOSTICS, GENERATORS, RESOURCE_FIELDS, ResourceVector

_SHA = re.compile(r"^[0-9a-f]{64}$")
_STAGE = "SYNTHETIC_ACTION_BOUND_REPLAY_NOT_EXECUTED"


def _cost(v: ResourceVector) -> dict:
    return {f: getattr(v, f) for f in RESOURCE_FIELDS}


@dataclass(frozen=True)
class ActionBoundResponse:
    """One fictitious public outcome keyed by action identity AND candidate."""
    action_id: str
    kind: str
    target_sha256: str | None
    reserved: ResourceVector
    used: ResourceVector
    visible_positive: bool | None = None
    produced_sha256: str | None = None

    def __post_init__(self):
        if type(self.action_id) is not str or not self.action_id.strip():
            raise ValueError("nonblank frozen action identity required")
        if self.kind not in DIAGNOSTICS | GENERATORS:
            raise ValueError("unsupported frozen public tool action")
        if self.target_sha256 is not None and (
                type(self.target_sha256) is not str or
                not _SHA.fullmatch(self.target_sha256)):
            raise ValueError("target candidate must be canonical SHA256")
        if self.produced_sha256 is not None and (
                type(self.produced_sha256) is not str or
                not _SHA.fullmatch(self.produced_sha256)):
            raise ValueError("produced candidate must be canonical SHA256")
        if self.kind == "generate" and self.target_sha256 is not None:
            raise ValueError("generation must use target-free opportunity")
        if self.kind != "generate" and self.target_sha256 is None:
            raise ValueError("non-generation outcome needs target candidate")
        if self.kind in DIAGNOSTICS:
            if type(self.visible_positive) is not bool or self.produced_sha256 is not None:
                raise ValueError("public diagnostic requires only visible boolean")
        elif self.visible_positive is not None:
            raise ValueError("candidate-producing action cannot carry oracle verdict")
        if (not isinstance(self.reserved, ResourceVector)
                or not isinstance(self.used, ResourceVector)
                or self.reserved.is_free() or self.used.is_free()
                or not self.reserved.affordable(self.used)):
            raise ValueError("reported five-vector must be positive and within reservation")

    @property
    def key(self):
        return (self.action_id, self.target_sha256)


@dataclass(frozen=True)
class ActionBoundBook:
    """Frozen synthetic action catalogue and policy-neutral public receipts."""
    catalog: tuple[SearchAction, ...]
    responses: tuple[ActionBoundResponse, ...]
    stage: str = _STAGE

    def __post_init__(self):
        if self.stage != _STAGE:
            raise ValueError("replay book cannot promote execution status")
        if (type(self.catalog) is not tuple or
                not 1 <= len(self.catalog) <= 10 or
                any(not isinstance(a, SearchAction) for a in self.catalog)):
            raise ValueError("bounded typed action catalog required")
        ids = [a.action_id for a in self.catalog]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate frozen action IDs")
        if (type(self.responses) is not tuple or
                not 1 <= len(self.responses) <= 128 or
                any(not isinstance(x, ActionBoundResponse) for x in self.responses)):
            raise ValueError("bounded typed public responses required")
        if len({r.key for r in self.responses}) != len(self.responses):
            raise ValueError("duplicate action ID and target response key")
        actions = {a.action_id: a for a in self.catalog}
        for response in self.responses:
            action = actions.get(response.action_id)
            if (action is None or action.kind != response.kind
                    or action.cost != response.reserved):
                raise ValueError("response action identity/kind/reservation not in catalog")

    @property
    def digest_sha256(self) -> str:
        data = {
            "stage": self.stage,
            "catalog": [{
                "id": a.action_id, "kind": a.kind, "cost": _cost(a.cost),
            } for a in sorted(self.catalog, key=lambda x: x.action_id)],
            "responses": [{
                "id": r.action_id, "kind": r.kind, "target": r.target_sha256,
                "reserved": _cost(r.reserved), "used": _cost(r.used),
                "visible_positive": r.visible_positive,
                "produced": r.produced_sha256,
            } for r in sorted(self.responses,
                             key=lambda x:(x.action_id,x.target_sha256 or ""))],
        }
        return sha256(json.dumps(data, sort_keys=True,
                                separators=(",",":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BoundReplayResult:
    status: str
    session: SharedSession
    response_book_sha256: str
    initial_opportunity_sha256: str
    chosen_action_ids: tuple[str, ...]
    released_candidate_sha256: str | None
    independent_correctness_labels: int = 0
    authenticated_model_calls: int = 0
    trusted_meter_attested: bool = False


def replay_bound_synthetic_actions(
    task_id: str,
    initial_budget: ResourceVector,
    book: ActionBoundBook,
    decisions: tuple[SharedDecision, ...],
    *,
    max_candidates: int = 8,
) -> BoundReplayResult:
    """Reproduce already chosen public actions, no policy or external callbacks.

    An action must be one of the currently affordable unique action/target
    opportunities. Missing frozen responses stop without inventing outcomes;
    attempts to reuse an action against another candidate are rejected.
    """
    if type(task_id) is not str or not task_id.startswith("SYNTHETIC_"):
        raise ValueError("real/unqualified task IDs cannot use synthetic replay")
    if not isinstance(initial_budget, ResourceVector) or initial_budget.is_free():
        raise ValueError("typed nonzero five-resource budget required")
    if not isinstance(book, ActionBoundBook):
        raise TypeError("typed frozen public response book required")
    if type(decisions) is not tuple or not 1 <= len(decisions) <= 32:
        raise ValueError("bounded immutable decision tuple required")
    if any(not isinstance(d, SharedDecision) for d in decisions):
        raise TypeError("only typed preselected decisions permitted")
    if any(d.terminal for d in decisions[:-1]):
        raise ValueError("release/abstain terminal must be last")

    session = SharedSession.empty(initial_budget, max_candidates=max_candidates)
    initial_opportunity = opportunity_digest(session, book.catalog)
    frozen = {x.key: x for x in book.responses}
    chosen = []

    def result(status: str, released=None):
        return BoundReplayResult(status, session, book.digest_sha256,
                                 initial_opportunity, tuple(chosen), released)

    for d in decisions:
        if d.terminal:
            if (d.reserved_cost != ResourceVector() or
                    d.action_id != d.kind or
                    d.kind not in ("release","abstain")):
                return result("INVALID_TERMINAL_ACTION")
            if d.kind == "abstain":
                if d.target_sha256 is not None:
                    return result("INVALID_TERMINAL_ACTION")
                return result("ABSTAINED")
            if d.target_sha256 not in {c.sha256 for c in session.state.candidates}:
                return result("INVALID_RELEASE_CANDIDATE")
            return result("RELEASED_PENDING_INDEPENDENT_EVALUATION",
                          d.target_sha256)
        # Matching menu uses both unique action ID and target SHA as well as
        # the same five-dimensional reservation; symbolic targets never enter.
        if d not in tuple(o.as_decision()
                          for o in matched_opportunities(session, book.catalog)):
            return result("INVALID_OR_UNAVAILABLE_ACTION_TARGET")
        response = frozen.get((d.action_id,d.target_sha256))
        if response is None:
            return result("FROZEN_PUBLIC_RESPONSE_MISSING")
        if response.kind != d.kind or response.reserved != d.reserved_cost:
            return result("FROZEN_PUBLIC_RESPONSE_IDENTITY_MISMATCH")
        session = commit_shared(
            session, book.catalog, d,
            reported_cost=response.used,
            observed_positive=response.visible_positive,
            new_candidate_sha256=response.produced_sha256,
        )
        chosen.append(d.action_id)
    return result("TRACE_INCOMPLETE_NO_TERMINAL")
