"""S05–S10 cross-ledger evidence audit; NEVER a task or model permit.

Combines separately frozen source-only pilot, model-card and critical-path
registries. Source files and Git hashes are evidence *leads*, not reviewers,
rights adjudication, sealed oracles or hardware measurements.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from .critical_path import ROOT, build_critical_path
from .pilot_preflight import build_pilot_preflight
from .public_model_card_audit import build_public_card_audit
from .shadow_eight_arm_runner import POLICIES

ISSUES = (65, 66, 67, 68, 69, 70)
SCOPE = ("S05", "S06", "S07", "S08", "S09", "S10")
STAGE = "S05_S10_SOURCE_EVIDENCE_CROSSWALK_NOT_REAL_EXPERIMENT"

# This is a prospective fidelity review inventory, not eight faithful agents.
METHOD_GAPS = {
    "ucode_conditional_bes": "full registered conditional controller, fitted dependence and real action integration unvalidated",
    "ucode_unconditional_bes": "matched no-history-assumption budgeted-search implementation unvalidated",
    "no_uncertainty_search": "strictly uncertainty-free matched-retrieval/generation baseline unvalidated",
    "uncertainty_only": "no extra search acquisition and identical opportunities not independently audited",
    "fixed_testing": "predeclared testing count, timing and matched five-resource accounting unvalidated",
    "selective_verification": "selective verifier source method and thresholds not independently reproduced",
    "mcts_search": "faithful Monte Carlo tree policy, rollout, backup and budget match not audited",
    "replay_search": "replay provenance, fairness and policy-blind action schedule not independently verified",
}
GO_FALSE = (
    "independent_source_era_scope_approved", "source_file_rights_adjudicated",
    "oracle_independently_authored", "oracle_sealed_outside_repository",
    "sandbox_attested", "execution_metering_attested", "task_admitted",
    "go_executed",
)
PHP_FALSE = (
    "source_file_rights_adjudicated", "original_issue_text_sealed",
    "independent_specification_reviewed", "oracle_independently_authored",
    "oracle_sealed_outside_repository", "sandbox_attested",
    "execution_metering_attested", "task_admitted", "php_executed",
)


def _json(root: Path, path: str) -> dict:
    file = root / path
    if not file.is_file() or file.is_symlink():
        raise ValueError("missing or linked canonical public source: " + path)
    parsed = json.loads(file.read_text(encoding="utf-8"))
    if type(parsed) is not dict:
        raise ValueError("canonical public source must be an object: " + path)
    return parsed


def audit_remaining_stage_evidence(
    protocol: Mapping, pilot: Mapping, critical: Mapping, card: Mapping,
    go: Mapping, php: Mapping, manuscript: str,
) -> dict:
    """Reject self-promoted six-stage evidence while preserving source facts.

    Arguments may be substituted with invented dictionaries by first-party
    negative tests; such substitution does not authorize future execution.
    """
    if any(type(x) is not dict for x in (protocol,pilot,critical,card,go,php)):
        raise TypeError("six typed canonical metadata objects required")
    if type(manuscript) is not str:
        raise TypeError("plain GitHub LaTeX source required, not compiled PDF")
    policies = protocol.get("policy_ids")
    models = protocol.get("model_ids")
    if (type(policies) is not list or len(policies) != 8
            or set(policies) != POLICIES or set(METHOD_GAPS) != POLICIES
            or type(models) is not list or len(models) != 6
            or len(set(models)) != 6
            or protocol.get("primary_treatment") != "ucode_conditional_bes"
            or protocol.get("primary_comparator") != "no_uncertainty_search"
            or protocol.get("policy_implementations_faithfully_reproduced") is not False
            or protocol.get("qualified_task_ids") != []
            or protocol.get("results_measured") is not False):
        raise ValueError("S05 frozen six-model/eight-policy fidelity contract drift")
    if (critical.get("stage") != "SOURCE_LINKED_CRITICAL_PATH_NO_REAL_RESULTS"
            or critical.get("policies",{}).get("registered") != 8
            or critical.get("policies",{}).get("faithfully_real_task_verified") != 0
            or critical.get("milestone_accounting",{}).get(
                "independently_verified_complete_exit_criteria") != 0
            or critical.get("milestone_accounting",{}).get(
                "still_without_full_exit_evidence") != 10
            or critical.get("milestone_accounting",{}).get(
                "overall_percent_complete") is not None
            or critical.get("scientific_measurement",{}).get(
                "measured_primary_effect") is not None
            or critical.get("scientific_measurement",{}).get(
                "independently_qualified_real_model_runs") != 0
            or critical.get("manuscript",{}).get(
                "external_live_overleaf_synced") is not False
            or critical.get("manuscript",{}).get(
                "verified_publisher_pdf_compiled") is not False):
        raise ValueError("S10 scientific exit or manuscript falsely promoted")
    if (critical.get("metadata_discovery",{}).get("pr_leads") != 120
            or critical.get("independent_pilot_admission",{}).get("open_checks") != 16
            or critical.get("independent_pilot_admission",{}).get(
                "qualified_executable_tasks") != 0):
        raise ValueError("S06 candidate lineage/admission inventory drift")
    candidates = pilot.get("candidates")
    if (pilot.get("stage") != "REAL_PR_METADATA_PREFLIGHT_ONLY_BLOCKED_NO_EXECUTION"
            or type(candidates) is not list
            or [c.get("candidate_id") for c in candidates] != [43,104]
            or pilot.get("pending_admission_checks") != 16
            or pilot.get("independent_hidden_oracles_sealed") != 0
            or pilot.get("qualified_executable_tasks") != 0
            or pilot.get("real_model_runs") != 0
            or pilot.get("confirmed_primary_effect") is not None
            or any(c.get("open_gate_count") != 8
                   or c.get("external_execution_allowed") is not False
                   or c.get("independently_qualified") is not False
                   for c in candidates)):
        raise ValueError("S07/S08 external task gate falsely promoted")
    # Go spec: six independent normative questions and twelve hypothetical
    # case families, with no gold output or signoff in the public blueprint.
    if (go.get("stage") != "GO43_PUBLIC_REVIEW_QUESTIONS_NOT_EXECUTABLE_ORACLE"
            or go.get("candidate_id") != 43
            or go.get("base_commit") != candidates[0].get(
                "immutable_pre_fix_base_sha40")
            or go.get("external_business_rules_normativity_review") != "PENDING"
            or any(go.get(field) is not False for field in GO_FALSE)
            or type(go.get("ambiguity_register")) is not list
            or len(go["ambiguity_register"]) != 6
            or len({x.get("ambiguity_id") for x in go["ambiguity_register"]}) != 6
            or any(x.get("status") != "NEEDS_INDEPENDENT_SPEC_AUTHOR_RESOLUTION"
                   for x in go["ambiguity_register"])
            or type(go.get("oracle_case_families")) is not list
            or len(go["oracle_case_families"]) != 12
            or any(x.get("gold_output_included") is not False
                   for x in go["oracle_case_families"])):
        raise ValueError("S07 Go43 source-era ambiguity/oracle source altered")
    if (php.get("stage") != "PHP104_EXTERNAL_ORACLE_BLUEPRINT_ONLY"
            or php.get("candidate_id") != 104
            or php.get("base_commit") != candidates[1].get(
                "immutable_pre_fix_base_sha40")
            or any(php.get(field) is not False for field in PHP_FALSE)
            or type(php.get("oracle_case_families")) is not list
            or len(php["oracle_case_families"]) != 10
            or any(x.get("gold_output_included") is not False
                   for x in php["oracle_case_families"])):
        raise ValueError("S08 PHP104 source-era/oracle scope altered")
    if (card.get("stage") != "SIX_MODEL_PUBLIC_CARD_PROVENANCE_GAP_AUDIT_ONLY"
            or card.get("planned_models") != 6
            or card.get("actual_qualified_checkpoints") != 0
            or card.get("verified_private_model_accesses") != 0
            or card.get("full_license_reviews_completed") != 0
            or card.get("models_loaded_or_inferred") != 0
            or card.get("real_model_outcomes") != 0
            or card.get("card_observations_authentic_signed_snapshots") is not False
            or type(card.get("model_rows")) is not list
            or [r.get("model_id") for r in card["model_rows"]] != models
            or any(r.get("model_runnable_for_study") is not False
                   or r.get("full_license_and_access_authorized") is not False
                   or r.get("checkpoint_and_tokenizer_sha_pinned") is not False
                   for r in card["model_rows"])):
        raise ValueError("S09 unsigned model card metadata falsely approved")
    # Validate source assertions, not whether the paper compiles or achieves
    # anything empirical; no hidden evaluator result is read here.
    for marker in (
        r"\label{eq:paired}",
        r"\label{eq:lineage-omission}",
        r"\paragraph{Prospective matched quality--resource Pareto audit.}",
        r"\paragraph{Two-order conditional likelihood coherence (S04).}",
    ):
        if marker not in manuscript:
            raise ValueError("S10 manuscript source missing methods audit marker")
    return {
        "schema_version": "1.0",
        "stage": STAGE,
        "sprint_stage_ids": list(SCOPE),
        "sprint_issue_numbers": list(ISSUES),
        "registered_policy_ids": list(policies),
        "policy_fidelity_review": [
            {"policy_id":p, "fidelity_reproduction_status":
             "UNVERIFIED_SOURCE_METHOD_AND_REAL_TASK_MATCH",
             "missing_method_evidence":METHOD_GAPS[p]}
            for p in policies
        ],
        "policy_slots_count_not_faithful": 8,
        "lineage_metadata_leads_not_admitted": 120,
        "independent_lineage_split_attested": False,
        "go43_unresolved_normativity_questions": 6,
        "go43_public_review_case_families_not_gold": 12,
        "php104_public_review_case_families_not_gold": 10,
        "external_task_admission_gates_pending": 16,
        "independently_admitted_tasks": 0,
        "model_slots_not_qualified": 6,
        "authenticated_model_snapshots": 0,
        "observed_real_model_runs": 0,
        "scientific_exit_criteria_verified": 0,
        "scientific_exit_criteria_pending": 10,
        "measured_primary_effect": None,
        "github_manuscript_source_present": True,
        "overleaf_live_sync_verified": False,
        "independent_paper_pdf_compilation_verified": False,
        "stage_status": {
            "S05":"SOURCE_WIRING_AUDIT_DONE_METHOD_FIDELITY_OPEN",
            "S06":"SOURCE_GRAPH_SEMANTIC_AUDIT_DONE_SPLIT_ADJUDICATION_OPEN",
            "S07":"GO43_PUBLIC_HANDOFF_AUDITED_INDEPENDENT_SPEC_OPEN",
            "S08":"PHP104_PUBLIC_HANDOFF_AUDITED_INDEPENDENT_SPEC_OPEN",
            "S09":"PUBLIC_MODEL_CARD_AUDITED_FULL_LICENSE_RUNTIME_OPEN",
            "S10":"MANUSCRIPT_SOURCE_CROSSCHECKED_REAL_EVALUATION_OPEN",
        },
        "no_execution_permit": True,
        "external_code_executed": False,
        "independently_authenticated_reviewer_signatures": 0,
        "synthetic_unit_tests_are_not_real_success": True,
    }


def build_remaining_stage_evidence(root: Path = ROOT) -> dict:
    base = Path(root)
    paper_file = base / "paper/overleaf/main.tex"
    if not paper_file.is_file() or paper_file.is_symlink():
        raise ValueError("missing or linked manuscript source")
    return audit_remaining_stage_evidence(
        _json(base, "configs/confirmatory_sbse_protocol_2026-10-25.json"),
        build_pilot_preflight(base),
        build_critical_path(base),
        build_public_card_audit(root=base),
        _json(base, "data/admission/2026-11-07/"
                    "go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json"),
        _json(base, "data/admission/2026-10-28/"
                    "php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json"),
        paper_file.read_text(encoding="utf-8"),
    )
