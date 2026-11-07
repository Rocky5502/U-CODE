"""Evidence-linked U-CODE research critical path (PUBLIC metadata ONLY).

This is a conservative *delivery dependency audit*, NOT a percent-complete
project manager, time forecast, statistical inference, or an authorization
to run third-party code. A source file existing means source scaffolding
exists; it does not demonstrate an executable benchmark, secured runner,
trained model or scientifically qualified policy.

The 10 major milestones are sourced from the historical planning register,
but scientific completion is checked against the CURRENT frozen
protocol, six-model plan and cross-ledger PHP/Go preflight. The historical
workstream statuses are NOT treated as current evidence of completion.

Deliberately fails closed if any input self-promotes to real-task execution
or empirical performance unsupported by this source-only report.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from .model_readiness import validate_selected_manifest
from .pilot_preflight import build_pilot_preflight

ROOT=Path(__file__).resolve().parents[2]
IDS=("P0-1","P0-2","P0-3","P0-4",
     "P1-5","P1-6","P1-7","P1-8","P1-9","P2-10")

# These are planning dependencies, NOT elapsed-time or causality estimates.
# P0 workstreams can be prepared in parallel; their independently checked
# exit criteria are required for downstream empirically defensible results.
DEPENDS={
    "P0-1":(),
    "P0-2":(),
    "P0-3":(),
    "P0-4":(),
    "P1-5":("P0-1","P0-3"),
    "P1-6":("P0-2","P0-3","P0-4"),
    "P1-7":("P0-1","P0-2"),
    "P1-8":("P1-5","P1-6","P1-7"),
    "P1-9":("P1-8",),
    "P2-10":("P1-9",),
}

# Confirm exactly these first-party files exist; never claim they are
# independently audited or complete implementations of a study arm.
REFERENCE_FILES={
    "P0-1":("src/ucode/task_admission.py","src/ucode/pilot_preflight.py",
             "scripts/audit_private_review_forms.py"),
    "P0-2":("src/ucode/oci_sandbox_preflight.py",),
    "P0-3":("src/ucode/model_readiness.py",),
    "P0-4":("src/ucode/conditional_bes.py","src/ucode/joint_validity_acquisition.py"),
    "P1-5":("src/ucode/joint_frequency_fit.py",),
    "P1-6":("src/ucode/shadow_eight_arm_runner.py","src/ucode/joint_frequency_controls.py"),
    "P1-7":("src/ucode/lineage_risk_graph.py",),
    "P1-8":("src/ucode/experiment_contract.py",),
    "P1-9":("paper/overleaf/main.tex","paper/overleaf/references.bib"),
    "P2-10":("scripts/verify_dataset_release.py",),
}
_PRIORITY_ORDER=("P0","P1","P2")
_PROVENANCE_FILES=(
    "configs/confirmatory_sbse_protocol_2026-10-25.json",
    "configs/accepted_six_model_study_2026-10-25.json",
    "configs/ucode_work_remaining_gates_2026-10-27.json",
    "data/curated/2026-10-27/frozen_cleaning_summary.json",
)


def _object(root: Path, path: str) -> dict:
    obj=json.loads((root/path).read_text(encoding="utf-8"))
    if type(obj) is not dict:
        raise ValueError("expected a JSON object at "+path)
    return obj


def _dependencies() -> dict[str,int]:
    """Validate DAG and count milestone edges along longest upstream chain."""
    if set(DEPENDS)!=set(IDS) or set(REFERENCE_FILES)!=set(IDS):
        raise ValueError("critical path source code does not cover 10 registered milestones")
    state={}
    levels={}
    def visit(node):
        if state.get(node)==1:
            raise ValueError("cyclic milestone dependency graph")
        if state.get(node)==2:
            return levels[node]
        if node not in DEPENDS:
            raise ValueError("unknown milestone dependency")
        state[node]=1
        for dep in DEPENDS[node]:
            if dep not in DEPENDS or dep==node:
                raise ValueError("unknown/self milestone dependency")
            visit(dep)
        levels[node]=1+max((levels[d] for d in DEPENDS[node]),default=0)
        state[node]=2
        return levels[node]
    for node in IDS:
        visit(node)
    return levels


def _longest_chain(levels: Mapping[str,int]) -> tuple[str,...]:
    end=max(IDS,key=lambda x:(levels[x],-IDS.index(x)))
    path=[end]
    while DEPENDS[end]:
        end=max(DEPENDS[end],key=lambda x:(levels[x],-IDS.index(x)))
        path.append(end)
    return tuple(reversed(path))


def build_critical_path(
    root: Path = ROOT, *,
    pilot: dict | None = None,
    protocol: dict | None = None,
    selected: dict | None = None,
    gate_register: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    """Combine independently versioned metadata; do not invent completeness.

    This source-only command recognizes only the CURRENT not-admitted study
    stage. A later independently approved phase requires a different,
    externally authenticated readiness contract rather than merely toggling
    flags in a JSON file. Input overrides are for adversarial unit tests.
    """
    root=Path(root)
    p=protocol if protocol is not None else _object(
        root,"configs/confirmatory_sbse_protocol_2026-10-25.json")
    s=selected if selected is not None else _object(
        root,"configs/accepted_six_model_study_2026-10-25.json")
    g=gate_register if gate_register is not None else _object(
        root,"configs/ucode_work_remaining_gates_2026-10-27.json")
    m=metadata if metadata is not None else _object(
        root,"data/curated/2026-10-27/frozen_cleaning_summary.json")
    prep=pilot if pilot is not None else build_pilot_preflight(root)
    if any(type(x) is not dict for x in (p,s,g,m,prep)):
        raise TypeError("typed canonical registry dictionaries required")
    if (p.get("status")!="PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"
            or p.get("qualified_task_ids")!=[]
            or p.get("independent_oracles_sealed") is not False
            or p.get("runner_isolated_and_attested") is not False
            or p.get("model_revisions_frozen") is not False
            or p.get("policy_implementations_faithfully_reproduced") is not False
            or p.get("results_measured") is not False
            or p.get("external_code_executions")!=0
            or p.get("seeds_frozen") is not False
            or p.get("final_budget_caps_frozen") is not False):
        raise ValueError("cannot report promoted/unverified empirical science")
    selected_models=s.get("models")
    if (p.get("model_count")!=6 or len(p.get("model_ids",[]))!=6
            or type(selected_models) is not list or len(selected_models)!=6
            or [x.get("model_id") for x in selected_models]!=p["model_ids"]
            or len(p.get("policy_ids",[]))!=8
            or len(set(p["policy_ids"]))!=8
            or p.get("primary_treatment")!="ucode_conditional_bes"
            or p.get("primary_comparator")!="no_uncertainty_search"):
        raise ValueError("six-model/eight-policy primary protocol drift")
    reports=validate_selected_manifest(
        s,_object(root,"configs/models_v2_2026-10-24.json"))
    if len(reports)!=6 or any(r.runnable for r in reports):
        raise ValueError("model qualification claimed without external attestation")
    if (prep.get("candidate_count")!=2
            or [x.get("candidate_id") for x in prep.get("candidates",[])]!=[43,104]
            or prep.get("pending_admission_checks")!=16
            or prep.get("qualified_executable_tasks")!=0
            or prep.get("real_model_runs")!=0
            or prep.get("independent_hidden_oracles_sealed")!=0
            or prep.get("policy_slots_registered_not_executed")!=8
            or prep.get("model_slots_registered_not_qualified")!=6
            or prep.get("confirmed_primary_effect") is not None
            or prep.get("matched_real_run_matrix_frozen") is not False
            or any(x.get("open_gate_count")!=8
                   or x.get("independently_qualified") is not False
                   or x.get("external_execution_allowed") is not False
                   for x in prep["candidates"])):
        raise ValueError("cross-ledger independent task/model qualification drift")
    for field,number in (
        ("discovered_pr_links",120),("metadata_retrieved",119),
        ("production_source_path_leads",62),
        ("shortlisted_for_manual_review",12),
        ("independently_approved_executable_tasks",0),
    ):
        if m.get(field)!=number:
            raise ValueError("frozen metadata counter changed: "+field)
    if (g.get("source_data",{}).get("qualified_executable_tasks")!=0
            or g.get("models",{}).get("selected_for_planning")!=6
            or g.get("models",{}).get("checkpoints_revision_pinned")!=0
            or g.get("models",{}).get("real_inference_runs_verified")!=0
            or g.get("study",{}).get("confirmatory_policies")!=8
            or g.get("paper",{}).get("results_present_as_real_study") is not False
            or g.get("paper",{}).get("actual_springer_pdf_compiled_and_inspected") is not False
            or g.get("paper",{}).get("external_live_overleaf_project_synced") is not False):
        raise ValueError("historical planning register conflicts with prospective evidence")
    items=g.get("next_work")
    if (type(items) is not list or len(items)!=len(IDS)
            or [x.get("id") for x in items]!=list(IDS)):
        raise ValueError("ten-milestone planning roster drift")
    levels=_dependencies()
    milestones=[]
    for item in items:
        identifier=item["id"]
        phase=identifier.split("-")[0]
        if (item.get("priority")!=phase or phase not in _PRIORITY_ORDER
                or type(item.get("issue")) is not int
                or not str(item.get("title","")).strip()
                or not str(item.get("deliverable","")).strip()
                or not str(item.get("exit_criteria","")).strip()):
            raise ValueError("malformed or relabeled planning milestone")
        # Historical status strings are NOT copied into today's verdict.
        files=REFERENCE_FILES[identifier]
        if any(not (root/f).is_file() or (root/f).is_symlink() for f in files):
            raise ValueError("first-party source-scaffolding file missing")
        milestones.append({
            "id":identifier,"priority":phase,
            "issue_number":item["issue"],"title":item["title"],
            "evidence_needed":item["deliverable"],
            "exit_criterion":item["exit_criteria"],
            "depends_on":list(DEPENDS[identifier]),
            "dependency_depth_in_milestones":levels[identifier],
            "reference_source_files_present":list(files),
            "reference_source_files_are_not_approval":True,
            "scientific_exit_criterion_independently_verified":False,
            "status":"OPEN_EXIT_EVIDENCE_UNVERIFIED",
        })
    block_counts=Counter(b for r in reports for b in r.blockers)
    # This is a report on a verified prospective snapshot, not a time
    # estimate, a velocity projection or a new research performance score.
    return {
        "schema_version":"1.0",
        "stage":"SOURCE_LINKED_CRITICAL_PATH_NO_REAL_RESULTS",
        "deadline_from_registered_call":"2027-01-30",
        "deadline_independently_reverified_by_this_script":False,
        "source_registry_snapshot_date":g.get("snapshot_date"),
        "metadata_discovery":{"pr_leads":120,"retrieved_pr_metadata":119,
                              "production_source_path_leads":62,
                              "prioritized_manual_review_leads":12},
        "independent_pilot_admission":{
            "candidate_ids":[43,104],
            "open_checks":16,"total_checks":16,
            "candidate_count":2,"qualified_executable_tasks":0,
            "independently_sealed_oracles":0,
        },
        "models":{"planned":6,"independently_runnable":0,
                  "checkpoint_revisions_frozen":0,
                  "unique_blocker_categories":dict(sorted(block_counts.items()))},
        "policies":{"registered":8,"faithfully_real_task_verified":0,
                    "real_matched_policy_runs":0},
        "scientific_measurement":{
            "external_code_executions":0,
            "independently_qualified_real_model_runs":0,
            "measured_primary_effect":None,
            "reported_observed_sample_size":None,
        },
        "manuscript":{
            "github_springer_source_present":True,
            "verified_publisher_pdf_compiled":False,
            "external_live_overleaf_synced":False,
            "reported_full_empirical_rq_results":False,
        },
        "milestone_accounting":{
            "total_exit_criteria":len(IDS),
            "independently_verified_complete_exit_criteria":0,
            "still_without_full_exit_evidence":len(IDS),
            "phase_totals":dict(sorted(Counter(x["priority"] for x in milestones).items())),
            "independent_workstreams_possible_now":[x["id"] for x in milestones
                                                    if not x["depends_on"]],
            "other_workstreams_dependent_on_prerequisites":[x["id"] for x in milestones
                                                             if x["depends_on"]],
            "one_longest_dependency_chain":list(_longest_chain(levels)),
            "longest_chain_length_in_milestones":max(levels.values()),
            "overall_percent_complete":None,
            "calendar_time_remaining_estimate":None,
            "interpretation":(
                "Open full scientific exit criteria are NOT a percent-complete "
                "measure of source engineering; dependency depth is NOT elapsed time."
            ),
        },
        "source_record_sha256":{
            name:sha256((root/name).read_bytes()).hexdigest()
            for name in _PROVENANCE_FILES
        },
        "milestones":milestones,
        "warning":(
            "Planning source/first-party CI does not independently authenticate "
            "human reviewers, source rights, hidden oracle, checkpoint weights "
            "or physical sandbox; never authorize external execution from this report."
        ),
    }


def critical_path_markdown(report: dict) -> str:
    if (type(report) is not dict
            or report.get("stage")!="SOURCE_LINKED_CRITICAL_PATH_NO_REAL_RESULTS"
            or report.get("milestone_accounting",{}).get("overall_percent_complete") is not None
            or report.get("scientific_measurement",{}).get("measured_primary_effect") is not None):
        raise ValueError("only source-backed prospective readiness reports allowed")
    a=report["milestone_accounting"]
    data=report["metadata_discovery"]
    pilot=report["independent_pilot_admission"]
    models=report["models"]
    lines=[
        "# U-CODE remaining work — evidence-linked critical path",
        "",
        "> **Prospective scientific work only.** This is a dependency and missing",
        "> evidence audit, not a measured repair gain, risk guarantee, overall",
        "> completion percentage, time estimate or execution authorization.",
        "",
        "## Source-backed scope and experimental gates",
        "",
        "| Evidence unit | Verified current count |",
        "|---|---:|",
        f"| PR discovery links (not runnable tasks) | {data['pr_leads']} |",
        f"| Retrieved metadata records | {data['retrieved_pr_metadata']} |",
        f"| Production source-path leads | {data['production_source_path_leads']} |",
        f"| Shortlisted manual-review leads | {data['prioritized_manual_review_leads']} |",
        f"| PHP/Go pending independent admission gates | {pilot['open_checks']}/{pilot['total_checks']} |",
        f"| Independently admitted executable tasks | {pilot['qualified_executable_tasks']} |",
        f"| Selected open-weight model names | {models['planned']} |",
        f"| Independently runnable/frozen checkpoints | {models['independently_runnable']} |",
        f"| Registered confirmatory policy arms | {report['policies']['registered']} |",
        f"| Faithfully real-task-verified policy arms | {report['policies']['faithfully_real_task_verified']} |",
        f"| Qualified real model runs | {report['scientific_measurement']['independently_qualified_real_model_runs']} |",
        "",
        f"**Major milestone exit criteria:** {a['still_without_full_exit_evidence']} "
        f"of {a['total_exit_criteria']} have not been independently verified as complete.",
        "Some software components and manuscript sections already exist; this",
        "count must **never** be presented as a project completion percentage.",
        "",
        "## Work that can proceed in parallel",
        "",
        ", ".join(a["independent_workstreams_possible_now"]) + ". These are"
        " the four P0 workstreams. Their software preparation can advance now;",
        " independent scientific signoff still depends on external evidence.",
        "",
        "## One longest logical dependency chain",
        "",
        " → ".join(a["one_longest_dependency_chain"]),
        "",
        f"This path has {a['longest_chain_length_in_milestones']} "
        "major milestones. It is **not a critical-path duration estimate**;",
        " some tasks can overlap, and there are multiple equally long chains.",
        "",
        "## Detailed open research milestones",
        "",
        "| Workstream | Priority | Depends on | Missing signoff evidence / acceptance |",
        "|---|---|---|---|",
    ]
    for item in report["milestones"]:
        needed=item["exit_criterion"].replace("|","/")
        lines.append(
            f"| [#{item['issue_number']}](https://github.com/Rocky5502/U-CODE/issues/{item['issue_number']}) "
            f"{item['id']} | {item['priority']} | "
            f"{', '.join(item['depends_on']) or 'parallel'} | {needed} |"
        )
    lines += [
        "",
        "The table describes **full scientific exit criteria**, not the",
        "presence or absence of preliminary code. Reference implementations",
        "exist for each stream; none is external experimental approval.",
        "",
        "## Immediate external handoffs",
        "",
        "1. Independently adjudicate original PHP/Go source-era specifications,",
        "   file-level rights and AI-line authorship, with evaluator-only",
        "   oracle seals. Keep private review evidence outside public CI.",
        "2. Independently verify a network-disabled rootless runner and actual",
        "   token/test/GPU/CPU/wall metering before third-party execution.",
        "3. Review six model licenses/terms, choose immutable weight/tokenizer",
        "   revisions and prove physical inference compatibility.",
        "4. In parallel, finish reproducible agent-control and",
        "   budget-matched eight-policy fidelity audits without oracle leaks.",
        "",
        "After those P0 gates, qualify lineage-disjoint labels, train/calibrate",
        "joint probabilities, run matched ITT comparisons, and populate the",
        "paper only from independently joined terminal evaluator verdicts.",
        "The registered primary contrast is **ucode_conditional_bes** versus",
        "**no_uncertainty_search**, not exploratory DRPA.",
        "",
        f"Registered target submission deadline: **{report['deadline_from_registered_call']}**.",
        "This program does not verify live publisher updates.",
        "",
        "**N/A** is the correct current effect estimate, never 0%.",
        "Live Overleaf synchronization and publisher PDF compilation remain",
        "unverified; GitHub source alone does not satisfy those tasks.",
        "",
    ]
    return "\n".join(lines)
