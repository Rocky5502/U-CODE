"""Evaluator-blind, five-vector accounting skeleton for future approved tasks.

This module never executes source code, downloads repositories, calls an LLM,
or invokes a hidden evaluator. Only a separately approved sandbox adapter may
supply tool receipts. This is NOT a certified resource limiter: OS/runtime
limits and meter authenticity must be checked independently.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable

from .task_view_boundary import AgentTaskView
from .vector_policy import ResourceVector

_TOOL_KINDS = frozenset(("generate", "repair", "retrieve", "test", "static_analysis"))
_TERMINALS = frozenset(("release", "abstain"))
_ALL_KINDS = _TOOL_KINDS | _TERMINALS


def _bounded_text(value: str, field: str, maximum: int, *, allow_empty: bool = True) -> None:
    if type(value) is not str or (not allow_empty and not value.strip()):
        raise ValueError(field + " must be text")
    if len(value.encode("utf-8")) > maximum or "\x00" in value:
        raise ValueError(field + " exceeds safe text boundary")


def _digest(patch: str | None) -> str | None:
    return sha256(patch.encode("utf-8")).hexdigest() if patch is not None else None


@dataclass(frozen=True)
class BlindAction:
    kind: str
    upper_bound: ResourceVector

    def __post_init__(self):
        if type(self.kind) is not str or self.kind not in _ALL_KINDS:
            raise ValueError("unsupported policy action")
        if not isinstance(self.upper_bound, ResourceVector):
            raise TypeError("five-dimensional maximum cost required")
        if self.kind in _TERMINALS and not self.upper_bound.is_free():
            raise ValueError("terminal action cannot reserve resources")
        if self.kind in _TOOL_KINDS and self.upper_bound.is_free():
            raise ValueError("nonterminal action needs positive resource reservation")


@dataclass(frozen=True)
class PublicToolReceipt:
    """Policy-visible tool result, never a held-out evaluator verdict.

    `used` must come from an independently audited adapter in real experiments.
    The schema cannot prove that text feedback is free from leaked gold data.
    """
    kind: str
    used: ResourceVector
    feedback: str = ""
    patch: str | None = None

    def __post_init__(self):
        if self.kind not in _TOOL_KINDS:
            raise ValueError("tool receipt has unsupported action")
        if not isinstance(self.used, ResourceVector):
            raise TypeError("tool receipt needs typed five-resource measurement")
        _bounded_text(self.feedback, "public feedback", 32768)
        if self.kind in ("generate", "repair"):
            _bounded_text(self.patch, "generated patch", 131072, allow_empty=False)
        elif self.patch is not None:
            raise ValueError("diagnostic action cannot inject candidate patch")


@dataclass(frozen=True)
class PublicStep:
    kind: str
    used: ResourceVector
    remaining: ResourceVector
    feedback: str
    candidate_sha256: str | None


@dataclass(frozen=True)
class BlindState:
    task: AgentTaskView
    remaining: ResourceVector
    candidate_patch: str | None
    history: tuple[PublicStep, ...]


@dataclass(frozen=True)
class BlindSession:
    """No correctness field. Scoring must happen AFTER this session returns."""
    status: str
    released_patch: str | None
    remaining: ResourceVector
    history: tuple[PublicStep, ...]
    accounting_verified: bool
    task_spec_sha256: str

    @property
    def released_patch_sha256(self) -> str | None:
        return _digest(self.released_patch)


Policy = Callable[[BlindState], BlindAction]
PublicTool = Callable[[BlindAction, AgentTaskView, str | None,
                       tuple[PublicStep, ...]], PublicToolReceipt]


def run_blind_policy(
    task: AgentTaskView,
    budget: ResourceVector,
    policy: Policy,
    public_tool: PublicTool,
    *,
    max_steps: int = 20,
) -> BlindSession:
    """Run an evaluator-blind, bounded trace with conservative reservations.

    Policy observes only AgentTaskView, visible tool feedback, the current
    candidate and remaining budget. No evaluator is accepted or invoked.
    An action is dispatched only if its declared upper-bound cost fits ALL
    five caps. If an adapter fails, lies about its action, or reports a cost
    over its reservation, halt with UNVERIFIED accounting. External quota
    enforcement is still mandatory before running real third-party code.
    """
    if not isinstance(task, AgentTaskView):
        raise TypeError("only typed source-free task views may reach a policy")
    if not isinstance(budget, ResourceVector):
        raise TypeError("five-dimensional budget required")
    if not callable(policy) or not callable(public_tool):
        raise TypeError("policy and policy-visible adapter must be callables")
    if type(max_steps) is not int or not 1 <= max_steps <= 1000:
        raise ValueError("bounded positive max_steps required")

    remaining = budget
    history: list[PublicStep] = []
    patch: str | None = None

    def finish(status: str, released: str | None = None,
               verified: bool = True) -> BlindSession:
        return BlindSession(status, released, remaining, tuple(history),
                            verified, task.spec_sha256)

    for _ in range(max_steps):
        choice = policy(BlindState(task, remaining, patch, tuple(history)))
        if not isinstance(choice, BlindAction):
            raise TypeError("policy must return a BlindAction")
        if choice.kind == "abstain":
            return finish("ABSTAINED")
        if choice.kind == "release":
            return finish("RELEASED_PENDING_INDEPENDENT_EVALUATION", patch) if patch else finish(
                "INVALID_RELEASE_NO_PATCH")
        if choice.kind == "repair" and patch is None:
            return finish("INVALID_REPAIR_NO_PATCH")
        if choice.kind in ("test", "static_analysis") and patch is None:
            return finish("INVALID_DIAGNOSTIC_NO_PATCH")
        if not remaining.affordable(choice.upper_bound):
            return finish("BUDGET_BLOCKED")

        # Reserve the full declared maximum before invoking any tool.
        reserved_remaining = remaining.subtract(choice.upper_bound)
        try:
            receipt = public_tool(choice, task, patch, tuple(history))
        except Exception:
            remaining = reserved_remaining
            return finish("TOOL_FAILED_COST_UNVERIFIED", verified=False)
        if not isinstance(receipt, PublicToolReceipt) or receipt.kind != choice.kind:
            remaining = reserved_remaining
            return finish("TOOL_RECEIPT_INVALID", verified=False)
        if not choice.upper_bound.affordable(receipt.used):
            remaining = reserved_remaining
            return finish("TOOL_COST_OVERRUN", verified=False)

        remaining = remaining.subtract(receipt.used)
        if choice.kind in ("generate", "repair"):
            patch = receipt.patch
        history.append(PublicStep(choice.kind, receipt.used, remaining,
                                  receipt.feedback, _digest(patch)))
    return finish("MAX_STEPS_REACHED")
