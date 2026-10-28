"""Full eight-arm *shadow* wiring through evaluator-blind reference execution.

This is integration of eight registered handler slots, NOT a faithful
implementation of eight research algorithms. Policies/tools are supplied by
the caller and remain unauthenticated callbacks: this module is NOT a secure
sandbox and MUST NOT be connected to third-party code or a hidden oracle.
No scoring, patch correctness, model execution, or external attestations.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable, Mapping

from .blind_policy_trace import BlindSession, BlindState, BlindAction, PublicToolReceipt, run_blind_policy
from .experiment_contract import FrozenStudy
from .shadow_assignment_parity import AssignedOpportunity, audit_shadow_assignment_parity
from .task_view_boundary import AgentTaskView
from .vector_policy import RESOURCE_FIELDS, ResourceVector

POLICIES = frozenset((
    "ucode_conditional_bes", "ucode_unconditional_bes",
    "no_uncertainty_search", "uncertainty_only", "fixed_testing",
    "selective_verification", "mcts_search", "replay_search",
))
_STAGE = "SHADOW_ADAPTER_INTEGRATION_NOT_EIGHT_FAITHFUL_ALGORITHMS"
PolicyFactory = Callable[[AssignedOpportunity], Callable[[BlindState], BlindAction]]
ToolFactory = Callable[[AssignedOpportunity], Callable[..., PublicToolReceipt]]


@dataclass(frozen=True)
class ShadowArm:
    task_id: str
    model_id: str
    seed: int
    budget_id: str
    policy_id: str
    terminal_status: str
    patch_sha256: str | None
    visible_trace_sha256: str
    reported_remaining: ResourceVector
    accounting_verified_by_schema_only: bool
    public_action_count: int


@dataclass(frozen=True)
class ShadowMatrix:
    stage: str
    declared_assignment_sha256: str
    total_shadow_arm_wirings: int
    arms: tuple[ShadowArm, ...]
    independent_oracle_labels: int = 0
    authorized_external_executions: int = 0
    real_task_successes: int = 0
    verified_model_inferences: int = 0
    policy_fidelity_attested: bool = False
    verified_hardware_metering: bool = False


def _visible_trace_digest(session: BlindSession) -> str:
    """Hash bounded public step metadata, NOT free-text feedback or patch."""
    payload = {
        "status": session.status, "task_spec_sha256": session.task_spec_sha256,
        "patch_sha256": session.released_patch_sha256,
        "accounting_schema_only": session.accounting_verified,
        "steps": [{
            "kind": h.kind, "patch_sha256": h.candidate_sha256,
            "used": {x: getattr(h.used, x) for x in RESOURCE_FIELDS},
            "remaining": {x: getattr(h.remaining, x) for x in RESOURCE_FIELDS},
        } for h in session.history],
        "remaining": {x: getattr(session.remaining, x) for x in RESOURCE_FIELDS},
    }
    return sha256(json.dumps(payload,sort_keys=True,
                             separators=(",",":")).encode("utf-8")).hexdigest()


def run_shadow_eight_arm_matrix(
    study: FrozenStudy,
    assignments: tuple[AssignedOpportunity, ...],
    task_views: Mapping[str, AgentTaskView],
    handler_factories: Mapping[str, PolicyFactory],
    public_tool_factory: ToolFactory,
    *,
    max_steps: int = 20,
) -> ShadowMatrix:
    """Wires eight registered policy names into one evaluator-blind API.

    Each policy arm receives a new handler and public tool callback; all
    declared starting conditions must pass M4 matching before ANY callback
    is constructed. No evaluator or oracle callback is accepted. The module
    cannot authenticate that an injected callback performs no I/O. Only
    first-party synthetic adapters belong in this *offline* function.
    """
    if not isinstance(study, FrozenStudy):
        raise TypeError("frozen study required")
    if (len(study.model_ids) != 6 or len(study.policies) != 8
            or set(study.policies) != POLICIES):
        raise ValueError("exactly eight registered policies and six planned models required")
    if (not isinstance(task_views, Mapping)
            or set(task_views) != {t for t, _ in study.task_lineages}
            or not isinstance(handler_factories, Mapping)
            or set(handler_factories) != POLICIES):
        raise ValueError("missing/extra task or eight policy handler registrations")
    if not callable(public_tool_factory):
        raise TypeError("public tool factory required")
    if type(max_steps) is not int or not 1 <= max_steps <= 1000:
        raise ValueError("bounded max steps required")
    for _, factory in handler_factories.items():
        if not callable(factory):
            raise ValueError("each registered policy must supply its own factory")
    view_specs = {}
    for task_id, view in task_views.items():
        if not isinstance(view, AgentTaskView):
            raise TypeError("only typed task view may be assigned")
        view_specs[task_id] = view
    # Audit the complete matrix before constructing policy callbacks,
    # to prevent partial execution on a malformed assignment grid.
    audit = audit_shadow_assignment_parity(study, assignments)
    for a in assignments:
        view = view_specs[a.task_id]
        if (view.spec_sha256 != a.task_spec_sha256
                or view.base_sha != a.pre_fix_base_sha40):
            raise ValueError("assigned visible task/spec differs from approved projection")
    results = []
    for a in sorted(assignments,
                    key=lambda x: (x.task_id, x.model_id, x.seed,
                                   x.budget_id, x.policy_id)):
        handler = handler_factories[a.policy_id](a)
        tool = public_tool_factory(a)
        if not callable(handler) or not callable(tool):
            raise TypeError("registered handler and public tool must be callable")
        session = run_blind_policy(view_specs[a.task_id], a.resource_cap,
                                   handler, tool, max_steps=max_steps)
        results.append(ShadowArm(
            task_id=a.task_id, model_id=a.model_id, seed=a.seed,
            budget_id=a.budget_id, policy_id=a.policy_id,
            terminal_status=session.status,
            patch_sha256=session.released_patch_sha256,
            visible_trace_sha256=_visible_trace_digest(session),
            reported_remaining=session.remaining,
            accounting_verified_by_schema_only=session.accounting_verified,
            public_action_count=len(session.history),
        ))
    return ShadowMatrix(
        stage=_STAGE,
        declared_assignment_sha256=audit.declared_assignment_digest,
        total_shadow_arm_wirings=len(results),
        arms=tuple(results),
    )
