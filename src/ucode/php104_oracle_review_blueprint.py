"""PHP #104 external-oracle design *blueprint*, NOT a hidden oracle.

This checked-in material must never contain test implementations, gold outputs,
post-fix patch text or approved evaluator results. An independent reviewer
must author and seal those materials elsewhere. We verify only that a
reviewer-facing plan derives from pinned pre-fix observations and cannot
self-promote into a qualified task.

This code does not run third-party PHP or authenticate GitHub/API evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from .php104_source_contract_audit import verify_php104_source_contract_leads

_TOP = frozenset((
    "schema_version", "stage", "candidate_id", "base_commit",
    "base_commit_time", "root_license_blob_sha", "root_license_observed",
    "copyright_notice_observations", "oracle_case_families",
    "source_file_rights_adjudicated", "original_issue_text_sealed",
    "independent_specification_reviewed", "oracle_independently_authored",
    "oracle_sealed_outside_repository", "sandbox_attested",
    "execution_metering_attested", "task_admitted", "php_executed",
))
_NOTICE = frozenset(("path", "blob_sha", "notice_type"))
_CASE = frozenset(("case_id", "witness_ids", "stage", "gold_output_included"))
_BASE_SHA = "25e9b1cf855669c24ba1609c7d4cfcda17ac6217"
_LICENSE = "9d2375c29942233e3b646d51210ebc67235df873"
_NOTICE_BY_PATH = {
    "src/PersistenceHandler/FilePersistenceHandler.php": (
        "1edebb766b53d2117972a8bafaff27d716b55163",
        "AUTHOR_AND_COPYRIGHT_HEADER_2021",
    ),
    "src/PersistenceHandler/FileSerializedResourcePersistenceHandler.php": (
        "96d3e275e091c50d510687a3d9bbf75b4c69c369",
        "AUTHOR_AND_COPYRIGHT_HEADER_2021",
    ),
    "src/Filter/Prefetch/CachedResourceFilter.php": (
        "7674093fb5be90b082cbd2b35565cf506944d9fa",
        "AUTHOR_DOCBLOCK_ONLY",
    ),
    "tests/Filter/Prefetch/CachedResourceFilterTest.php": (
        "e6c9e6e2ad94c69b8ec55c77642f341626cf601e",
        "COPYRIGHT_AND_ROOT_LICENSE_POINTER",
    ),
}
# Every proposed case is grounded in unexecuted baseline observations. These
# are COVERAGE QUESTIONS, not pass/fail predicates or answer keys. The
# integration case must span writer AND reader to discourage circular tests.
_FAMILIES = {
    "EMPTY_OR_ROOT_URI": ("FILE_LAYOUT_PATH_COMPLETION",),
    "TRAILING_SLASH_DIRECTORY": ("FILE_LAYOUT_PATH_COMPLETION",),
    "NESTED_URI_PATH": (
        "FILE_LAYOUT_PATH_COMPLETION", "FILE_LAYOUT_BASENAME_ENCODING"),
    "ENCODED_BASENAME": ("FILE_LAYOUT_BASENAME_ENCODING",),
    "SPIDER_ID_NAMESPACE": ("CACHE_LOOKUP_AND_FRESHNESS",),
    "BASE_PATH_SEPARATOR": (
        "FILE_LAYOUT_PATH_COMPLETION", "CACHE_LOOKUP_AND_FRESHNESS"),
    "REAL_WRITER_CACHE_LOOKUP": (
        "SERIALIZED_RESOURCE_WRITER", "CACHE_LOOKUP_AND_FRESHNESS"),
    "CACHE_FRESHNESS_BOUNDARIES": ("CACHE_LOOKUP_AND_FRESHNESS",),
    "PROTECTED_NAMING_EXTENSION": ("FILE_LAYOUT_PATH_COMPLETION",),
    "INDEPENDENT_LEGACY_FIXTURE": (
        "CACHE_TEST_FIXTURE_LAYOUT_DUPLICATION",
        "SERIALIZED_RESOURCE_WRITER", "CACHE_LOOKUP_AND_FRESHNESS"),
}


def _utc(value: object) -> datetime:
    if type(value) is not str:
        raise ValueError("ISO timestamp text required")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if t.tzinfo is None:
        raise ValueError("timezone aware timestamp required")
    return t.astimezone(timezone.utc)


def verify_php104_oracle_blueprint(
    blueprint: Mapping, source_contract: Mapping, chronology: dict,
    source_trees: dict, dossiers: list,
) -> dict:
    """Verify a non-executable, non-sealed reviewer plan with strict identity.

    Outputs only counts and audit risks. It has no admission boolean that
    can become true, and no test fixtures or expected results are accepted.
    """
    if (type(blueprint) is not dict or set(blueprint) != _TOP
            or blueprint["schema_version"] != "1.0"
            or blueprint["stage"] != "PHP104_EXTERNAL_ORACLE_BLUEPRINT_ONLY"):
        raise ValueError("review blueprint schema drift or forbidden oracle field")
    src = verify_php104_source_contract_leads(
        source_contract, chronology, source_trees, dossiers)
    if src["executable_tasks_admitted"] != 0:
        raise ValueError("unapproved source contract cannot enable an experiment")
    if (type(blueprint["candidate_id"]) is not int
            or blueprint["candidate_id"] != 104
            or blueprint["base_commit"] != _BASE_SHA
            or blueprint["base_commit"] != source_contract["base_commit"]
            or blueprint["root_license_blob_sha"] != _LICENSE):
        raise ValueError("pinned PHP task/base/source-license identity mismatch")
    if blueprint["root_license_observed"] != "ROOT_MIT_NOTICE_REVIEW_NOT_CLEARED":
        raise ValueError("root notice is not file-level rights adjudication")
    for name in (
        "source_file_rights_adjudicated", "original_issue_text_sealed",
        "independent_specification_reviewed", "oracle_independently_authored",
        "oracle_sealed_outside_repository", "sandbox_attested",
        "execution_metering_attested", "task_admitted", "php_executed",
    ):
        if blueprint[name] is not False:
            raise ValueError("blueprint cannot self-approve missing external gates")
    base_at = _utc(blueprint["base_commit_time"])
    parent_at = _utc(source_contract["parent_issue_created_at"])
    child_at = _utc(chronology["records"][0]["issue_created_at"])
    if (base_at.isoformat() != "2026-10-22T22:07:39+00:00"
            or not base_at < parent_at < child_at):
        raise ValueError("source-era base commit must strictly predate issue text")
    notices = blueprint["copyright_notice_observations"]
    if (type(notices) is not list
            or len(notices) != len(_NOTICE_BY_PATH)):
        raise ValueError("complete four-file rights observation required")
    seen_notices = set()
    for notice in notices:
        if type(notice) is not dict or set(notice) != _NOTICE:
            raise ValueError("unexpected copyright notice field or confidential data")
        path = notice["path"]
        if type(path) is not str or path not in _NOTICE_BY_PATH or path in seen_notices:
            raise ValueError("duplicate or unknown copyright source path")
        seen_notices.add(path)
        if ((notice["blob_sha"], notice["notice_type"]) !=
                _NOTICE_BY_PATH[path]):
            raise ValueError("rights observation not pinned to original Git blob")
    if seen_notices != set(_NOTICE_BY_PATH):
        raise ValueError("missing reviewed root-scoped source notice")
    cases = blueprint["oracle_case_families"]
    if type(cases) is not list or len(cases) != len(_FAMILIES):
        raise ValueError("ten independent-review case families required")
    seen = set()
    for case in cases:
        if type(case) is not dict or set(case) != _CASE:
            raise ValueError("unexpected oracle case data or potential answer leakage")
        cid = case["case_id"]
        if type(cid) is not str or cid not in _FAMILIES or cid in seen:
            raise ValueError("duplicate or unregistered review family")
        seen.add(cid)
        if (type(case["witness_ids"]) is not list
                or case["witness_ids"] != list(_FAMILIES[cid])):
            raise ValueError("case witnesses must be exact pre-fix evidence IDs")
        if case["stage"] != "PROPOSED_NO_ORACLE_CODE_OR_EXPECTED_OUTPUT":
            raise ValueError("a public blueprint cannot claim executed cases")
        if case["gold_output_included"] is not False:
            raise ValueError("gold outputs must never be stored in public blueprint")
    if seen != set(_FAMILIES):
        raise ValueError("missing prospective case family")
    return {
        "status": "REVIEW_PLAN_ONLY_NOT_INDEPENDENT_HIDDEN_ORACLE",
        "candidate_id": 104,
        "base_commit_predates_parent_seconds": int(
            (parent_at - base_at).total_seconds()),
        "observed_root_license": "MIT_REPOSITORY_ROOT_REVIEW_ONLY",
        "source_notice_files_observed": len(seen_notices),
        "prospective_oracle_case_families": len(seen),
        "sealed_hidden_oracles": 0,
        "source_file_rights_approved": False,
        "independent_task_spec_approved": False,
        "qualified_executable_tasks": 0,
        "php_code_executed": False,
        "public_gold_output_bytes": 0,
        "policy_input_authorized": False,
    }
