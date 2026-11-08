"""Public Hugging Face model-card *observation* audit for U-CODE P0-3.

No network, model download, trust of unsigned Hub metadata, weights loading,
private account access, license approval or model inference. Estimates of
BF16 weight storage come from APPROXIMATE parameter counts, NOT model
safetensor files or a runtime measurement. No fit/feasibility certification.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from math import isfinite
from pathlib import Path
import json
from typing import Mapping

from .model_readiness import validate_selected_manifest

ROOT = Path(__file__).resolve().parents[2]
_OBSERVATIONS_PATH = ROOT / (
    "data/admission/2026-11-09/six_model_public_hub_cards_OBSERVATION_ONLY.json"
)
_SELECTED_PATH = ROOT / "configs/accepted_six_model_study_2026-10-25.json"
_SOURCE_PATH = ROOT / "configs/models_v2_2026-10-24.json"
_PROTOCOL_PATH = ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json"

_TOP = frozenset({
    "schema_version", "observed_on_utc_date", "stage", "observation_method",
    "source_model_ids_frozen_in", "source_hub", "no_weights_downloaded",
    "all_model_checkpoint_revisions_independently_verified",
    "signed_card_snapshot_held", "authenticated_full_license_review_complete",
    "private_gated_access_validated", "runtime_vram_test_performed",
    "real_model_inferences", "observations",
})
_ROW = frozenset({
    "model_id", "card_url", "hub_license_id", "hub_card_reports_gated",
    "reported_parameters_millions_approx", "architecture_tag", "library_tag",
    "pin_model_sha40", "pin_tokenizer_sha40",
    "full_license_text_review_status", "account_terms_verified",
    "actual_weight_bytes_verified", "measured_peak_vram_gib",
})
_STAGE = "PUBLIC_HUB_CARD_METADATA_OBSERVATION_ONLY_NOT_APPROVED"
_HELD_FALSE = (
    "all_model_checkpoint_revisions_independently_verified",
    "signed_card_snapshot_held", "authenticated_full_license_review_complete",
    "private_gated_access_validated", "runtime_vram_test_performed",
)
_LICENSES = frozenset({"apache-2.0", "other", "gemma", "llama3.1"})
_ARCH = frozenset({"qwen2", "qwen3_moe", "mistral3", "deepseek_v2", "gemma", "llama"})
_LIBRARIES = frozenset({"transformers", "vllm"})

def _read_json_object(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if type(result) is not dict:
        raise ValueError("expected JSON object from local frozen research file")
    return result

def audit_public_card_observations(
    observations: Mapping, selected: Mapping, source_inventory: Mapping,
    protocol: Mapping, *, comparison_capacity_gib: int = 16,
) -> dict:
    """Compare unsigned public metadata against the unchanged selected roster.

    This MUST NOT write to the execution manifest or manufacture SHA pins.
    The 16-GiB capacity is a WHAT-IF, not a measured GPU memory value.
    """
    if (type(observations) is not dict or set(observations) != _TOP
            or observations["schema_version"] != "1.0"
            or observations["observed_on_utc_date"] != "2026-11-09"
            or observations["stage"] != _STAGE
            or type(observations["observation_method"]) is not str
            or not observations["observation_method"].startswith(
                "Hugging Face connected hub_repo_details public model metadata")
            or observations["source_model_ids_frozen_in"] !=
                "configs/accepted_six_model_study_2026-10-25.json"
            or observations["source_hub"] != "https://huggingface.co"
            or observations["no_weights_downloaded"] is not True
            or observations["real_model_inferences"] != 0
            or type(observations["real_model_inferences"]) is not int
            or any(observations[x] is not False for x in _HELD_FALSE)):
        raise ValueError("unsigned public model observations cannot self-promote")
    if type(comparison_capacity_gib) is not int or not 1 <= comparison_capacity_gib <= 1024:
        raise ValueError("bounded integer hypothetical comparison capacity required")
    if (type(selected) is not dict or type(source_inventory) is not dict
            or type(protocol) is not dict
            or selected.get("phase") !=
                "ALL_SIX_SELECTED_FOR_PLANNING_NOT_READY_FOR_INFERENCE"
            or selected.get("model_count") != 6
            or selected.get("no_paid_compute_approved") is not True
            or protocol.get("status") !=
                "PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"
            or protocol.get("results_measured") is not False
            or protocol.get("external_code_executions") != 0
            or protocol.get("qualified_task_ids") != []
            or protocol.get("model_revisions_frozen") is not False):
        raise ValueError("selected or registered study has false readiness claims")
    selected_models = selected.get("models")
    if type(selected_models) is not list or len(selected_models) != 6:
        raise ValueError("all six selected models required")
    ids = [m.get("model_id") for m in selected_models]
    if protocol.get("model_ids") != ids or len(set(ids)) != 6:
        raise ValueError("public observation cannot change frozen model roster")
    assessments = validate_selected_manifest(selected, source_inventory)
    if len(assessments) != 6 or any(x.runnable for x in assessments):
        raise ValueError("model readiness self-promoted without license/hardware checks")
    if any(m.get("inference_execution_status") != "NOT_RUN"
           or m.get("independently_verified_task_runs") != 0
           for m in selected_models):
        raise ValueError("public card observations cannot make real model outcomes")
    rows = observations["observations"]
    if type(rows) is not list or len(rows) != 6:
        raise ValueError("exactly six public metadata observation rows required")
    if [r.get("model_id") for r in rows if type(r) is dict] != ids:
        raise ValueError("model observation roster/order drift, duplicate or missing ID")
    report_rows = []
    for row, model, current in zip(rows, selected_models, assessments):
        if type(row) is not dict or set(row) != _ROW:
            raise ValueError("unknown privileged or missing public card field")
        model_id = model["model_id"]
        if row["card_url"] != model["card_url"]:
            raise ValueError("public card URL differs from selected source")
        if (type(row["hub_license_id"]) is not str
                or row["hub_license_id"] not in _LICENSES
                or type(row["hub_card_reports_gated"]) is not bool
                or row["architecture_tag"] not in _ARCH
                or row["library_tag"] not in _LIBRARIES):
            raise ValueError("invalid public model metadata tags")
        approx = row["reported_parameters_millions_approx"]
        if (type(approx) not in (int, float) or not isfinite(approx)
                or not 1000 <= approx <= 100000):
            raise ValueError("approximate parameter count malformed")
        if (row["pin_model_sha40"] is not None
                or row["pin_tokenizer_sha40"] is not None
                or row["full_license_text_review_status"] != "NOT_DONE"
                or row["account_terms_verified"] is not False
                or row["actual_weight_bytes_verified"] is not False
                or row["measured_peak_vram_gib"] is not None):
            raise ValueError("public card does not authenticate license, SHA or VRAM")
        # Decimal(str(...)) avoids binary-floating drift; this is a rough
        # BF16-only weights approximation, not an observed file byte count.
        gib = (Decimal(str(approx)) * Decimal("1000000") * Decimal(2)
               / Decimal(1024 ** 3))
        approx_gib = str(gib.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        differs = row["hub_license_id"] != model["card_license"]
        report_rows.append({
            "model_id": model_id,
            "public_card_url": row["card_url"],
            "public_hub_license_tag_observed_not_legal_review": row["hub_license_id"],
            "historical_planning_license_label": model["card_license"],
            "public_card_license_label_mismatch": differs,
            "public_card_reports_gated_not_user_entitlement": row["hub_card_reports_gated"],
            "architecture_tag_observed": row["architecture_tag"],
            "reported_parameters_millions_approx": approx,
            "bf16_weights_only_rough_gib": approx_gib,
            "hypothetical_capacity_gib": comparison_capacity_gib,
            "abstract_bf16_storage_class": (
                "ROUGH_WEIGHTS_ONLY_EXCEEDS_HYPOTHETICAL_CAPACITY"
                if gib > Decimal(comparison_capacity_gib)
                else "ROUGH_WEIGHTS_ONLY_WITHIN_CAPACITY_NOT_LOAD_FEASIBILITY"),
            "full_license_and_access_authorized": False,
            "checkpoint_and_tokenizer_sha_pinned": False,
            "quantized_runtime_feasibility_proven": False,
            "actual_peak_vram_measured": False,
            "model_runnable_for_study": False,
            "existing_execution_blockers": list(current.blockers),
        })
    return {
        "schema_version": "1.0",
        "stage": "SIX_MODEL_PUBLIC_CARD_PROVENANCE_GAP_AUDIT_ONLY",
        "source_observed_on_utc_date": observations["observed_on_utc_date"],
        "card_observations_authentic_signed_snapshots": False,
        "selected_original_six_model_ids_unchanged": True,
        "planned_models": 6,
        "reported_public_card_gated_count": sum(
            int(r["public_card_reports_gated_not_user_entitlement"]) for r in report_rows),
        "public_license_label_mismatches": sum(
            int(r["public_card_license_label_mismatch"]) for r in report_rows),
        "public_metadata_is_not_full_license_review": True,
        "hypothetical_hardware_gib_not_observed": comparison_capacity_gib,
        "bf16_estimates_are_rough_weights_only_not_runtime_predictions": True,
        "actual_qualified_checkpoints": 0,
        "verified_private_model_accesses": 0,
        "full_license_reviews_completed": 0,
        "models_loaded_or_inferred": 0,
        "real_model_outcomes": 0,
        "operator_must_freeze_real_revisions_and_licenses": True,
        "model_rows": report_rows,
    }

def build_public_card_audit(*, root: Path = ROOT,
                            comparison_capacity_gib: int = 16) -> dict:
    base = Path(root)
    return audit_public_card_observations(
        _read_json_object(base /
            "data/admission/2026-11-09/six_model_public_hub_cards_OBSERVATION_ONLY.json"),
        _read_json_object(base /
            "configs/accepted_six_model_study_2026-10-25.json"),
        _read_json_object(base / "configs/models_v2_2026-10-24.json"),
        _read_json_object(base /
            "configs/confirmatory_sbse_protocol_2026-10-25.json"),
        comparison_capacity_gib=comparison_capacity_gib)
