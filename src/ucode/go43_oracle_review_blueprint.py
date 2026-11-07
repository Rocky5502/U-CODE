"""Go #43 frozen pre-fix design review; NEVER an evaluator or task admission.

The official pre-fix Git tree identifies a public `docs/design.md` blob.
This module verifies its Git blob ID against the original base tree and
constructs an EXTERNAL reviewer plan that does not include test code,
expected outputs, post-PR patches, oracle secrets or executable source.

Important scientific ambiguity: the original design states both zero
floor for losers' points and equal winner/loser transfers (conservation).
Those statements cannot universally hold for an underfunded loser.
A reviewer must determine the rule; no guessed 'fix' can be a hidden gold.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1, sha256
from pathlib import Path
import re
from typing import Mapping

from .pilot_preflight import build_pilot_preflight
from .task_admission import REQUIRED_GATES

_BASE="ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a"
_TREE="e53fb011857926632c4a4ec8752425e0f2b41559"
_BLOB="b566ca7627b6518670a866a6a637bd5257e947f4"
_BYTES=16052
_GO_MOD="0933c3551c51527a752bc5cca0bd47581fc304a5"
_REPO="PlayHuai/eighty-point-huai-an"
_PATH="docs/design.md"
_STAGE="GO43_PUBLIC_REVIEW_QUESTIONS_NOT_EXECUTABLE_ORACLE"
_STATUS="PROPOSED_REVIEW_ONLY_NO_TEST_CODE_OR_GOLD"
_QUESTION_FIELDS=frozenset(("case_id","spec_sections","stage","gold_output_included"))
_AMBIGUITY_FIELDS=frozenset(("ambiguity_id","spec_section","status"))
_TOP=frozenset((
    "schema_version","stage","candidate_id","repository","task_scope",
    "base_commit","base_tree_sha","source_document_path",
    "source_document_git_blob_sha40","source_document_bytes",
    "toolchain_go_mod_sha40","external_business_rules_normativity_review",
    "independent_source_era_scope_approved",
    "oracle_case_families","ambiguity_register",
    "source_file_rights_adjudicated","oracle_independently_authored",
    "oracle_sealed_outside_repository","sandbox_attested",
    "execution_metering_attested","task_admitted","go_executed",
))
# Sections are **public pre-fix** requirements, not PR-added tests or
# post-fix behavior. No numerical answer keys are stored in the cases.
_CASES={
    "GAP_TIER_EDGES":("3.2",),
    "A_TWO_SINGLE_VS_SPRING":("3.2",),
    "HALL_MULTIPLIER_CASES":("3.2",),
    "LOW_BALANCE_SETTLEMENT":("3.2",),
    "FRACTIONAL_HALL_MULTIPLIER":("3.2",),
    "TEAM_DISTRIBUTION_AND_CONSERVATION":("3.2",),
    "RANK_BOUNDARY_CROSSING":("3.3",),
    "SETTLE_ONLY_ON_MATCH_COMPLETION":("1","3.1"),
    "NATURAL_LEVEL_NO_DIRECT_POINT_CHANGE":("3.2","6.6"),
    "ATOMIC_ALL_PLAYER_LEDGER":("7",),
    "RETRY_IDEMPOTENCE":("7",),
    "RECOVERY_AFTER_RECONNECT":("7",),
}
_AMBIGUITIES={
    "ZERO_FLOOR_VS_TOTAL_CONSERVATION":"3.2",
    "HALL_COEFFICIENT_FRACTIONAL_ROUNDING":"3.2",
    "TEAM_PLAYER_SPLIT_AND_NONNEGATIVE_BALANCE":"3.2",
    "SPRING_RULE_SOURCE_AND_SCOPE":"3.2",
    "ATOMIC_RETRY_IDENTITY_AND_OBSERVABILITY":"7",
    "EXTERNAL_BUSINESS_RULES_PRECEDENCE":"intro",
}
_NONADMISSION_FIELDS=(
    "source_file_rights_adjudicated",
    "oracle_independently_authored",
    "oracle_sealed_outside_repository",
    "sandbox_attested",
    "execution_metering_attested",
    "task_admitted",
    "go_executed",
    "independent_source_era_scope_approved",
)


def git_blob_sha1(raw:bytes)->str:
    """Compute Git's exact SHA-1 object ID over raw *file bytes*.

    Cryptographic SHA-1 is Git's historical object identifier, NOT a
    trustworthy real-world authorization or claim about the file rights.
    """
    if type(raw) is not bytes:
        raise TypeError("raw bytes required; avoid Unicode/newline rewrite")
    return sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


def inspect_go43_local_pref_fix_document(raw:bytes)->dict:
    """Read-only offline witness; never include source text or gold outputs."""
    if type(raw) is not bytes or len(raw)>1_000_000:
        raise ValueError("regular bounded pre-fix Git source file bytes required")
    git_id=git_blob_sha1(raw)
    if len(raw)!=_BYTES or git_id!=_BLOB:
        raise ValueError("source bytes do not match immutable pre-fix Git blob")
    try:
        source=raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("pre-fix source document must be valid UTF-8") from exc
    # The blob ID already binds the content. These headings check that the
    # expected functional *section types* are present and provide no test gold.
    for token in ("3.2 积分结算规则","3.3 段位设计","7 全局非功能需求"):
        if token not in source:
            raise ValueError("pinned source headings not found")
    return {
        "stage":"LOCAL_IMMUTABLE_GIT_BLOB_BYTES_MATCH_NOT_SPEC_APPROVAL",
        "source_document_git_blob_sha40":git_id,
        "source_document_sha256":sha256(raw).hexdigest(),
        "source_document_byte_count":len(raw),
        "source_document_content_returned":False,
        "pre_pr_issue_body_version_verified":False,
        "scope_normatively_approved":False,
        "hidden_oracle_independently_sealed":False,
        "external_code_executed":False,
        "experiment_task_admitted":False,
    }


def verify_go43_oracle_review_blueprint(
    blueprint:Mapping, source_meta:Mapping, pilot:dict,
    pre_fix_tree_inventory:Mapping, chronology:Mapping,
)->dict:
    """Fail closed against false golden answers, source drift and scope inflation."""
    if (type(blueprint) is not dict or set(blueprint)!=_TOP or
        blueprint["schema_version"]!="1.0" or
        blueprint["stage"]!=_STAGE):
        raise ValueError("Go reviewer blueprint schema drift / potential gold leakage")
    if (type(source_meta) is not dict or
        source_meta.get("stage")!="GO43_PRE_FIX_DOCUMENT_BLOB_METADATA_ONLY" or
        source_meta.get("candidate_id")!=43 or
        source_meta.get("repository")!=_REPO or
        source_meta.get("task_base_sha")!=_BASE or
        source_meta.get("base_tree_sha")!=_TREE or
        source_meta.get("spec_path")!=_PATH or
        source_meta.get("spec_blob_sha")!=_BLOB or
        source_meta.get("spec_blob_size_bytes")!=_BYTES or
        source_meta.get("spec_blob_type")!="blob" or
        source_meta.get("spec_blob_mode")!="100644" or
        source_meta.get("source_tree_truncated") is not False or
        any(source_meta.get(k) is not False for k in (
            "source_content_executed","pre_pr_issue_body_version_proven",
            "document_normatively_approved_as_full_pr_spec",
            "independent_oracle_sealed","source_file_rights_cleared",
            "experiment_eligible"))):
        raise ValueError("pre-fix source blob metadata drift or forged approval")
    if (type(pilot) is not dict or
        pilot.get("stage")!="REAL_PR_METADATA_PREFLIGHT_ONLY_BLOCKED_NO_EXECUTION" or
        pilot.get("qualified_executable_tasks")!=0 or
        pilot.get("independent_hidden_oracles_sealed")!=0 or
        pilot.get("pending_admission_checks")!=16 or
        pilot.get("real_model_runs")!=0):
        raise ValueError("pilot cannot self-approve a Go source-era microtask")
    candidates=pilot.get("candidates")
    if type(candidates) is not list or len(candidates)!=2:
        raise ValueError("exact PHP/Go candidate roster required")
    go=next((r for r in candidates if r.get("candidate_id")==43),None)
    if (go is None or go.get("repository")!=_REPO or
        go.get("immutable_pre_fix_base_sha40")!=_BASE or
        go.get("task_scope")!="declared_microtask" or
        go.get("open_gate_count")!=8 or
        go.get("independently_qualified") is not False or
        go.get("external_execution_allowed") is not False or
        set(go.get("open_evidence_gates",[]))!=set(REQUIRED_GATES)):
        raise ValueError("Go task scope not independently qualified")
    if (type(pre_fix_tree_inventory) is not dict or
        type(pre_fix_tree_inventory.get("records")) is not list):
        raise ValueError("pre-fix tree inventory required")
    tree=next((r for r in pre_fix_tree_inventory["records"]
               if r.get("candidate_id")==43),None)
    if (tree is None or tree.get("repository")!=_REPO or
        tree.get("base_commit")!=_BASE or
        tree.get("base_tree_sha")!=_TREE or
        tree.get("tree_recursion_truncated") is not False or
        tree.get("real_build_executed") is not False or
        tree.get("source_file_redistribution_approved") is not False or
        tree.get("independent_oracle_verified") is not False or
        tree.get("experiment_eligible") is not False or
        tree.get("toolchain_metadata")!=[{
            "path":"server/go.mod","git_blob_sha":_GO_MOD
        }]):
        raise ValueError("source-era Go toolchain/tree evidence drift")
    if (type(chronology) is not dict or
        type(chronology.get("records")) is not list):
        raise ValueError("source-era issue chronology required")
    issue=next((r for r in chronology["records"]
                if r.get("candidate_id")==43),None)
    if (issue is None or issue.get("repository")!=_REPO or
        issue.get("issue_number")!=29 or
        issue.get("pr_number")!=30 or
        issue.get("pr_base_sha")!=_BASE or
        issue.get("issue_text_at_pr_creation_immutably_archived") is not False or
        issue.get("independently_verified_pre_pr_specification") is not False or
        issue.get("executable_task_approved") is not False):
        raise ValueError("source-era issue not archived/approved")
    try:
        issue_at=datetime.fromisoformat(issue["issue_created_at"].replace("Z","+00:00"))
        pr_at=datetime.fromisoformat(issue["pr_created_at"].replace("Z","+00:00"))
    except (ValueError,AttributeError) as exc:
        raise ValueError("invalid source-era chronology") from exc
    if (issue_at.utcoffset()!=timezone.utc.utcoffset(issue_at) or
        pr_at.utcoffset()!=timezone.utc.utcoffset(pr_at) or
        (pr_at-issue_at).total_seconds()!=8):
        raise ValueError("unverified Go issue-to-PR eight-second chronology")
    expected=(43,_REPO,"declared_microtask",_BASE,_TREE,_PATH,_BLOB,_BYTES,_GO_MOD)
    observed=tuple(blueprint[k] for k in (
        "candidate_id","repository","task_scope","base_commit",
        "base_tree_sha","source_document_path",
        "source_document_git_blob_sha40","source_document_bytes",
        "toolchain_go_mod_sha40",
    ))
    if observed!=expected:
        raise ValueError("Go public blueprint must bind exact immutable pre-fix microtask")
    if blueprint["external_business_rules_normativity_review"]!="PENDING":
        raise ValueError("business-rule hierarchy needs independent adjudication")
    if any(blueprint[k] is not False for k in _NONADMISSION_FIELDS):
        raise ValueError("Go source blueprint cannot self-approve or execute task")
    cases=blueprint["oracle_case_families"]
    if type(cases) is not list or len(cases)!=len(_CASES):
        raise ValueError("all twelve pre-fix reviewer question families required")
    seen=set()
    for c in cases:
        if type(c) is not dict or set(c)!=_QUESTION_FIELDS:
            raise ValueError("unexpected oracle case field/gold leakage")
        cid=c["case_id"]
        if type(cid) is not str or cid not in _CASES or cid in seen:
            raise ValueError("unknown or duplicate Go oracle review case")
        seen.add(cid)
        if (type(c["spec_sections"]) is not list or
            c["spec_sections"]!=list(_CASES[cid])):
            raise ValueError("oracle review case must cite exact source-era requirement sections")
        if c["stage"]!=_STATUS or c["gold_output_included"] is not False:
            raise ValueError("no expected outputs or hidden oracle authorization in public blueprint")
    if seen!=set(_CASES):
        raise ValueError("missing source-era reviewer family")
    ambiguities=blueprint["ambiguity_register"]
    if type(ambiguities) is not list or len(ambiguities)!=len(_AMBIGUITIES):
        raise ValueError("all six unresolved source-era ambiguities required")
    encountered=set()
    for item in ambiguities:
        if type(item) is not dict or set(item)!=_AMBIGUITY_FIELDS:
            raise ValueError("unexpected ambiguity private answer/approval field")
        key=item["ambiguity_id"]
        if type(key) is not str or key not in _AMBIGUITIES or key in encountered:
            raise ValueError("duplicate/unknown source-era ambiguity")
        encountered.add(key)
        if (item["spec_section"]!=_AMBIGUITIES[key] or
            item["status"]!="NEEDS_INDEPENDENT_SPEC_AUTHOR_RESOLUTION"):
            raise ValueError("ambiguity cannot be resolved from PR/tests or LLM inference")
    return {
        "stage":"SOURCE_PINNED_REVIEW_HANDOFF_NOT_EXECUTABLE",
        "candidate_id":43,"immutable_pre_fix_spec_blob_sha40":_BLOB,
        "immutable_document_bytes_observed_via_source_metadata":_BYTES,
        "actual_local_source_bytes_verified_by_this_step":False,
        "pre_pr_issue_to_pr_seconds":8,
        "public_review_case_families":len(cases),
        "unresolved_normative_ambiguities":len(ambiguities),
        "independently_approved_task_specification":False,
        "independently_sealed_hidden_oracles":0,
        "file_specific_reuse_rights_approved":False,
        "sandbox_attested":False,
        "go_code_executed":False,
        "qualified_executable_tasks":0,
        "policy_visible_gold_output_bytes":0,
        "policy_prompt_authorized":False,
    }
