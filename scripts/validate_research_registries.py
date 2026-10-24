"""Validate *candidate* model/dataset registries without external downloads.

Uses only Python standard library; rejects promotion of a lead to
'approved/runnable' without immutable revision, rights and oracle evidence.
The current inventories intentionally contain no such promotions.
"""
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "configs/models_v2_2026-10-24.json"
DATASETS = ROOT / "data/discovery/dataset_source_registry_v2_2026-10-24.csv"
REQUIRED_DATA_COLUMNS = {
    "dataset", "unit", "primary_url", "access_state", "license_rights",
    "oracle_status", "local_execution", "distinct_cohort", "risk_or_limit",
}
COHORTS = {"Naturalistic", "Controlled_generation", "Attribution_only",
           "Auxiliary_training", "Efficiency_secondary"}


def _https_url(raw: str) -> bool:
    parsed = urlparse(raw)
    return (parsed.scheme == "https" and bool(parsed.netloc)
            and not parsed.username and not parsed.password)


def validate_registries(
    model_path: Path = MODELS, dataset_path: Path = DATASETS
) -> dict[str, int]:
    manifest = json.loads(model_path.read_text(encoding="utf-8"))
    if manifest.get("status") == "APPROVED_FOR_STUDY":
        raise ValueError("candidate registry must not self-attest study approval")
    # The current v2 manifest labels its stage, not a generic status.
    if manifest.get("stage") != "CANDIDATES_NOT_APPROVED_OR_EXECUTED":
        raise ValueError("v2 model registry stage must remain explicitly provisional")
    models = manifest.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("no candidate models")
    ids = set()
    for m in models:
        model_id = m.get("id")
        if not isinstance(model_id, str) or "/" not in model_id or model_id in ids:
            raise ValueError("missing, malformed or duplicate Hugging Face model ID")
        ids.add(model_id)
        if not _https_url(m.get("url", "")):
            raise ValueError("model URL must be HTTPS")
        for key in ("model_revision", "tokenizer_revision", "license_file_revision"):
            if m.get(key) is not None:
                raise ValueError(f"{key} unexpectedly pinned without verified revision")
        if any(m.get(k) is not False for k in
               ("rights_approved", "weights_downloaded", "model_inference_executed",
                "pilot_selected")):
            raise ValueError("candidate model mistakenly promoted to approved/executed")
        if not m.get("memory_gate") or not m.get("license_full_text_review"):
            raise ValueError("missing memory or rights gate")

    with dataset_path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or ()) != REQUIRED_DATA_COLUMNS:
            raise ValueError("dataset registry column schema mismatch")
        rows = list(reader)
    if not rows:
        raise ValueError("dataset registry empty")
    seen = set()
    for item in rows:
        name = item["dataset"]
        if not name or name in seen:
            raise ValueError("blank/duplicate dataset entry")
        seen.add(name)
        if item["distinct_cohort"] not in COHORTS:
            raise ValueError("invalid dataset cohort")
        if not _https_url(item["primary_url"]):
            raise ValueError("dataset source must be HTTPS")
        if item["local_execution"] != "not_executed":
            raise ValueError("unverified benchmark claim disguised as local execution")
        if not item["oracle_status"] or not item["license_rights"]:
            raise ValueError("missing independent oracle or source-license gate")
    return {"models": len(models), "datasets": len(rows)}


if __name__ == "__main__":
    summary = validate_registries()
    print(f"RESEARCH_CANDIDATE_REGISTRIES_VALID models={summary['models']} "
          f"datasets={summary['datasets']} no_model_or_oracle_promotions=true")
