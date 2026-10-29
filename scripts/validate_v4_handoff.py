"""Source-only V4 new-chat handoff audit against frozen actual registries.

A structural consistency check, NOT authenticated live GitHub verification,
independent human task admission, real model execution or Springer PDF review.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/ucode_handoff_v4_2026-10-29.json"

def audit_v4_handoff(record: dict, *, root: Path = ROOT) -> dict:
    if not isinstance(record, dict) or record.get("schema_version") != "1.0":
        raise ValueError("V4 handoff requires schema version 1.0")
    if record.get("stage") != "HANDOFF_ONLY_NO_NEW_REAL_TRIAL":
        raise ValueError("V4 handoff is not an experimental report")
    if (record.get("repository") != "Rocky5502/U-CODE" or
        record.get("latest_scientific_pr_in_baseline") != 21):
        raise ValueError("V4 repository or historic sprint baseline drift")
    if (record.get("baseline_verified_main_sha") !=
            "56bf2e8ff31edb250e9d5f9cbc2219ddab235527" or
        record.get("baseline_verified_ci_run_id") != 40834818493 or
        record.get("baseline_ci_conclusion") != "success" or
        record.get("offline_tests_per_python_version") != 1115 or
        record.get("python_versions") != ["3.10", "3.12"]):
        raise ValueError("V4 recorded baseline is not the verified original snapshot")
    if record.get("status_must_be_rechecked_on_next_chat") is not True:
        raise ValueError("historic CI is not current CI for future commits")
    roles = [f"R{x}" for x in range(17)]
    if (record.get("original_expert_roles_count") != len(roles) or
        record.get("original_expert_roles") != roles):
        raise ValueError("missing original canonical R0-R16 roles")
    path = record.get("document")
    if path != "docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md":
        raise ValueError("wrong canonical V4 startup document")
    handoff = (root / path).read_text("utf-8")
    for item in [
        "COPY/PASTE ACTIVATION", "R0 Executive PI",
        "R16 Associate/Meta-Reviewer", "P0-1", "P0-2", "P0-3",
        "P0-4", "P1-9", "120", "119", "62", "12",
        "1,115", "NO real", "no measured",
        "evaluator-only", "Overleaf", "A100", "2027",
        "RQ5 generalization", "RQ6 mechanistic",
    ]:
        if item.casefold() not in handoff.casefold():
            raise ValueError("V4 Markdown lost essential handoff element: " + item)
    for role in roles:
        if not re.search(r"\b"+role+r"\b", handoff):
            raise ValueError("missing role in human-readable handoff: " + role)
    for other in ("supersedes_startup_document", "source_registry", "study_registry"):
        linked = record.get(other)
        if not isinstance(linked, str) or not (root / linked).is_file():
            raise ValueError("missing linked historical or protocol source")
    source = json.loads((root / record["source_registry"]).read_text("utf-8"))
    protocol = json.loads((root / record["study_registry"]).read_text("utf-8"))
    evidence = record.get("observed_dataset")
    if not isinstance(evidence, dict):
        raise ValueError("V4 missing data evidence manifest")
    reference = source["source_data"]
    expected = {
        "discovered_pr_links":reference["discovered_pr_links"],
        "pr_metadata_retrieved":reference["pr_metadata_retrieved"],
        "search_language_strata":reference["language_search_strata"],
        "production_source_path_leads":reference["production_source_path_leads"],
        "first_pass_metadata_leads":reference["first_pass_manual_review_leads"],
        "manual_review_leads":reference["manual_shortlist"],
        "independently_approved_executable_tasks":reference["qualified_executable_tasks"],
        "independent_functional_oracles":reference["independent_functional_oracles"],
    }
    if evidence != expected or evidence["independently_approved_executable_tasks"] != 0:
        raise ValueError("V4 data counters differ from audited existing source")
    study = record.get("prospective_study")
    if not isinstance(study, dict):
        raise ValueError("V4 study manifest missing")
    criteria = {
        "model_names_count":len(protocol["model_ids"]),
        "policy_slots_count":len(protocol["policy_ids"]),
        "primary_treatment":protocol["primary_treatment"],
        "primary_comparator":protocol["primary_comparator"],
        "real_model_inferences_verified":source["models"]["real_inference_runs_verified"],
        "real_policy_effects_measured":source["study"]["real_policy_effects_measured"],
        "model_revisions_frozen":protocol["model_revisions_frozen"],
        "runner_security_attested":protocol["runner_isolated_and_attested"],
        "live_overleaf_synced":source["paper"]["external_live_overleaf_project_synced"],
        "compiled_springer_pdf_reviewed":source["paper"]["actual_springer_pdf_compiled_and_inspected"],
    }
    if study != criteria or study["real_policy_effects_measured"] != 0:
        raise ValueError("V4 proposed study incorrectly promoted to a real experiment")
    if record.get("five_resource_fields") != source["study"]["resource_vector"]:
        raise ValueError("V4 lost a resource dimension")
    if "P0-1" not in record.get("priority_first_unblocked_sprint", ""):
        raise ValueError("V4 lost the independently qualified task/oracle priority")
    # These are the real existing source files V4 points to. Validate files
    # exist, but do not mistake existence for task approvals or measured data.
    paths = [
        "src/ucode/postterminal_accounting.py",
        "src/ucode/oci_sandbox_preflight.py",
        "src/ucode/release_semantics.py",
        "src/ucode/conditional_bes_public_replay.py",
        "src/ucode/uncertainty_only_reference.py",
        "scripts/smoke_postterminal_accounting.py",
        "paper/overleaf/main.tex",
        "paper/overleaf/references.bib",
        "docs/UCODE_MASTER_SUPERPROMPT_2026-10-24.md",
    ]
    if any(not (root / p).is_file() for p in paths):
        raise ValueError("V4 points to unmaterialized essential prior work")
    return {
        "status":"V4_HANDOFF_STRUCTURALLY_CONSISTENT_NOT_LIVE_VERIFIED",
        "baseline_ci_run_id":record["baseline_verified_ci_run_id"],
        "baseline_tests_per_version":record["offline_tests_per_python_version"],
        "virtual_roles":len(roles),
        "pr_discovery_records":evidence["discovered_pr_links"],
        "independently_admitted_tasks":0,
        "actual_model_experiments":0,
        "real_effectiveness_measured":0,
        "new_main_ci_must_be_rechecked":True,
    }

def main():
    data = json.loads(MANIFEST.read_text("utf-8"))
    print(json.dumps(audit_v4_handoff(data), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
