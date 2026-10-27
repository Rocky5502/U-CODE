"""Validate the U-CODE NEW-CHAT handover's evidence ledger, OFFLINE ONLY.

This checks that the frozen handover is internally consistent with the
source-controlled model/protocol/metadata registers at its handoff date.
It does not attest external GitHub CI, authentic human review, live Overleaf,
model inference, independent correctness, source rights or paper readiness.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "configs/ucode_work_remaining_gates_2026-10-27.json"


def validate_handoff_snapshot(register: dict, *, root=ROOT) -> dict:
    if not isinstance(register, dict) or register.get("schema_version") != "1.0":
        raise ValueError("valid research handoff schema required")
    dataset = register.get("source_data")
    if not isinstance(dataset, dict):
        raise ValueError("dataset register missing")
    frozen = json.loads((root / "data/curated/2026-10-27/frozen_cleaning_summary.json").read_text("utf-8"))
    count_map = {
        "discovered_pr_links": "discovered_pr_links",
        "distinct_repository_names": "distinct_repository_names",
        "pr_metadata_retrieved": "metadata_retrieved",
        "production_source_path_leads": "production_source_path_leads",
        "first_pass_manual_review_leads": "first_pass_manual_review_leads",
        "manual_shortlist": "shortlisted_for_manual_review",
        "qualified_executable_tasks": "independently_approved_executable_tasks",
    }
    for register_key, original_key in count_map.items():
        if (type(dataset.get(register_key)) is not int or
                dataset[register_key] != frozen[original_key]):
            raise ValueError("dataset handover count differs from audit: " + register_key)
    if dataset.get("language_search_strata") != 12 or dataset.get(
            "labels_are_query_strata_not_verified_changed_language") is not True:
        raise ValueError("search-language provenance overstated")
    if dataset["executable_original_source_snapshots"] != 0 or dataset["independent_functional_oracles"] != 0:
        raise ValueError("source snapshot unexpectedly self-certified")
    protocol = json.loads((root / register["protocol"]).read_text("utf-8"))
    roster = json.loads((root / "configs/accepted_six_model_study_2026-10-25.json").read_text("utf-8"))
    if (protocol["model_ids"] != [m["model_id"] for m in roster["models"]]
            or register["models"]["selected_for_planning"] != len(protocol["model_ids"]) != 6):
        raise ValueError("model roster differs from selected confirmatory model registry")
    if (register["study"]["confirmatory_policies"] != len(protocol["policy_ids"])
            or register["study"]["primary_treatment"] != protocol["primary_treatment"]
            or register["study"]["primary_control"] != protocol["primary_comparator"]):
        raise ValueError("handed-over study arm mismatches preregistration")
    if (register["models"]["real_inference_runs_verified"] != 0
            or register["study"]["real_policy_effects_measured"] != 0
            or register["paper"]["results_present_as_real_study"] is not False
            or register["paper"]["external_live_overleaf_project_synced"] is not False):
        raise ValueError("uncorroborated new experimental result or live Overleaf sync")
    if register["study"]["resource_vector"] != ["tokens", "test_calls", "gpu_seconds", "cpu_seconds", "wall_seconds"]:
        raise ValueError("not all five resource constraints preserved")
    queue = register.get("next_work")
    if (not isinstance(queue, list) or len(queue) < 9
            or len({w["id"] for w in queue}) != len(queue)):
        raise ValueError("missing or duplicated blocker work packages")
    if not any(w["issue"] == 7 and w["priority"] == "P0" for w in queue):
        raise ValueError("independent task and oracle pilot gate missing")
    for task in queue:
        if task.get("priority") not in ("P0", "P1", "P2") or not 1 <= task.get("issue", -1) <= 7:
            raise ValueError("missing priority or original GitHub issue ID")
        if not task.get("deliverable") or not task.get("exit_criteria"):
            raise ValueError("each uncompleted scientific gate needs explicit acceptance criteria")
    doc = root / "docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V3_2026-10-27.md"
    if not doc.is_file() or "ACTIVATION" not in doc.read_text("utf-8"):
        raise ValueError("activation prompt is not present in Git repo")
    for key in ("canonical_source", "bibliography"):
        if not (root / register["paper"][key]).is_file():
            raise ValueError("canonical manuscript handover file missing")
    return {
        "status": "HANDOFF_SNAPSHOT_STRUCTURAL_CHECK_PASSED_NOT_EMPIRICAL_VALIDATION",
        "verified_snapshot_git_sha": register["snapshot_verified_git_head"],
        "baseline_ci_run_id_not_current_ci_claim": register["snapshot_verified_ci_run_id"],
        "metadata_records": dataset["discovered_pr_links"],
        "query_language_strata": dataset["language_search_strata"],
        "independent_task_admissions": 0,
        "real_model_effects": 0,
        "unresolved_research_work_packages": len(queue),
        "live_overleaf_synced": False,
        "paper_pdf_compiled": False,
    }


def main():
    print(json.dumps(validate_handoff_snapshot(
        json.loads(HANDOFF.read_text("utf-8"))), indent=2, sort_keys=True))
    print("NOTE: this validates a dated handover snapshot; REFRESH LIVE GITHUB HEAD AND CI.")


if __name__ == "__main__":
    main()
