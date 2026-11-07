"""Offline integrity check for the dated V5 U-CODE research handoff.

Historical consistency only: NOT independent approval, live CI verification,
source rights, sealed oracle, model inference, sandbox attestation, or peer review.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/ucode_handoff_v5_2026-11-07.json"


def audit_v5_handoff(record: dict | None = None, document: str | None = None,
                     *, root: Path = ROOT) -> dict:
    if record is None:
        record = json.loads((root / "configs/ucode_handoff_v5_2026-11-07.json").read_text("utf-8"))
    if not isinstance(record, dict) or record.get("schema_version") != "1.0":
        raise ValueError("V5 requires a versioned immutable handoff snapshot")
    if (record.get("stage") != "SOURCE_ONLY_HANDOFF_NO_REAL_EXPERIMENT"
            or record.get("repository") != "Rocky5502/U-CODE"
            or record.get("snapshot_date_utc") != "2026-11-07"):
        raise ValueError("V5 date, repository or source-only stage drift")
    if (record.get("snapshot_main_sha") != "0059e8fedfba6c0dfb198a79f44452548192cf1a"
            or record.get("snapshot_merged_pr") != 53
            or record.get("snapshot_postmerge_ci_run") != 42368901886
            or record.get("snapshot_ci_outcome") != "success"
            or record.get("snapshot_python_versions") != ["3.10", "3.12"]
            or record.get("snapshot_first_party_tests_each") != 1515
            or record.get("history_must_be_refreshed_on_resume") is not True):
        raise ValueError("V5 historical GitHub evidence changed or misrepresented as evergreen")
    if record.get("virtual_roles") != [f"R{i}" for i in range(17)]:
        raise ValueError("V5 canonical R0–R16 role roster drift")
    if (record.get("pending_php_go_admission_gates") != 16
            or record.get("independently_admitted_tasks") != 0
            or record.get("sealed_functional_oracles") != 0
            or record.get("qualified_model_checkpoints") != 0
            or record.get("real_policy_effects") != 0
            or record.get("major_scientific_exit_criteria_incomplete") != 10
            or record.get("live_overleaf_sync_not_established") is not True):
        raise ValueError("V5 fabricated admission, oracle, model, results or journal-readiness status")
    expected_paths = {
        "document": "docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V5_2026-11-07.md",
        "retains_historical_v4": "docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md",
        "registered_protocol": "configs/confirmatory_sbse_protocol_2026-10-25.json",
        "scientific_critical_path": "docs/UCODE_PROGRESS_CRITICAL_PATH_2026-11-07.md",
        "source_era_go_review": "docs/G5_GO43_SOURCE_ERA_ORACLE_REVIEW_2026-11-07.md",
    }
    for key, expected in expected_paths.items():
        if record.get(key) != expected or not (root / expected).is_file():
            raise ValueError("V5 canonical research source path missing or redirected: " + key)
    exact_blobs = {
        "original_go_base": "ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a",
        "original_go_design_blob": "b566ca7627b6518670a866a6a637bd5257e947f4",
        "original_go_business_rules_blob": "e71288e3127cb66f2471a5ddd2800092db0552cc",
    }
    for key, value in exact_blobs.items():
        if record.get(key) != value:
            raise ValueError("V5 original-source identity was modified: " + key)
    protocol = json.loads((root / record["registered_protocol"]).read_text("utf-8"))
    if (record.get("confirmatory_model_count") != len(protocol["model_ids"])
            or record.get("confirmatory_policy_count") != len(protocol["policy_ids"])
            or len(protocol["model_ids"]) != 6 or len(protocol["policy_ids"]) != 8
            or protocol["primary_treatment"] != "ucode_conditional_bes"
            or protocol["primary_comparator"] != "no_uncertainty_search"
            or protocol["results_measured"] is not False):
        raise ValueError("V5 frozen six-model/eight-arm primary comparison drift")
    if document is None:
        document = (root / record["document"]).read_text("utf-8")
    role_lines = document.splitlines()
    for role in record["virtual_roles"]:
        if not any(line.startswith("| **" + role + " —") for line in role_lines):
            raise ValueError("V5 human-readable role missing: " + role)
    required = [
        "START — COPY/PASTE INTO A NEW CHAT",
        "END — COPY/PASTE INTO A NEW CHAT",
        "P0-1", "P0-2", "P0-3", "P0-4",
        "P1-5", "P1-6", "P1-7", "P1-8", "P1-9", "P2-10",
        "16/16", "1,515", "42368901886", "0059e8f",
        "independent", "not gold outputs", "Go #43", "PHP #104",
        "Overleaf", "R0–R16", "reviewer", "no fabricated",
        "five hard", "ITT", "main.tex",
    ]
    for item in required + list(exact_blobs.values()) + protocol["model_ids"] + protocol["policy_ids"]:
        if item.casefold() not in document.casefold():
            raise ValueError("V5 required evidence or protocol content missing: " + item)
    for component in ["tokens", "test_calls", "gpu_seconds", "cpu_seconds", "wall_seconds"]:
        if component not in document:
            raise ValueError("V5 missing independent resource dimension: " + component)
    readme = (root / "README.md").read_text("utf-8")
    historical = (root / record["retains_historical_v4"]).read_text("utf-8")
    if ("UCODE_NEW_CHAT_MASTER_HANDOFF_V5_2026-11-07.md" not in readme
            or "UCODE_NEW_CHAT_MASTER_HANDOFF_V5_2026-11-07.md" not in historical):
        raise ValueError("V5 navigation must appear in README and historical V4")
    return {
        "status": "V5_HANDOFF_STRUCTURALLY_VALID_NOT_INDEPENDENT_ADMISSION",
        "dated_main_sha": record["snapshot_main_sha"],
        "dated_ci_run": record["snapshot_postmerge_ci_run"],
        "dated_offline_tests_per_python_version": record["snapshot_first_party_tests_each"],
        "virtual_review_perspectives_not_real_reviewers": 17,
        "remaining_php_go_independent_gates": 16,
        "independently_admitted_tasks": 0,
        "measured_real_effects": 0,
        "recheck_live_github_and_ci": True,
    }


def main() -> None:
    print(json.dumps(audit_v5_handoff(), indent=2, sort_keys=True))
    print("Historical offline consistency only: query current GitHub, independent approvals and live Overleaf separately.")


if __name__ == "__main__":
    main()
