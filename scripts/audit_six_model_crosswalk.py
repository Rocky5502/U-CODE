"""M5: reconcile six-model selection, deployment plan and eight-policy protocol.

No downloads, hardware access, tokens, third-party code or approved model
terms. A checked-in manifest cannot sign its own readiness. This is only a
planning crosswalk over already-reviewed static configuration files.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from scripts.plan_ai_galaxy_six_models import inspect_plan
from scripts.validate_sbse_protocol import validate_prospective_protocol
from ucode.model_readiness import validate_selected_manifest

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ROOT / "configs/accepted_six_model_study_2026-10-25.json"
INVENTORY = ROOT / "configs/models_v2_2026-10-24.json"
DEPLOYMENT = ROOT / "configs/ai_galaxy_six_model_deployment_2026-10-27.json"
PROTOCOL = ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json"


@dataclass(frozen=True)
class CrosswalkModel:
    model_id: str
    proposed_endpoint_port: int
    planned_gpu: str
    study_blockers: tuple[str,...]
    deployment_blockers: tuple[str,...]
    additional_risk: str
    inference_approved: bool = False
    real_task_trials: int = 0


@dataclass(frozen=True)
class Crosswalk:
    status: str
    models: tuple[CrosswalkModel,...]
    policy_count: int
    primary_treatment: str
    primary_comparator: str
    qualified_tasks: int = 0
    model_executions: int = 0
    paid_gpu_rentals: int = 0
    successful_benchmark_outcomes: int = 0


def validate_model_protocol_crosswalk(
    selected: dict, inventory: dict, deployment: dict, protocol: dict,
) -> Crosswalk:
    """Verify identities and explicit blockers, never report trial readiness."""
    models = validate_selected_manifest(selected, inventory)
    planned = inspect_plan(selected, deployment)
    protocol_status = validate_prospective_protocol(protocol, selected)
    selected_order = tuple(m.model_id for m in models)
    if (tuple(protocol.get("model_ids", ())) != selected_order or
            tuple(m.model_id for m in planned) != selected_order):
        raise ValueError("three-way model roster and ordering mismatch")
    if protocol_status["qualified_tasks"] != 0:
        raise ValueError("crosswalk cannot certify task admission")
    if any(m.runnable for m in models) or any(p.executable for p in planned):
        raise ValueError("unexpected inferred operational readiness from static manifests")
    result = []
    for index, (model, hardware) in enumerate(zip(models, planned)):
        conf = deployment["models"][index]
        if conf.get("model_id") != model.model_id:
            raise ValueError("deployment entry order changed")
        original = selected["models"][index]
        if (original.get("checkpoint_revision") != conf.get("checkpoint_revision") or
                original.get("tokenizer_revision") != conf.get("tokenizer_revision")):
            raise ValueError("cross-manifest checkpoint or tokenizer revision drift")
        if model.model_id.startswith("deepseek-ai/"):
            risk = "CUSTOM_MODEL_CODE_INDEPENDENT_SECURITY_AUDIT_REQUIRED"
            if conf.get("untrusted_custom_model_code_must_be_reviewed") is not True:
                raise ValueError("DeepSeek code audit risk cannot be erased")
        elif model.model_id.startswith(("google/", "meta-llama/")):
            risk = "MODEL_SPECIFIC_ACCESS_TERMS_REVIEW_REQUIRED"
            if conf.get("restricted_terms_access_must_be_accepted") is not True:
                raise ValueError("restricted terms gate cannot be erased")
        elif model.model_id.startswith("mistralai/"):
            risk = "A100_PRECISION_COMPATIBILITY_PREFLIGHT_REQUIRED"
            if conf.get("model_native_fp8_engine_verification_required") is not True:
                raise ValueError("Devstral precision preflight cannot be erased")
        else:
            risk = "RUNTIME_AND_MEMORY_PREFLIGHT_REQUIRED"
        result.append(CrosswalkModel(
            model_id=model.model_id,
            proposed_endpoint_port=hardware.endpoint_port,
            planned_gpu=hardware.gpu,
            study_blockers=model.blockers,
            deployment_blockers=hardware.blockers,
            additional_risk=risk,
        ))
    if len(result) != 6:
        raise ValueError("silent model attrition")
    return Crosswalk(
        "PLAN_RECONCILED_ALL_MODELS_BLOCKED_NO_INFERENCE",
        tuple(result), len(protocol["policy_ids"]),
        protocol["primary_treatment"], protocol["primary_comparator"],
    )


def main():
    selected, inventory, deployment, protocol = (
        json.loads(p.read_text("utf-8")) for p in
        (SELECTED, INVENTORY, DEPLOYMENT, PROTOCOL)
    )
    crosswalk = validate_model_protocol_crosswalk(
        selected, inventory, deployment, protocol)
    out = {
        "status": crosswalk.status,
        "six_models": [{
            "id": m.model_id, "planned_port": m.proposed_endpoint_port,
            "planned_gpu": m.planned_gpu,
            "study_blockers": list(m.study_blockers),
            "deployment_blockers": list(m.deployment_blockers),
            "additional_risk": m.additional_risk,
            "inference_approved": m.inference_approved,
            "real_task_trials": m.real_task_trials,
        } for m in crosswalk.models],
        "policies": crosswalk.policy_count,
        "primary": [crosswalk.primary_treatment,
                    crosswalk.primary_comparator],
        "qualified_tasks": 0, "model_executions": 0, "paid_gpu_rentals": 0,
        "successful_benchmark_outcomes": 0,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
