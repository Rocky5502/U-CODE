"""Read-only planning/preflight for ALL SIX U-CODE selected open-weight LLMs.

No weight downloads, inference, GPU rentals, shell calls, access tokens or
third-party code execution. A configuration is not an operational service.
The canonical user-selected model roster is checked on every invocation.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "accepted_six_model_study_2026-10-25.json"
PLAN = ROOT / "configs" / "ai_galaxy_six_model_deployment_2026-10-27.json"
REVISION_FIELDS = ("checkpoint_revision", "tokenizer_revision")
REQUIRED_GATES = (
    "frozen_weight_and_tokenizer_commit_sha",
    "full_license_and_terms_review",
    "model_weight_hashes_verified",
    "inference_engine_version_frozen",
    "trust_remote_code_audited_if_required",
    "verified_gpu_precision_support",
    "measured_peak_vram_and_prefill_latency",
    "independent_resource_monitoring",
    "task_admission_and_sealed_oracle_for_scientific_trials",
)
HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class PlannedModel:
    model_id: str
    gpu: str
    weight_floor_gb: float
    context: int
    endpoint_port: int
    blockers: tuple[str, ...]
    executable: bool = False


def _revision(value):
    return type(value) is str and len(value) == 40 and all(ch in HEX for ch in value)


def inspect_plan(selected: dict, plan: dict) -> tuple[PlannedModel, ...]:
    """Fail closed on six-model identity drift, typos or invented readiness."""
    if (not isinstance(selected, dict) or not isinstance(plan, dict)
        or selected.get("model_count") != 6
        or plan.get("status") != "PROSPECTIVE_SIX_MODEL_DEPLOYMENT_CONFIG_ONLY_NOT_EXECUTED"
        or plan.get("source_manifest") != "configs/accepted_six_model_study_2026-10-25.json"):
        raise ValueError("the six-model study identity/status must remain prospective")
    source = selected.get("models")
    models = plan.get("models")
    if (type(source) is not list or type(models) is not list
        or len(source) != 6 or len(models) != 6):
        raise ValueError("exact six-model registry required")
    ids = [x.get("model_id") for x in source]
    planned = [x.get("model_id") for x in models]
    if len(set(ids)) != 6 or planned != ids:
        raise ValueError("planned six model IDs must match the canonical ordered roster")
    expected_port = 8100
    result = []
    for original, item in zip(source, models):
        if (original.get("inference_execution_status") != "NOT_RUN"
            or original.get("model_weights_verified") is not False
            or original.get("independently_verified_task_runs") != 0):
            raise ValueError("canonical model manifest claims unverified execution")
        if item.get("model_inference_executed") is not False:
            raise ValueError("deployment plan must never imply execution")
        if item.get("model_weights_verified") is not False:
            raise ValueError("unverified model weights cannot be promoted")
        if item.get("license_and_terms_approved") is not False:
            raise ValueError("license and terms cannot be silently approved")
        if item.get("vllm_openai_compatible_endpoint_port") != expected_port:
            raise ValueError("each model needs its frozen unique endpoint port")
        expected_port += 1
        for field in REVISION_FIELDS:
            if item.get(field) is not None and not _revision(item[field]):
                raise ValueError("model/tokenizer revision must be full 40-hex commit")
        if item.get("checkpoint_revision") is not None and (
                original.get("checkpoint_revision") != item.get("checkpoint_revision")):
            raise ValueError("deployment checkpoint revision mismatches canonical roster")
        if (type(item.get("parameters_billions_approx")) not in (int, float)
            or type(item.get("bf16_weight_floor_decimal_gb_approx")) not in (int, float)
            or item["parameters_billions_approx"] <= 0
            or item["bf16_weight_floor_decimal_gb_approx"] <= 0):
            raise ValueError("valid positive model weights required")
        if item.get("gpu_vram_gb_requested") != 80 or (
            item.get("gpu_count_for_model") != 1
        ):
            raise ValueError("initial one-GPU 80GB sizing must be explicit")
        ctx = item.get("max_model_len_tokens_initial")
        if type(ctx) is not int or not 2048 <= ctx <= 16384:
            raise ValueError("unmeasured initial context exceeds conservative bound")
        mem = item.get("memory_utilization_ceiling")
        if type(mem) not in (float, int) or not 0 < mem <= 0.85:
            raise ValueError("unsafe preflight memory utilization")
        if item.get("max_num_seqs_initial") != 1:
            raise ValueError("unmeasured concurrent sequences must be one")
        blockers = [
            "immutable_revision_missing",
            "license_or_gated_terms_not_audited",
            "weights_and_tokenizer_not_verified",
            "inference_engine_version_not_pinned",
            "runtime_precision_and_VRAM_not_measured",
            "independent_runner_and_oracle_not_approved",
        ]
        if item.get("model_native_fp8_engine_verification_required"):
            blockers.append("native_fp8_accelerator_compatibility_not_tested")
        if item.get("untrusted_custom_model_code_must_be_reviewed"):
            blockers.append("untrusted_custom_code_security_review_missing")
        if item.get("restricted_terms_access_must_be_accepted"):
            blockers.append("gated_provider_terms_not_accepted")
        result.append(PlannedModel(
            item["model_id"], item["rental_gpu_for_initial_preflight"],
            float(item["bf16_weight_floor_decimal_gb_approx"]),
            ctx, item["vllm_openai_compatible_endpoint_port"],
            tuple(blockers),
        ))
    profiles = plan.get("profiles")
    if not isinstance(profiles, dict) or set(profiles) != {
        "sequential_one_gpu", "simultaneous_six_gpu"
    }:
        raise ValueError("sequential and simultaneous profiles both required")
    if (profiles["sequential_one_gpu"].get("requested_gpu_count") != 1
        or profiles["simultaneous_six_gpu"].get("requested_gpu_count") != 6):
        raise ValueError("GPU scheduling profiles contradictory")
    if set(plan.get("deployment_gates", {})) != set(REQUIRED_GATES):
        raise ValueError("all nine readiness gates required")
    if not all(plan["deployment_gates"].values()):
        raise ValueError("do not disable deployment gates")
    return tuple(result)


def load_plan():
    return (json.loads(SOURCE.read_text(encoding="utf-8")),
            json.loads(PLAN.read_text(encoding="utf-8")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("sequential_one_gpu",
                        "simultaneous_six_gpu"), default="sequential_one_gpu")
    parser.add_argument("--json", action="store_true",
                        help="Print six planned services in JSON; never launches models")
    args = parser.parse_args()
    selected, plan = load_plan()
    choices = inspect_plan(selected, plan)
    profile = plan["profiles"][args.profile]
    info = {
        "status": "PLAN_VALIDATED_NOT_READY_FOR_INFERENCE",
        "gpu_profile": args.profile,
        "gpu_count": profile["requested_gpu_count"],
        "model_count": len(choices),
        "model_running_count": 0,
        "all_checkpoints_frozen": False,
        "model_configs": [
            dict(model_id=x.model_id, gpu=x.gpu,
                 bf16_weight_floor_decimal_gb_approx=x.weight_floor_gb,
                 initial_context_tokens=x.context, endpoint_port=x.endpoint_port,
                 blockers=x.blockers, executable=x.executable)
            for x in choices
        ],
        "provider_inventory_and_pricing": "VERIFY_LIVE_BEFORE_RENTAL",
    }
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print("U-CODE SIX-MODEL CONFIG CHECK: VALIDATED; INFERENCE NOT READY")
        print(f"GPU profile: {args.profile} ({info['gpu_count']} GPU reservations)")
        for row in choices:
            print(f"- {row.model_id}: {row.gpu}; weights BF16 ~{row.weight_floor_gb:.1f} GB "
                  f"(excludes KV/overhead); ctx {row.context}; port {row.endpoint_port}; "
                  f"BLOCKED ({len(row.blockers)} gates)")
        print("No paid rental, inference, checkpoint pinning or dataset run performed.")


if __name__ == "__main__":
    main()
