"""Evidence-grounded G5/M4 external pilot readiness inventory (NO EXECUTION).

Reads the frozen, real PR metadata files and existing evaluator registrations,
enforces their identities against the canonical corpus, and reports why no
external code, DRPA model comparison or oracle evaluation is yet allowed.

IMPORTANT: This is an INFORMATIONAL REVIEW-ONLY preflight. A future real
runner must require separately authenticated signed task admission and never
treat an output of this module as an execution permit.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from scripts.check_task_admission import validate_prospective_dossiers
from scripts.summarize_audit import load_manifest, load_records
from .evaluator_boundary import (
    evaluate_registration, registration_from_json,
)
from .task_admission import REQUIRED_GATES, parse_dossier

ROOT = Path(__file__).resolve().parents[2]
_DATA = ROOT / "data" / "admission"
_REGISTRATIONS = ROOT / "data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl"
_DOSSIERS = _DATA / "2026-10-25/pilot_dossiers.jsonl"
_EXPECTED_IDS = (43, 104)


def _json(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if type(obj) is not dict:
        raise ValueError("expected a single JSON object: " + str(path))
    return obj


def _jsonl(path: Path) -> tuple[dict, ...]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if type(value) is not dict:
            raise ValueError("JSONL entries must be objects")
        items.append(value)
    return tuple(items)


def build_pilot_preflight(root: Path = ROOT) -> dict:
    """Fail closed on source identity drift; never infer permission from hashes.

    Only first-party JSON/CSV metadata is read. No dynamic imports from the
    candidate repositories, network calls, shell commands or model inference.
    """
    root = Path(root)
    admission = root / "data/admission"
    manifest = load_manifest(root / "data/discovery/agent_pr_candidates_120.csv")
    audited = load_records(root / "data/audits/2026-10-24", manifest)
    source_dossiers = admission / "2026-10-25/pilot_dossiers.jsonl"
    verified = validate_prospective_dossiers(audited, manifest, source_dossiers)
    dossiers = {x.candidate_id: x for x in
                (parse_dossier(row) for row in _jsonl(source_dossiers))}
    registration_rows = _jsonl(
        root / "data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl")
    registrations = {}
    for payload in registration_rows:
        reg = registration_from_json(payload)
        if reg.candidate_id in registrations:
            raise ValueError("duplicate prospective evaluator registration")
        registrations[reg.candidate_id] = reg
    if (tuple(sorted(dossiers)) != _EXPECTED_IDS
            or tuple(sorted(registrations)) != _EXPECTED_IDS
            or tuple(x["candidate_id"] for x in verified) != _EXPECTED_IDS):
        raise ValueError("candidate cohort drift requires a separately frozen registration")

    php = _json(admission / "2026-10-28/php104_base_source_contract_leads.json")
    php_cases = _json(admission /
                      "2026-10-28/php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json")
    go = _json(admission /
               "2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json")
    if (php.get("candidate_id") != 104
            or php.get("base_commit") != dossiers[104].base_sha
            or php.get("executable_task_admitted") is not False
            or php.get("independent_pre_fix_task_spec_approved") is not False
            or php.get("held_out_oracle_approved") is not False
            or php.get("source_rights_cleared") is not False
            or php.get("parent_issue_body_at_pr_time_archived") is not False):
        raise ValueError("PHP source-era public evidence drift or forged approval")
    if (php_cases.get("candidate_id") != 104
            or php_cases.get("base_commit") != php["base_commit"]
            or php_cases.get("task_admitted") is not False
            or php_cases.get("oracle_sealed_outside_repository") is not False
            or php_cases.get("php_executed") is not False
            or any(x.get("gold_output_included") is not False
                   for x in php_cases.get("oracle_case_families", []))):
        raise ValueError("PHP public blueprint must contain no oracle/gold approval")
    if (go.get("candidate_id") != 43
            or go.get("repository") != dossiers[43].repository
            or go.get("task_base_sha") != dossiers[43].base_sha
            or go.get("spec_blob_sha") != registrations[43].pre_fix_spec_blob_sha
            or go.get("pre_pr_issue_body_version_proven") is not False
            or go.get("independent_oracle_sealed") is not False
            or go.get("experiment_eligible") is not False):
        raise ValueError("Go pre-fix spec metadata drift or forged approval")

    protocol = _json(root / "configs/confirmatory_sbse_protocol_2026-10-25.json")
    models = _json(root / "configs/accepted_six_model_study_2026-10-25.json")
    # Inspect the canonical protocol rather than fabricating a task allocation.
    if (protocol.get("model_count") != 6
            or len(protocol.get("model_ids", [])) != 6
            or len(set(protocol["model_ids"])) != 6
            or len(protocol.get("policy_ids", [])) != 8
            or len(set(protocol["policy_ids"])) != 8
            or protocol.get("primary_treatment") not in protocol["policy_ids"]
            or protocol.get("primary_comparator") not in protocol["policy_ids"]
            or protocol.get("primary_treatment") == protocol.get("primary_comparator")
            or protocol.get("qualified_task_ids") != []
            or protocol.get("model_revisions_frozen") is not False
            or protocol.get("independent_oracles_sealed") is not False
            or protocol.get("runner_isolated_and_attested") is not False
            or protocol.get("results_measured") is not False
            or protocol.get("seeds_frozen") is not False
            or protocol.get("final_budget_caps_frozen") is not False):
        raise ValueError("confirmatory protocol changed: requires explicit registration review")
    # The separate model-study manifest must describe the selected six,
    # without requiring future results in this current frozen gate check.
    if type(models) is not dict:
        raise ValueError("typed model study required")

    leads = []
    for candidate_id in _EXPECTED_IDS:
        task = dossiers[candidate_id]
        reg = registrations[candidate_id]
        report = next(x for x in verified if x["candidate_id"] == candidate_id)
        if (reg.repository != task.repository or reg.task_base_sha != task.base_sha
                or set(reg.pr_authored_test_paths) != set(task.changed_test_paths)
                or reg.status != "PROSPECTIVE_UNSEALED"
                or report["eligible_for_experiment"] is not False
                or set(report["open_gates"]) != set(REQUIRED_GATES)
                or report["status"] != "NEEDS_EVIDENCE"):
            raise ValueError("cross-ledger task, test or admission identity mismatch")
        reader = evaluate_registration(reg)
        if (reader["independently_admitted"] is not False
                or reader["oracle_evaluations"] != 0):
            raise ValueError("unattested evaluator metadata cannot claim admission")
        source_era = (
            "PHP_ISSUE_TEXT_NOT_ARCHIVED_AT_PR_CREATION" if candidate_id == 104
            else "GO_PINNED_DESIGN_BLOB_MICROTASK_SCOPE_NOT_FULL_PR"
        )
        leads.append({
            "candidate_id": candidate_id,
            "repository": task.repository,
            "pr_url": task.pr_url,
            "immutable_pre_fix_base_sha40": task.base_sha,
            "task_scope": reg.task_scope,
            "source_era_spec_issue": source_era,
            "open_evidence_gates": list(report["open_gates"]),
            "open_gate_count": len(report["open_gates"]),
            "evaluator_registration_blockers": reader["missing_or_unverified"],
            "policy_visible_registration_sha256": reader["policy_view_digest_sha256"],
            "dossier_sha256": report["dossier_sha256"],
            "prospective_only": True,
            "independently_qualified": False,
            "external_execution_allowed": False,
        })

    # Specific artifact and approvals needed to move forward, but never
    # publish hidden oracle contents or independent private reviewer evidence.
    return {
        "schema_version": "1.0",
        "stage": "REAL_PR_METADATA_PREFLIGHT_ONLY_BLOCKED_NO_EXECUTION",
        "candidates": leads,
        "candidate_count": len(leads),
        "pending_admission_checks": sum(x["open_gate_count"] for x in leads),
        "model_slots_registered_not_qualified": len(protocol["model_ids"]),
        "policy_slots_registered_not_executed": len(protocol["policy_ids"]),
        "primary_treatment": protocol["primary_treatment"],
        "primary_comparator": protocol["primary_comparator"],
        "drpa_exploratory_only": True,
        "matched_real_run_matrix_frozen": False,
        "independent_hidden_oracles_sealed": 0,
        "qualified_executable_tasks": 0,
        "real_model_runs": 0,
        "drpa_real_task_evaluations": 0,
        "confirmed_primary_effect": None,
        "external_source_executed": False,
        "hidden_oracle_values_exposed": False,
        "required_next_actions": [
            "Independent specification adjudication and source-era provenance",
            "File-level permission and line-level AI authorship review",
            "Evaluator-only independently authored sealed task oracle and prior commitment",
            "Repository-lineage train/evaluation separation",
            "Rootless network-disabled sandbox and audited CPU/GPU/token/test/wall meters",
            "Frozen model/checkpoint, tokenizer, seeds, caps and matched action opportunities",
            "Separate authorization by independently responsible evaluators",
        ],
        "warning": (
            "No script in this research-only preflight can promote tasks. "
            "Hash equality and first-party CI do not authenticate a sealed oracle. "
            "Do not run external PHP/Go sources or LLM trials under this report."
        ),
    }
