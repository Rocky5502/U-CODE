"""Reproducible, NO-RESULTS U-CODE dataset/study readiness and metric contract.

Do not convert query strata or PR metadata to tasks. All empirical metrics
are None until a separately verified, evaluator-only experiment is supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

METRIC_DEFINITIONS = (
    {
        "id":"verified_full_task_success_itt",
        "unit":"proportion of all assigned task/model/seed/budget cells",
        "numerator":"independently verified successful released task patches",
        "denominator":"all assigned cells for the policy, including abstain and timeout",
        "zero_denominator":"undefined; reject",
        "oracle_required":True,
    },
    {
        "id":"release_coverage",
        "unit":"proportion of all assigned cells",
        "numerator":"assigned cells with a released patch",
        "denominator":"all assigned cells for policy",
        "zero_denominator":"undefined; reject",
        "oracle_required":False,
    },
    {
        "id":"wrong_release_risk",
        "unit":"proportion of released patches",
        "numerator":"released patches failing independently sealed functional oracle",
        "denominator":"released patches with independently joined verdicts",
        "zero_denominator":"null (not zero; no releases)",
        "oracle_required":True,
    },
    {
        "id":"paired_itt_success_difference",
        "unit":"percentage-point difference, treatment minus control",
        "numerator":"sum per-assignment success_treatment - success_control",
        "denominator":"all matched assigned task/model/seed/budget pairs",
        "zero_denominator":"undefined; reject",
        "oracle_required":True,
    },
    {
        "id":"five_resource_realized_cost",
        "unit":"separate tokens, test_calls, gpu_seconds, cpu_seconds, wall_seconds",
        "numerator":"independently measured per-run resource totals",
        "denominator":"per assigned arm/cell; mean by arm may be reported separately",
        "zero_denominator":"undefined; reject",
        "oracle_required":False,
    },
    {
        "id":"infrastructure_failure_sensitivity_bounds",
        "unit":"lower/upper success-effect bounds, not confidence interval",
        "numerator":"worst/best feasible outcomes for unknown infrastructure failures",
        "denominator":"all matched assigned cells",
        "zero_denominator":"undefined; reject",
        "oracle_required":True,
    },
)


@dataclass(frozen=True)
class ReadinessSnapshot:
    data: dict


def build_readiness_snapshot(
    frozen_cleaning: dict, registry: dict, protocol: dict,
    verified_release: dict, source_registry_count: int,
) -> ReadinessSnapshot:
    """Read only real registry/metadata counters, not invented task outcomes."""
    if not all(type(obj) is dict for obj in
               (frozen_cleaning,registry,protocol,verified_release)):
        raise TypeError("typed dictionaries from repository registries required")
    original=frozen_cleaning
    source=registry.get("source_data")
    models=registry.get("models")
    study=registry.get("study")
    paper=registry.get("paper")
    if any(type(x) is not dict for x in (source,models,study,paper)):
        raise ValueError("missing researcher-signed prospective gate summaries")
    for key,value in (
        ("discovered_pr_links",120),("metadata_retrieved",119),
        ("production_source_path_leads",62),
        ("shortlisted_for_manual_review",12),
        ("independently_approved_executable_tasks",0),
    ):
        if original.get(key)!=value:
            raise ValueError("frozen metadata discovery denominator mismatch: "+key)
    semantic=verified_release.get("semantic_audit")
    if not isinstance(semantic,dict):
        raise ValueError("metadata SHA and cross-file semantic audit prerequisite")
    for old,new in (
        ("discovered_pr_links","pr_discovery_rows"),
        ("metadata_retrieved","metadata_retrieved"),
        ("production_source_path_leads","production_source_path_leads"),
        ("shortlisted_for_manual_review","shortlisted_manual_review"),
        ("independently_approved_executable_tasks","approved_executable_tasks"),
    ):
        if semantic.get(new)!=original.get(old):
            raise ValueError("metadata release semantic snapshot discrepancy: "+old)
    for key in ("discovered_pr_links","pr_metadata_retrieved",
                "production_source_path_leads","manual_shortlist",
                "qualified_executable_tasks","independent_functional_oracles"):
        if key in source:
            value=source[key]
            expected={
                "discovered_pr_links":120,"pr_metadata_retrieved":119,
                "production_source_path_leads":62,"manual_shortlist":12,
                "qualified_executable_tasks":0,"independent_functional_oracles":0,
            }[key]
            if value!=expected:
                raise ValueError("remaining-work dataset gate disagrees: "+key)
    if not type(source_registry_count) is int or source_registry_count < 1:
        raise ValueError("dataset candidate registry required")
    selected_models=protocol.get("model_ids")
    policies=protocol.get("policy_ids")
    if (protocol.get("model_count")!=6 or not isinstance(selected_models,list)
            or len(selected_models)!=6 or len(set(selected_models))!=6
            or not isinstance(policies,list) or len(policies)!=8
            or len(set(policies))!=8):
        raise ValueError("model or policy protocol roster drift")
    if (study.get("confirmatory_policies")!=8 or
            models.get("selected_for_planning")!=6 or
            protocol.get("qualified_task_ids")!=[] or
            protocol.get("results_measured") is not False or
            protocol.get("runner_isolated_and_attested") is not False or
            protocol.get("independent_oracles_sealed") is not False or
            protocol.get("model_revisions_frozen") is not False or
            protocol.get("primary_treatment") not in policies or
            protocol.get("primary_comparator") not in policies):
        raise ValueError("experimental readiness incorrectly promoted")
    if (paper.get("results_present_as_real_study") is not False
            or paper.get("external_live_overleaf_project_synced") is not False
            or paper.get("actual_springer_pdf_compiled_and_inspected") is not False):
        raise ValueError("manuscript report cannot claim unverifiable results")
    if (protocol.get("external_code_executions")!=0 or
            models.get("real_inference_runs_verified")!=0):
        raise ValueError("cannot reclassify model runs as verified")
    if (set(row["id"] for row in METRIC_DEFINITIONS)
            != set(["verified_full_task_success_itt","release_coverage",
                    "wrong_release_risk","paired_itt_success_difference",
                    "five_resource_realized_cost",
                    "infrastructure_failure_sensitivity_bounds"])):
        raise ValueError("metric IDs must remain explicitly defined")
    data={
        "schema_version":"1.0",
        "stage":"PROSPECTIVE_RESEARCH_METADATA_AUDITED_NO_EMPIRICAL_RESULTS",
        "metadata":{
            "unit":"unique PR-link/repository-name discovery record, NOT executable task",
            "records":original["discovered_pr_links"],
            "retrieved":original["metadata_retrieved"],
            "query_language_strata":12,
            "production_source_path_leads":original["production_source_path_leads"],
            "review_shortlist":original["shortlisted_for_manual_review"],
            "approved_executable_tasks":0,
            "independent_functional_oracles":0,
            "candidate_public_dataset_sources":source_registry_count,
            "actual_changed_language_coverage_verified":False,
        },
        "confirmatory_study":{
            "planned_model_names":len(selected_models),
            "planned_policy_slots":len(policies),
            "planned_primary_contrast":[protocol["primary_treatment"],
                                        protocol["primary_comparator"]],
            "frozen_model_revisions":0,
            "verified_real_inference_runs":0,
            "sealed_oracles":0,
            "fully_implemented_real_policy_comparators":0,
            "independently_mapped_sandbox":False,
            "paper_results_present":False,
        },
        "metric_dictionary":list(METRIC_DEFINITIONS),
        # Null is semantically not available; 0 would be misleading, and
        # must never be used for unknown effects or unknown release risk.
        "observed_metric_values":{x["id"]:None for x in METRIC_DEFINITIONS},
        "observed_denominator":None,
        "live_overleaf_synced":False,
        "actual_pdf_visual_review":False,
        "interpretation":"DATASET_PREPARATION_AND_SOFTWARE_INSTRUMENTATION_ONLY",
    }
    return ReadinessSnapshot(data)


def readiness_markdown(snapshot: ReadinessSnapshot) -> str:
    if not isinstance(snapshot,ReadinessSnapshot):
        raise TypeError("verified readiness snapshot required")
    d=snapshot.data
    if any(value is not None for value in d["observed_metric_values"].values()):
        raise ValueError("no empirical values can appear in a prospective report")
    lines=[
        "# U-CODE — verified research preparation status",
        "",
        "> **Prospective only.** No verified empirical software-repair outcomes,",
        "> independently admitted executable tasks, sealed oracles, trained",
        "> confidence models, or real six-model experiments. This report is",
        "> generated from repository registries and metadata source audits.",
        "",
        "## Dataset integrity (PR metadata, not executable tasks)",
        "",
        "| Counter | Verified source-state value |",
        "|---|---:|",
    ]
    m=d["metadata"]
    for name,key in (
        ("PR discovery records","records"),
        ("PR metadata retrieved","retrieved"),
        ("GitHub search-language query strata","query_language_strata"),
        ("Production source-path leads","production_source_path_leads"),
        ("Manual-review shortlist","review_shortlist"),
        ("Independently approved executable tasks","approved_executable_tasks"),
        ("Independent functional oracles","independent_functional_oracles"),
        ("Candidate public dataset sources","candidate_public_dataset_sources"),
    ):
        lines.append("| "+name+" | "+str(m[key])+" |")
    lines += [
        "",
        "**The twelve query-language strata do not establish actual",
        "changed-source coverage in twelve languages.**",
        "",
        "## Confirmatory study",
        "",
        "Six model names and eight policy slots are registered for prospective",
        "comparison. Actual model inference, independently authenticated",
        "resource metering, task admission and real policy-effect estimates",
        "are still blocked.",
        "",
        "## Metric definitions (no observed values yet)",
        "",
        "| Metric | Numerator / denominator | Undefined state |",
        "|---|---|---|",
    ]
    for x in d["metric_dictionary"]:
        lines.append("| "+x["id"]+" | "+x["numerator"]+" / "+
                     x["denominator"]+" | "+x["zero_denominator"]+" |")
    lines += [
        "",
        "For all six metrics the **observed value is N/A**, not zero.",
        "In particular, wrong-release risk is undefined with no released",
        "patches; a zero-release policy cannot be declared perfectly safe.",
        "The intention-to-treat denominator is all assigned task cells,",
        "including abstentions/timeouts. Independent evaluator labels",
        "must join only after terminal policy actions.",
        "",
        "The U-CODE manuscript and Overleaf source are prospective; source",
        "lint does not compile or visually validate a publisher PDF.",
        "",
    ]
    return "\n".join(lines)
