"""Reproducibility gate for the six user-selected U-CODE model candidates.

Selecting a public model for study does NOT confer terms acceptance, a
particular model snapshot, compatible memory, or permission to execute.
The gate returns blockers; it does not download weights or run inference.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SELECTED = ROOT / "configs" / "accepted_six_model_study_2026-10-25.json"
SOURCE_V2 = ROOT / "configs" / "models_v2_2026-10-24.json"
REV = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SPECIAL_TERMS = {"gemma", "llama3.1"}
NON_APACHE = {"deepseek-license", "gemma", "llama3.1"}


@dataclass(frozen=True)
class ModelReadiness:
    model_id: str
    accepted_for_planning: bool
    blockers: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return self.accepted_for_planning and not self.blockers


def load_selected_models(path: Path = SELECTED) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_selected_manifest(
    selected: dict, source_inventory: dict,
) -> tuple[ModelReadiness, ...]:
    """Fail closed on changed scientific identities or false execution claims."""
    entries = selected.get("models")
    originals = source_inventory.get("models")
    if (selected.get("phase") != "ALL_SIX_SELECTED_FOR_PLANNING_NOT_READY_FOR_INFERENCE"
            or type(entries) is not list or len(entries) != 6
            or type(originals) is not list or len(originals) != 6):
        raise ValueError("expected six user-selected, unexecuted model candidates")
    original_by_id = {m["id"]: m for m in originals}
    if len(original_by_id) != 6:
        raise ValueError("source inventory has duplicate model IDs")
    selected_ids = [m.get("model_id") for m in entries]
    if len(set(selected_ids)) != 6 or set(selected_ids) != set(original_by_id):
        raise ValueError("six selected IDs must exactly match source v2 inventory")
    answers = []
    for m in entries:
        model_id = m["model_id"]
        upstream = original_by_id[model_id]
        if (m.get("card_url") != upstream.get("url")
                or m.get("card_license") != upstream.get("license_card")
                and model_id != "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
                and model_id != "google/codegemma-1.1-7b-it"
                and model_id != "meta-llama/Llama-3.1-8B-Instruct"):
            raise ValueError("selected model source URL/license conflicts with v2")
        if m.get("selection") != "user_selected_for_planning" or m.get("study_included") is not True:
            raise ValueError("all six requested models must be in the research plan")
        if m.get("inference_execution_status") == "NOT_RUN" and m.get("independently_verified_task_runs") != 0:
            raise ValueError("nonzero experiment count despite model never run")
        if m.get("inference_execution_status") not in ("NOT_RUN", "COMPLETED_AND_AUDITED"):
            raise ValueError("unknown model execution state")
        blockers = []
        if m.get("full_license_review") != "APPROVED":
            blockers.append("license_text_not_approved")
        if m.get("card_license") in SPECIAL_TERMS and m.get("gated_terms_verified") is not True:
            blockers.append("gated_terms_unverified")
        for field in ("checkpoint_revision", "tokenizer_revision"):
            rev = m.get(field)
            if not isinstance(rev, str) or not REV.fullmatch(rev):
                blockers.append(f"{field}_not_immutable")
        sha = m.get("frozen_chat_template_sha256")
        if not isinstance(sha, str) or not SHA256.fullmatch(sha):
            blockers.append("chat_template_hash_missing")
        if not m.get("engine_version"):
            blockers.append("inference_engine_unpinned")
        if not m.get("quantization_format"):
            blockers.append("quantization_unpinned")
        gb = m.get("measured_peak_vram_gb")
        if type(gb) not in (int, float) or not 0 < gb < 1024:
            blockers.append("gpu_peak_unmeasured")
        if m.get("model_weights_verified") is not True:
            blockers.append("weights_not_verified")
        if m.get("passed_sandbox_security_review") is not True:
            blockers.append("sandbox_not_approved")
        answers.append(ModelReadiness(model_id, True, tuple(blockers)))
    return tuple(answers)


def preflight_selected_models(
    manifest_path: Path = SELECTED, source_path: Path = SOURCE_V2,
) -> tuple[ModelReadiness, ...]:
    return validate_selected_manifest(
        load_selected_models(manifest_path),
        json.loads(source_path.read_text(encoding="utf-8")),
    )


def require_full_six_model_readiness(
    reports: tuple[ModelReadiness, ...],
) -> None:
    """Forbid silently dropping large or gated models from a claimed 6-model run."""
    if len(reports) != 6 or any(not x.runnable for x in reports):
        blocked = [(x.model_id, x.blockers) for x in reports if not x.runnable]
        raise ValueError(f"six-model experiment BLOCKED: {blocked}")


if __name__ == "__main__":
    reports = preflight_selected_models()
    print("SELECTED_STUDY_MODELS=6; INFERENCE_EXECUTED=0")
    for x in reports:
        print(f"{x.model_id}: BLOCKED ({', '.join(x.blockers)})")
