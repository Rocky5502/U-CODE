"""Policy-neutral frozen PUBLIC outcome book for synthetic U-CODE replay.

Deliberately OFFLINE and SYNTHETIC: no external repository, LLM, test runner,
network, hidden oracle or trusted meter. Outcomes are synthetic fixtures,
not real tool measurements. The same book is reused across all eight arms
of one task/model/seed/budget pair; per-policy responses are NOT sampled.

The only supported integration is with the synthetic-only shadow runner.
Do NOT use this as a real-task evaluator or real candidate generator.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Mapping

from .blind_policy_trace import BlindAction, PublicStep, PublicToolReceipt
from .experiment_contract import FrozenStudy
from .shadow_assignment_parity import AssignedOpportunity, audit_shadow_assignment_parity
from .shadow_eight_arm_runner import (
    PolicyFactory, ShadowMatrix, run_shadow_eight_arm_matrix,
)
from .task_view_boundary import AgentTaskView
from .vector_policy import RESOURCE_FIELDS, ResourceVector

_SHA = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED = frozenset(("generate", "repair", "retrieve", "test", "static_analysis"))
_STAGE = "SYNTHETIC_PUBLIC_OUTCOME_REPLAY_ONLY"
PairKey = tuple[str, str, int, str]


def _vector(v: ResourceVector) -> dict:
    return {x: getattr(v, x) for x in RESOURCE_FIELDS}


@dataclass(frozen=True, slots=True)
class FrozenPublicOutcome:
    kind: str
    occurrence: int
    prior_patch_sha256: str | None
    upper_bound: ResourceVector
    used: ResourceVector
    feedback: str = ""
    patch: str | None = None

    def __post_init__(self):
        if type(self.kind) is not str or self.kind not in _ALLOWED:
            raise ValueError("unsupported frozen public action")
        if type(self.occurrence) is not int or not 0 <= self.occurrence <= 31:
            raise ValueError("bounded action occurrence 0..31 required")
        target = self.prior_patch_sha256
        if target is not None and (type(target) is not str or not _SHA.fullmatch(target)):
            raise ValueError("prior candidate must have canonical SHA256")
        if self.kind == "generate" and target is not None:
            raise ValueError("generation outcome cannot depend on prior candidate")
        if self.kind in ("repair", "test", "static_analysis") and target is None:
            raise ValueError("repair/test/static evidence must bind an existing candidate")
        if (not isinstance(self.upper_bound, ResourceVector)
                or not isinstance(self.used, ResourceVector)
                or self.upper_bound.is_free() or self.used.is_free()
                or not self.upper_bound.affordable(self.used)):
            raise ValueError("frozen five-resource receipt exceeds positive reservation")
        receipt = PublicToolReceipt(self.kind, self.used,
                                    feedback=self.feedback, patch=self.patch)
        if self.feedback and not self.feedback.startswith("SYNTHETIC "):
            raise ValueError("only explicit synthetic public feedback allowed")
        if receipt.patch is not None and not receipt.patch.startswith("SYNTHETIC "):
            raise ValueError("only explicit synthetic candidate text allowed")

    @property
    def key(self) -> tuple:
        return (self.kind, self.occurrence, self.prior_patch_sha256)


@dataclass(frozen=True, slots=True)
class SyntheticReplayBook:
    catalog_sha256: str
    entries: tuple[FrozenPublicOutcome, ...]
    stage: str = _STAGE

    def __post_init__(self):
        if self.stage != _STAGE:
            raise ValueError("book cannot self-certify authentic execution")
        if type(self.catalog_sha256) is not str or not _SHA.fullmatch(self.catalog_sha256):
            raise ValueError("book requires declared public opportunity catalog SHA")
        if (type(self.entries) is not tuple or
                not 1 <= len(self.entries) <= 128 or
                any(not isinstance(e, FrozenPublicOutcome) for e in self.entries)):
            raise ValueError("bounded immutable synthetic replay entries required")
        if len({e.key for e in self.entries}) != len(self.entries):
            raise ValueError("duplicate frozen action/occurrence/candidate key")

    @property
    def digest_sha256(self) -> str:
        rows = [{
            "kind": e.kind, "occurrence": e.occurrence,
            "prior_patch_sha256": e.prior_patch_sha256,
            "upper_bound": _vector(e.upper_bound),
            "used": _vector(e.used),
            "feedback": e.feedback, "patch": e.patch,
        } for e in sorted(self.entries, key=lambda x:
                           (x.kind, x.occurrence, x.prior_patch_sha256 or ""))]
        body = {"catalog_sha256": self.catalog_sha256,
                "stage": self.stage, "entries": rows}
        return sha256(json.dumps(body, sort_keys=True,
                        separators=(",",":")).encode("utf-8")).hexdigest()

    def new_public_adapter(self):
        """Create a fresh immutable lookup closure for one policy arm."""
        lookup = {e.key: e for e in self.entries}

        def tool(action: BlindAction, task: AgentTaskView,
                 prior_patch: str | None, history: tuple[PublicStep,...]):
            if not isinstance(task, AgentTaskView) or not task.repository.startswith("synthetic/"):
                raise ValueError("frozen replay accepts synthetic task views only")
            if not isinstance(action, BlindAction) or action.kind not in _ALLOWED:
                raise ValueError("frozen replay accepts typed nonterminal actions only")
            if type(history) is not tuple:
                raise TypeError("typed immutable public history required")
            occurrence = sum(step.kind == action.kind for step in history)
            prior_digest = (
                sha256(prior_patch.encode("utf-8")).hexdigest()
                if prior_patch is not None else None
            )
            key = (action.kind, occurrence,
                   None if action.kind == "generate" else prior_digest)
            row = lookup.get(key)
            if row is None:
                raise ValueError("unrecorded synthetic public tool opportunity")
            if action.upper_bound != row.upper_bound:
                raise ValueError("public tool reservation differs from frozen opportunity")
            return PublicToolReceipt(row.kind, row.used, row.feedback, row.patch)

        return tool


@dataclass(frozen=True)
class FrozenReplayReport:
    shadow: ShadowMatrix
    book_manifest_sha256: str
    matched_contexts: int
    stage: str = "SHARED_SYNTHETIC_REPLAY_NOT_INDEPENDENT_EXPERIMENT"
    authenticated_shared_sampling: bool = False
    model_inference_executed: int = 0
    sealed_oracle_results: int = 0


def run_shared_frozen_replay(
    study: FrozenStudy,
    assignments: tuple[AssignedOpportunity, ...],
    task_views: Mapping[str, AgentTaskView],
    policy_factories: Mapping[str, PolicyFactory],
    books: Mapping[PairKey, SyntheticReplayBook],
    *,
    max_steps: int = 20,
) -> FrozenReplayReport:
    """Share one frozen response book across every policy in each matched pair.

    Reject missing/mismatched book/catalog BEFORE constructing ANY handler.
    Merely giving all arms a common SHA does not certify actual draw parity;
    no real policy fidelity or external runtime integrity is claimed.
    """
    audit_shadow_assignment_parity(study, assignments)
    expected_keys: set[PairKey] = {
        (a.task_id, a.model_id, a.seed, a.budget_id) for a in assignments
    }
    if not isinstance(books, Mapping) or set(books) != expected_keys:
        raise ValueError("complete exact frozen replay books required")
    for a in assignments:
        key = (a.task_id, a.model_id, a.seed, a.budget_id)
        book = books[key]
        if not isinstance(book, SyntheticReplayBook):
            raise TypeError("registered shared replay book must be typed")
        if book.catalog_sha256 != a.common_opportunity_catalog_sha256:
            raise ValueError("shared frozen book differs from declared action catalog")

    digests = [{
        "task_id": t, "model_id": m, "seed": s, "budget_id": b,
        "book_sha256": books[(t,m,s,b)].digest_sha256,
    } for t,m,s,b in sorted(expected_keys)]
    book_manifest = sha256(json.dumps(
        digests, sort_keys=True, separators=(",",":")
    ).encode("utf-8")).hexdigest()

    def public_factory(a: AssignedOpportunity):
        return books[(a.task_id, a.model_id, a.seed,
                      a.budget_id)].new_public_adapter()

    shadow = run_shadow_eight_arm_matrix(
        study, assignments, task_views, policy_factories, public_factory,
        max_steps=max_steps)
    return FrozenReplayReport(shadow, book_manifest, len(expected_keys))
