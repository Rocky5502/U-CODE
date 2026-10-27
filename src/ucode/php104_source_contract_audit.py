"""Read-only source-era feasibility audit for PHP candidate #104.

A checked-in Git blob ID is not a trusted independent oracle or proof that
the CURRENT wording of an issue existed at PR creation. No third-party code
is executed, and this module cannot authorize source reuse or task admission.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Mapping

from .issue_chronology import verify_issue_prepr_chronology
from .pre_fix_tree_audit import check_pre_fix_tree_inventory

_TOP = frozenset((
    "schema_version", "stage", "observed_on", "candidate_id",
    "repository", "parent_issue_url", "parent_issue_created_at",
    "parent_issue_updated_at", "child_issue_url", "base_commit",
    "base_tree_sha", "parent_issue_body_at_pr_time_archived",
    "independent_pre_fix_task_spec_approved",
    "source_rights_cleared", "held_out_oracle_approved",
    "third_party_code_executed", "executable_task_admitted",
    "source_observations",
))
_OBSERVATION = frozenset(("id", "path", "git_blob_sha", "evidence_level"))
_EXPECTED = {
    "FILE_LAYOUT_PATH_COMPLETION": (
        "src/PersistenceHandler/FilePersistenceHandler.php",
        "1edebb766b53d2117972a8bafaff27d716b55163"),
    "FILE_LAYOUT_BASENAME_ENCODING": (
        "src/PersistenceHandler/FilePersistenceHandler.php",
        "1edebb766b53d2117972a8bafaff27d716b55163"),
    "SERIALIZED_RESOURCE_WRITER": (
        "src/PersistenceHandler/FileSerializedResourcePersistenceHandler.php",
        "96d3e275e091c50d510687a3d9bbf75b4c69c369"),
    "CACHE_LOOKUP_AND_FRESHNESS": (
        "src/Filter/Prefetch/CachedResourceFilter.php",
        "7674093fb5be90b082cbd2b35565cf506944d9fa"),
    "CACHE_TEST_FIXTURE_LAYOUT_DUPLICATION": (
        "tests/Filter/Prefetch/CachedResourceFilterTest.php",
        "e6c9e6e2ad94c69b8ec55c77642f341626cf601e"),
}


def _utc(value: object) -> datetime:
    if type(value) is not str:
        raise ValueError("date-time string required")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid date-time") from exc
    if t.tzinfo is None:
        raise ValueError("timezone-aware date-time required")
    return t.astimezone(timezone.utc)


def verify_php104_source_contract_leads(
    payload: Mapping, chronology: dict, pre_fix_trees: dict, dossiers: list,
) -> dict:
    """Cross-link PHP parent issue chronology and immutable base Git file IDs.

    The claim taxonomy is deliberately fixed; neither free-text task
    requirements, issue bodies, PR-head patches nor any oracle verdict can
    enter the checked artifact. No independent reviewer is simulated.
    """
    if (type(payload) is not dict or set(payload) != _TOP
            or payload["schema_version"] != "1.0"
            or payload["stage"] != "PHP104_READ_ONLY_BASE_SOURCE_CONTRACT_LEADS"):
        raise ValueError("unexpected PHP source audit fields or admission stage")
    try:
        observed_date = date.fromisoformat(payload["observed_on"])
        if observed_date.isoformat() != payload["observed_on"]:
            raise ValueError("noncanonical observation date")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid observation date") from exc
    issue_summary = verify_issue_prepr_chronology(chronology, dossiers)
    tree_summary = check_pre_fix_tree_inventory(pre_fix_trees, dossiers)
    if issue_summary["qualified_executable_tasks"] != 0 or tree_summary[
            "scientifically_admitted_tasks"] != 0:
        raise ValueError("no source admission authority")
    if type(payload["candidate_id"]) is not int or payload["candidate_id"] != 104:
        raise ValueError("PHP 104 identity required")
    issue = next(x for x in chronology["records"] if x["candidate_id"] == 104)
    tree = next(x for x in pre_fix_trees["records"] if x["candidate_id"] == 104)
    if (payload["repository"] != issue["repository"]
            or payload["child_issue_url"] != issue["issue_url"]
            or payload["base_commit"] != issue["pr_base_sha"]
            or payload["base_commit"] != tree["base_commit"]
            or payload["base_tree_sha"] != tree["base_tree_sha"]
            or payload["parent_issue_url"] !=
            "https://github.com/mvdbos/php-spider/issues/166"):
        raise ValueError("parent/child/PR/base Git identity mismatch")
    for field in (
        "parent_issue_body_at_pr_time_archived",
        "independent_pre_fix_task_spec_approved",
        "source_rights_cleared", "held_out_oracle_approved",
        "third_party_code_executed", "executable_task_admitted",
    ):
        if payload[field] is not False:
            raise ValueError("cannot self-approve external source or task gate")
    parent_at = _utc(payload["parent_issue_created_at"])
    parent_updated = _utc(payload["parent_issue_updated_at"])
    child_at = _utc(issue["issue_created_at"])
    pr_at = _utc(issue["pr_created_at"])
    if not parent_at < child_at < pr_at:
        raise ValueError("parent/child/PR creation order invalid")
    if parent_updated < parent_at:
        raise ValueError("parent update before creation")
    if parent_at.date() > observed_date or parent_updated.date() > observed_date:
        raise ValueError("source event after observation day")
    observations = payload["source_observations"]
    if (type(observations) is not list
            or len(observations) != len(_EXPECTED)):
        raise ValueError("exactly five pre-fix code observation leads required")
    seen = set()
    existing = {
        x["path"]: x["git_blob_sha"] for x in tree["observed_existing_source"]
    }
    for row in observations:
        if type(row) is not dict or set(row) != _OBSERVATION:
            raise ValueError("unexpected source observation or hidden leakage field")
        key = row["id"]
        if type(key) is not str or key not in _EXPECTED or key in seen:
            raise ValueError("unknown or repeated bounded source observation")
        seen.add(key)
        if (row["path"], row["git_blob_sha"]) != _EXPECTED[key]:
            raise ValueError("pre-fix Git blob/path differs from pinned observation")
        if row["path"] in existing and existing[row["path"]] != row["git_blob_sha"]:
            raise ValueError("source claim differs from canonical tree inventory")
        if row["evidence_level"] != "READ_ONLY_UNEXECUTED_SOURCE_OBSERVATION":
            raise ValueError("observed source alone cannot certify behavior")
    if seen != set(_EXPECTED):
        raise ValueError("incomplete or inconsistent contract-lead catalogue")
    return {
        "status": "SOURCE_ERA_BEHAVIOR_LEADS_REQUIRE_INDEPENDENT_ORACLE_REVIEW",
        "candidate_id": 104,
        "parent_created_before_child_seconds": int(
            (child_at - parent_at).total_seconds()),
        "parent_created_before_pr_seconds": int((pr_at - parent_at).total_seconds()),
        "child_created_before_pr_seconds": int((pr_at - child_at).total_seconds()),
        "read_only_source_observation_leads": len(seen),
        "distinct_pinned_pre_fix_blobs": len(set(_EXPECTED.values())),
        "original_issue_body_at_pr_creation_verified": False,
        "source_rights_cleared": False,
        "independent_functional_oracles_verified": 0,
        "executable_tasks_admitted": 0,
        "third_party_code_executed": False,
        "never_agent_visible": True,
    }
