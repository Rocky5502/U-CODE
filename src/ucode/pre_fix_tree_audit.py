"""Cross-check pinned read-only pre-fix Git tree metadata with original PR dossiers.

Cannot authenticate remote Git API contents or execute repo code; safeguards
source paths, immutable identifiers and zero-task promotion. It is NOT a
safe source checkout, rootless runner, independent oracle or rights review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .task_admission import parse_dossier

_SHA = re.compile(r"^[0-9a-f]{40}$")
_REL = re.compile(r"^(?!/)(?!.*[\\\x00])[^:]+$")
_ALLOWED = frozenset({
    "candidate_id", "repository", "pr_url", "base_commit", "base_tree_sha",
    "tree_recursion_truncated", "observed_tree_entries",
    "baseline_root_license_blob_sha", "toolchain_metadata",
    "observed_existing_source", "observed_expected_new_source_not_at_base",
    "base_tree_structure_verified", "real_build_executed",
    "source_code_downloaded", "source_file_redistribution_approved",
    "independent_oracle_verified", "experiment_eligible",
})


def _relative_path(path):
    return (type(path) is str and bool(path) and len(path) <= 512
            and _REL.fullmatch(path) is not None and all(
                part not in ("", ".", "..") for part in path.split("/")))


def _hashed_items(items, field):
    if type(items) is not list:
        raise ValueError(field + " must contain observed path and git blob pairs")
    seen = set()
    for x in items:
        if (type(x) is not dict or set(x) != {"path", "git_blob_sha"}
                or not _relative_path(x["path"]) or
                not isinstance(x["git_blob_sha"], str)
                or not _SHA.fullmatch(x["git_blob_sha"])):
            raise ValueError("invalid path or git blob ID in " + field)
        if x["path"] in seen:
            raise ValueError("duplicate relative path in " + field)
        seen.add(x["path"])
    return seen


def check_pre_fix_tree_inventory(snapshot, original_dossiers):
    if (type(snapshot) is not dict
            or snapshot.get("stage") != (
                "OFFICIAL_GITHUB_PRE_FIX_COMMIT_TREE_METADATA_ONLY_NO_SOURCE_CLONES")
            or type(snapshot.get("records")) is not list
            or len(snapshot["records"]) != 2):
        raise ValueError("two candidate source-only tree records required")
    by_id = {}
    for raw in original_dossiers:
        task = parse_dossier(raw)
        if task.candidate_id in by_id:
            raise ValueError("duplicate original admission dossier ID")
        by_id[task.candidate_id] = task
    if len(by_id) != 2:
        raise ValueError("expected original two PHP/Go admission dossiers")
    original_by_id = {x["candidate_id"]: x for x in original_dossiers}
    results, seen = [], set()
    for row in snapshot["records"]:
        if type(row) is not dict or set(row) != _ALLOWED:
            raise ValueError("tree inventory schema drift / post-fix leakage")
        cid = row["candidate_id"]
        if type(cid) is not int or cid not in by_id or cid in seen:
            raise ValueError("unknown or duplicate candidate tree inventory")
        seen.add(cid)
        original, task = original_by_id[cid], by_id[cid]
        if (row["repository"] != task.repository
                or row["pr_url"] != task.pr_url
                or row["base_commit"] != task.base_sha
                or row["baseline_root_license_blob_sha"]
                != original["root_license_blob_sha"]):
            raise ValueError("tree inventory differs from canonical PR/license blob")
        if (type(row["base_tree_sha"]) is not str
                or not _SHA.fullmatch(row["base_tree_sha"])
                or row["base_tree_sha"] == row["base_commit"]):
            raise ValueError("actual Git tree object SHA required, not commit SHA")
        if (row["tree_recursion_truncated"] is not False
                or type(row["observed_tree_entries"]) is not int
                or not 1 <= row["observed_tree_entries"] <= 100000):
            raise ValueError("complete plausible tree-index size required")
        for name in ("real_build_executed", "source_code_downloaded",
                     "source_file_redistribution_approved",
                     "independent_oracle_verified", "experiment_eligible"):
            if row[name] is not False:
                raise ValueError("pre-fix source paths do not authorize execution")
        if row["base_tree_structure_verified"] is not True:
            raise ValueError("no claimed read-only tree observation")
        toolchains = _hashed_items(row["toolchain_metadata"], "toolchain_metadata")
        existing = _hashed_items(row["observed_existing_source"],
                                 "observed_existing_source")
        expected = row["observed_expected_new_source_not_at_base"]
        if (type(expected) is not list
                or any(not _relative_path(x) for x in expected)
                or len(set(expected)) != len(expected)):
            raise ValueError("invalid expected new source path")
        prod = set(task.changed_production_paths)
        if (not existing or not existing <= prod
                or not set(expected) <= prod
                or existing & set(expected)
                or existing & toolchains
                or set(expected) & toolchains):
            raise ValueError("observed base file identity contradicts changed production paths")
        results.append({
            "candidate_id": cid,
            "repository": task.repository,
            "base_commit": task.base_sha,
            "base_tree_sha": row["base_tree_sha"],
            "observed_base_existing_sources": len(existing),
            "observed_base_absent_new_sources": len(expected),
            "observed_base_toolchain_metadata_files": len(toolchains),
            "safe_checkout_or_build_verified": False,
            "independent_oracle_verified": False,
            "experiment_eligible": False,
        })
    return {
        "stage": "PRE_FIX_TREE_METADATA_RECONCILED_NOT_RUNNABLE",
        "inventory_records": len(results),
        "read_only_tree_paths_observed": sum(
            x["observed_base_existing_sources"] for x in results),
        "toolchain_config_paths_observed": sum(
            x["observed_base_toolchain_metadata_files"] for x in results),
        "scientifically_admitted_tasks": 0,
        "real_builds_executed": 0,
        "records": sorted(results, key=lambda r: r["candidate_id"]),
    }


def verify_tree_snapshot(path: Path, dossiers_path: Path):
    raw = json.loads(Path(path).read_text("utf-8"))
    original = [json.loads(line) for line in
                Path(dossiers_path).read_text("utf-8").splitlines()
                if line.strip()]
    return check_pre_fix_tree_inventory(raw, original)
