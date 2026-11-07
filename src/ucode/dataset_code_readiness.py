"""Cross-ledger readiness audit of all 13 U-CODE external source leads.

This audits a *catalog*, a historical 120-PR metadata release and first-party
code scaffolding—not downloaded datasets, safe third-party repository builds,
external review, gold patches or real model inference. All authorizations
remain explicitly false. The current six-model/eight-policy registration is
authoritative; configs/experiment_matrix.json is a historical, incompatible
seven-arm/four-budget sketch, never executable experiment configuration.

No remote fetch, Docker, model imports, GPU calls or oracle access.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from scripts.audit_dataset_cohort_crosswalk import (
    RAW,CLEAN,SOURCES,LEGACY,SUMMARY,read_csv,inspect_cohorts,
)
from .pilot_preflight import build_pilot_preflight
from .model_readiness import validate_selected_manifest

ROOT=Path(__file__).resolve().parents[2]

CLASS_ROLES={
    "Naturalistic":"TRACE_AND_AI_AUTHORSHIP_PROVENANCE_RESEARCH_ONLY",
    "Controlled_generation":"REPOSITORY_TASK_CANDIDATE_NOT_ELIGIBLE",
    "Attribution_only":"CODE_AUTHORSHIP_AUXILIARY_NO_FUNCTIONAL_ORACLE",
    "Auxiliary_training":"TRAINING_CANDIDATE_NOT_HELD_OUT_EVALUATION",
    "Efficiency_secondary":"SEPARATE_EFFICIENCY_ENDPOINT_NOT_REPAIR_SUCCESS",
}

# These *specific* warnings are grounded in existing frozen source metadata,
# not evidence that the underlying dataset card/license is permanently valid.
SPECIFIC={
    "SWE-chat":("GATED_ACCESS_AND_POSSIBLE_PII",
                 "Needs user-granted terms and independent privacy review"),
    "SWE-rebench V2":("SINGLE_UPSTREAM_TRAIN_SPLIT_AND_GOLD_PATCHES",
                 "Full published schema contains gold patches/test patches; use only seven-column projection and independently adjudicated split"),
    "SWE-bench":("POSSIBLE_BENCHMARK_OVERLAP",
                 "Cross-repository/fork and task contamination screening is mandatory"),
    "Multi-SWE-bench":("UPSTREAM_RUNNER_NOT_REPRODUCED",
                 "Pin edition, task IDs, per-repository rights and actual runtime"),
    "SWE-PolyBench":("MULTILINGUAL_NOT_ALL_TWELVE_LANGUAGES",
                 "Its published benchmark covers four languages; no twelve-language generalization"),
    "CodeMirage":("RESTRICTIVE_CC_BY_NC_ND",
                 "Dataset card states CC-BY-NC-ND; do not assume derivative redistribution permission"),
    "MultiAIGCD":("PAPER_LINK_NOT_INDEPENDENT_DATASET_AUDIT",
                 "Published article links a public code/data repository; contents and rights still unreviewed"),
    "EffiBench-X":("DIFFERENT_TASK_GRAIN",
                 "No pooling execution-time efficiency outcomes with repository patch correctness"),
}
SOURCE_NAMES=(
    "AIDev","SWE-chat","DroidCollection","SWE-rebench V2",
    "SWE-bench","Multi-SWE-bench","SWE-PolyBench","EffiBench-X",
    "CodeMirage","MultiAIGCD","NextCoderDataset-Conversational",
    "OpenCodeReasoning-2","OpenCodeGeneticInstruct",
)
SOURCE_FILE_MAP={
    "metadata_intake_and_quality":(
        "scripts/audit_dataset_quality.py",
        "src/ucode/dataset_quality.py",
        "tests/test_dataset_quality.py",
    ),
    "thirteen_source_cohort_crosswalk":(
        "scripts/audit_dataset_cohort_crosswalk.py",
        "tests/test_dataset_cohort_crosswalk.py",
    ),
    "restricted_external_parquet_intake":(
        "src/ucode/external_dataset_intake.py",
        "tests/test_external_dataset_intake.py",
    ),
    "source_era_task_admission":(
        "src/ucode/task_admission.py",
        "src/ucode/pilot_preflight.py",
        "tests/test_pilot_preflight.py",
    ),
    "independent_review_signature_integrity":(
        "src/ucode/external_admission_receipt.py",
        "tests/test_external_admission_receipt.py",
    ),
    "evaluator_boundary":(
        "src/ucode/evaluator_boundary.py",
        "src/ucode/experiment_contract.py",
        "tests/test_experiment_contract.py",
    ),
    "model_readiness":(
        "src/ucode/model_readiness.py",
        "tests/test_model_readiness.py",
    ),
    "synthetic_evidence_and_search":(
        "src/ucode/conditional_bes.py",
        "src/ucode/joint_frequency_controls.py",
        "tests/test_joint_frequency_controls.py",
    ),
    "sandbox_preflight_only":(
        "src/ucode/oci_sandbox_preflight.py",
        "scripts/smoke_oci_sandbox_preflight.py",
    ),
    "prospective_paper_source":(
        "paper/overleaf/main.tex",
        "paper/overleaf/references.bib",
        "scripts/audit_overleaf_sources.py",
    ),
}

REGISTRY_PATH="configs/confirmatory_sbse_protocol_2026-10-25.json"
MODEL_PATH="configs/accepted_six_model_study_2026-10-25.json"
LEGACY_PATH="configs/experiment_matrix.json"
METADATA_PATH="data/curated/2026-10-27/frozen_cleaning_summary.json"


def _json(root:Path,relative:str)->dict:
    obj=json.loads((root/relative).read_text(encoding="utf-8"))
    if type(obj) is not dict:
        raise ValueError("expected canonical dict at "+relative)
    return obj


def audit_dataset_code_readiness(
    root:Path=ROOT, *, external=None, raw=None, curated=None,
    legacy_sources=None, summary=None, protocol=None, selected=None,
    legacy_matrix=None, pilot=None,
)->dict:
    """Derive current stage; reject false promotions and contradictory rosters.

    Overridden inputs are intended for adversarial synthetic unit tests.
    This is deliberately a read-only gate; it has no path that can mark
    a dataset ready for an independently verified real trial.
    """
    root=Path(root)
    ext=read_csv(root/("data/discovery/dataset_source_registry_v2_2026-10-24.csv")) if external is None else external
    raw=read_csv(root/("data/discovery/agent_pr_candidates_120.csv")) if raw is None else raw
    curated=read_csv(root/("data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv")) if curated is None else curated
    old=read_csv(root/("data/discovery/dataset_source_registry.csv")) if legacy_sources is None else legacy_sources
    hist=_json(root,METADATA_PATH) if summary is None else summary
    proto=_json(root,REGISTRY_PATH) if protocol is None else protocol
    model=_json(root,MODEL_PATH) if selected is None else selected
    historical=_json(root,LEGACY_PATH) if legacy_matrix is None else legacy_matrix
    preflight=build_pilot_preflight(root) if pilot is None else pilot
    cohort=inspect_cohorts(raw,curated,ext,old,hist)
    if (tuple(r["dataset"] for r in ext)!=SOURCE_NAMES
            or len({r["primary_url"] for r in ext})!=13):
        raise ValueError("thirteen-source catalog identity/order/url drift")
    if any(r["distinct_cohort"] not in CLASS_ROLES or
           r["local_execution"]!="not_executed" for r in ext):
        raise ValueError("catalog may not self-certify downstream code execution")
    if (proto.get("status")!="PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"
        or proto.get("model_count")!=6
        or len(proto.get("policy_ids",[]))!=8
        or len(set(proto["policy_ids"]))!=8
        or proto.get("primary_treatment")!="ucode_conditional_bes"
        or proto.get("primary_comparator")!="no_uncertainty_search"
        or proto.get("qualified_task_ids")!=[]
        or proto.get("results_measured") is not False
        or proto.get("external_code_executions")!=0
        or proto.get("runner_isolated_and_attested") is not False
        or proto.get("independent_oracles_sealed") is not False
        or proto.get("model_revisions_frozen") is not False):
        raise ValueError("frozen six-model/eight-policy real-study protocol drift")
    models=model.get("models")
    if (model.get("model_count")!=6 or type(models) is not list
        or len(models)!=6
        or [x.get("model_id") for x in models]!=proto.get("model_ids")):
        raise ValueError("six-model planning crosswalk drift")
    readiness=validate_selected_manifest(
        model,_json(root,"configs/models_v2_2026-10-24.json"))
    if any(x.runnable for x in readiness) or any(
            x.get("checkpoint_revision") is not None or
            x.get("tokenizer_revision") is not None or
            x.get("inference_execution_status")!="NOT_RUN" or
            x.get("independently_verified_task_runs")!=0 for x in models):
        raise ValueError("unverified model checkpoint, inference or license promotion")
    if (preflight.get("candidate_count")!=2
        or [r.get("candidate_id") for r in preflight.get("candidates",[])]!=[43,104]
        or preflight.get("pending_admission_checks")!=16
        or preflight.get("qualified_executable_tasks")!=0
        or preflight.get("independent_hidden_oracles_sealed")!=0
        or preflight.get("real_model_runs")!=0
        or preflight.get("drpa_real_task_evaluations")!=0
        or preflight.get("confirmed_primary_effect") is not None):
        raise ValueError("pilot evidence was incorrectly promoted")
    if (historical.get("schema_version")!="1.0"
        or historical.get("state")!="PLANNED_NOT_EXECUTED"
        or type(historical.get("arms")) is not list
        or type(historical.get("budget_constraints")) is not list):
        raise ValueError("legacy experiment sketch changed/was incorrectly promoted")
    changed_arm_count=(len(historical["arms"])!=len(proto["policy_ids"]))
    changed_budget_count=(
        len(historical["budget_constraints"])!=
        len(proto["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"]))
    name_drift=set(historical["arms"])!=set(proto["policy_ids"])
    if not (changed_arm_count and changed_budget_count and name_drift):
        raise ValueError("legacy experiment sketch changed; re-audit authority before reuse")
    # A legacy file can only be reported as NOT authoritative; no runner may
    # auto-import its policy IDs or resource ceilings.
    rows=[]
    for item in ext:
        name=item["dataset"]
        warning,detail=SPECIFIC.get(name,(
            "UNVERIFIED_SOURCE_ACCESS_RIGHTS_AND_TASK_GRAIN",
            "Dataset has no independently verified task-level release or run"))
        rows.append({
            "dataset":name,
            "catalog_cohort":item["distinct_cohort"],
            "candidate_role":CLASS_ROLES[item["distinct_cohort"]],
            "source_url":item["primary_url"],
            "catalog_access_claim_not_live_attested":item["access_state"],
            "catalog_rights_claim_not_independently_approved":item["license_rights"],
            "catalog_oracle_claim_not_independently_replayed":item["oracle_status"],
            "source_specific_risk_code":warning,
            "source_specific_risk_note":detail,
            "local_data_snapshot_proven":False,
            "source_revision_proven":False,
            "independent_file_reuse_rights_approved":False,
            "independent_oracle_reproduced":False,
            "repository_family_split_adjudicated":False,
            "physical_runner_and_meters_attested":False,
            "qualified_executable_task_count":0,
            "source_executed":False,
            "can_supply_primary_confirmatory_effect":False,
            "status":"CATALOG_ONLY_NEEDS_EXTERNAL_ACCESS_RIGHTS_ORACLE_AND_RUNNER",
        })
    modules=[]
    for component,paths in SOURCE_FILE_MAP.items():
        for p in paths:
            file=root/p
            if not file.is_file() or file.is_symlink():
                raise ValueError("missing or unsafe first-party scaffold: "+p)
        modules.append({
            "component":component,"first_party_files":list(paths),
            "files_present":True,
            "real_end_to_end_experiment_qualified":False,
            "note":"First-party paths/tests present; no external task or trusted runner execution proven",
        })
    return {
        "schema_version":"1.0",
        "stage":"ALL_THIRTEEN_SOURCES_CATALOG_ONLY_REAL_EXPERIMENT_BLOCKED",
        "dataset_catalog_count":13,
        "cohort_counts":cohort["source_catalog_cohorts"],
        "public_discovery_metadata":{
            "pr_links":120,"retrieved_pr_metadata":119,
            "production_path_leads":62,
            "shortlisted_reviewer_packets":12,
            "metadata_identity_reconciliation_passed":True,
            "qualified_executable_tasks":0,
        },
        "per_dataset":rows,
        "dataset_snapshot_count_independently_verified":0,
        "dataset_rights_filelevel_approved_count":0,
        "independent_oracle_replay_count":0,
        "pilot":{"source_era_candidates":2,"admission_gates_pending":16,
                 "admission_gates_total":16,"qualified_tasks":0},
        "models":{"planned":6,"qualified_checkpoint_revisions":0,
                  "real_model_runs":0},
        "confirmatory_design":{
            "authoritative_source":REGISTRY_PATH,
            "planned_policy_ids":list(proto["policy_ids"]),
            "registered_policy_slots":8,
            "real_end_to_end_faithful_policy_arms":0,
            "primary_treatment":proto["primary_treatment"],
            "primary_comparator":proto["primary_comparator"],
            "resource_dimensions":list(proto["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"]),
            "verified_real_primary_effect":None,
        },
        "legacy_experiment_matrix_warning":{
            "file":LEGACY_PATH,"status":"HISTORICAL_INCOMPATIBLE_NOT_EXECUTABLE_AUTHORITY",
            "old_policy_arm_count":len(historical["arms"]),
            "authoritative_policy_arm_count":len(proto["policy_ids"]),
            "old_resource_dimensions":len(historical["budget_constraints"]),
            "authoritative_resource_dimensions":len(proto["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"]),
            "policy_names_mismatched":name_drift,
            "never_use_for_confirmatory_experiment":True,
        },
        "code_readiness":{
            "first_party_component_groups_inspected":len(modules),
            "source_scaffolds_present":len(modules),
            "qualified_real_end_to_end_groups":0,
            "components":modules,
            "automatic_python_unit_test_pass_claimed_by_this_script":False,
        },
        "source_integrity_sha256":{
            p:sha256((root/p).read_bytes()).hexdigest()
            for p in (REGISTRY_PATH,MODEL_PATH,LEGACY_PATH,
                      METADATA_PATH,"data/discovery/dataset_source_registry_v2_2026-10-24.csv")
        },
        "disclosures":{
            "not_a_live_check_of_all_external_hosts":True,
            "not_a_local_data_disk_inventory":True,
            "no_external_code_executions":True,
            "no_actual_outcome_labels":True,
            "no_cross_dataset_task_join_proven":True,
            "no_overleaf_cloud_sync_or_pdf_compile":True,
        },
        "warning":"All 13 entries are source leads, not approved datasets. Passing local tests verifies code invariants, not real performance, rights or evaluator isolation.",
    }


def readiness_markdown(report:dict)->str:
    if (report.get("stage")!="ALL_THIRTEEN_SOURCES_CATALOG_ONLY_REAL_EXPERIMENT_BLOCKED"
        or report.get("confirmatory_design",{}).get("verified_real_primary_effect") is not None):
        raise ValueError("refuse to publish an unverified real benchmark-effect claim")
    lines=[
        "# U-CODE: all 13 dataset sources and code readiness",
        "",
        "**Scope:** GitHub frozen registry, local source/data schema, structural first-party "
        "code presence and blocked pilot gate. **No download, no model inference, no "
        "physical sandbox and no sealed oracle replay.**",
        "",
        "| Source | Use only as | Main blocking risk | Executable tasks approved |",
        "|---|---|---|---:|",
    ]
    for r in report["per_dataset"]:
        lines.append("| ["+r["dataset"]+"]("+r["source_url"]+") | "+
          r["catalog_cohort"].replace("_"," ")+" | "+
          r["source_specific_risk_code"].replace("_"," ")+" | 0 |")
    legacy=report["legacy_experiment_matrix_warning"]
    lines+= [
        "",
        "## Validated local code and experimental safety",
        "",
        f"- **{report['dataset_catalog_count']}** external source catalog entries; "
        "**zero** independently staged, rights-cleared, oracle-qualified "
        "executable task cohorts.",
        "- **120** PR discovery links, **119** retrieved metadata records, "
        "**62** production path leads, **12** reviewer screening leads. "
        "**0** independently executable tasks.",
        "- **16/16** open independent admission checks across PHP #104 and Go #43.",
        "- **6** models prospectively chosen, **0** qualified model revisions.",
        "- **8** registered policy slots, **0** real fully validated agent comparisons.",
        f"- **{report['code_readiness']['source_scaffolds_present']}** "
        "first-party pipeline component groups have source/test scaffolds; "
        "they are not proof of all dependencies, runtime isolation or full policy fidelity.",
        "",
        "## Serious configuration hazard: historical seven-arm experiment sketch",
        "",
        f"The old `{legacy['file']}` contains "
        f"**{legacy['old_policy_arm_count']}** policy arms and "
        f"**{legacy['old_resource_dimensions']}** budget fields. "
        "The authoritative immutable registration contains "
        f"**{legacy['authoritative_policy_arm_count']}** policy slots and "
        f"**{legacy['authoritative_resource_dimensions']}** measured resource dimensions.",
        "Do not run the old sketch or silently replace the preregistered design. "
        "The correct primary contrast is `ucode_conditional_bes` versus "
        "`no_uncertainty_search`; existing primary outcomes remain N/A.",
        "",
        "## Prerequisite before saying a dataset is ready",
        "",
        "1. Independently approve source-era task spec and exact file-level rights, "
        "and isolate post-PR patches and evaluator-only gold.",
        "2. Obtain an immutable, reproducible **local** source snapshot with "
        "content digest, changed-file language and actual repair-task grain.",
        "3. Enforce repository/fork ancestry and cross-dataset contamination "
        "checks before assigning train/validation/evaluation folds.",
        "4. Independently author/seal or reproduce hidden correctness oracles, "
        "run only inside a securely reviewed sandbox.",
        "5. Pin licenses, versions, six model checkpoints/tokenizers and five "
        "physical resource meters before the matched eight-arm study.",
        "",
        "The public source registry should never contain private credentials, "
        "reviewer evidence, repository code or oracle labels. Use a private "
        "separately attested release to demonstrate those approvals.",
        "",
    ]
    return "\n".join(lines)
