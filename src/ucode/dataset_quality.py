"""Source-free technical validation of U-CODE's PR *metadata* dataset.

This is a DATA QUALITY audit, not source-code rights review, task admission,
independent oracle construction, secure execution, or proof of AI line authorship.
Evidence is preserved at one PR-link per discovery record (120 total).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import re

from .dataset_curation import CuratedDataset, LANGUAGES, COLUMNS

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PASSIVE_STATES = {"source_rights_verified", "line_attribution_verified",
                  "sealed_independent_oracle_verified", "sandbox_verified",
                  "experiment_eligible"}
REJECT_TASK_FIELDS = frozenset({"gold_patch", "oracle_output", "test_passed",
                                "ground_truth", "task_success", "hidden_tests"})


@dataclass(frozen=True)
class DatasetValidation:
    checks: tuple[dict, ...]
    report: dict
    reviewer_leakage_flags: tuple[dict, ...]


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dataset_schema() -> dict:
    columns = {}
    for field in COLUMNS:
        if field in ("candidate_id", "changed_production_file_count",
                     "changed_test_file_count"):
            dtype = "nonnegative_integer"
        else:
            dtype = "string"
        role = (
            "identifier" if field in ("candidate_id", "repository", "pr_url")
            else "unverified_privilege_flag" if field in PASSIVE_STATES
            else "metadata_only"
        )
        columns[field] = {"type": dtype, "role": role, "nullable": False}
    columns["base_sha"]["nullable"] = True
    columns["head_sha"]["nullable"] = True
    columns["merge_commit_sha"]["nullable"] = True
    columns["repository_license_spdx_metadata"]["nullable"] = True
    columns["observed_production_languages"]["nullable"] = True
    return {
        "schema_version": "1.0",
        "grain": "ONE_DISCOVERED_GITHUB_PULL_REQUEST_LINK_PER_REPOSITORY_NAME",
        "columns": columns,
        "field_notes": {
            "search_language": "GitHub query-language stratum; not necessarily language of changed production files",
            "observed_production_languages": "Pipe-separated source suffix classifications; not a definitive language label",
            "lineage_group_hint": "Casefolded repository/fork-parent hint, not adjudicated project family",
            "manual_review_reasons": "Nonexclusive conservative flags; not an oracle",
            "priority_class": "Metadata-only manual-review ranking, never executable eligibility",
            "source_rights_verified": "Always FALSE until external file-level reviewer attests",
            "sealed_independent_oracle_verified": "Always FALSE in this release",
            "split_status": "Never frozen or labeled leakage-free in this release",
            "base_sha": "Audited PR base reference metadata; pre-fix runnable environment not verified",
            "head_sha": "Post-PR patch reference; must NEVER be exposed as task-solving input",
            "merge_commit_sha": "Post-PR reference; never an independent hidden evaluator oracle",
        },
        "disallowed_in_release": sorted(REJECT_TASK_FIELDS),
        "scientific_task_admission": "NONE",
    }


def validate_release(data: CuratedDataset, audits: list[dict]) -> DatasetValidation:
    if not isinstance(data, CuratedDataset):
        raise TypeError("CuratedDataset input required")
    rows = data.rows
    if len(rows) != 120 or len(audits) != 120:
        raise ValueError("full 120-link denominator required")
    if len({r["candidate_id"] for r in rows}) != 120:
        raise ValueError("duplicate clean candidate key")
    audit_id = {a["candidate_id"]: a for a in audits}
    if len(audit_id) != 120 or set(audit_id) != {
        r["candidate_id"] for r in rows
    }:
        raise ValueError("audit-to-clean join not exactly one-to-one")
    if any(set(r) != set(COLUMNS) for r in rows):
        raise ValueError("released clean table schema drift")
    if any(REJECT_TASK_FIELDS & set(r) for r in rows):
        raise ValueError("evaluator labels illegally exposed in public metadata")
    known_repo = set()
    known_urls = set()
    language = Counter()
    miss = Counter()
    owner_ids: dict[str, list[int]] = defaultdict(list)
    sha_occurrence: dict[str, list[tuple[int, str]]] = defaultdict(list)
    hints: dict[str, list[int]] = defaultdict(list)
    flags = []
    for row in rows:
        cid = row["candidate_id"]
        rec = audit_id[cid]
        repo = row["repository"]
        if type(cid) is not int or type(repo) is not str or repo.count("/") != 1:
            raise ValueError("invalid primary PR and repository identifiers")
        if any(type(row[k]) is not int or row[k] < 0 for k in (
                "changed_production_file_count", "changed_test_file_count")):
            raise ValueError("invalid changed source/test file count")
        if (repo.casefold() in known_repo
            or row["pr_url"].casefold() in known_urls):
            raise ValueError("duplicate repository or pull-request identity")
        known_repo.add(repo.casefold())
        known_urls.add(row["pr_url"].casefold())
        if row["search_language"] not in LANGUAGES:
            raise ValueError("bad search-language stratum")
        language[row["search_language"]] += 1
        for key in PASSIVE_STATES:
            if row[key] != "FALSE":
                raise ValueError("metadata release cannot claim privileged approvals")
        if row["split_status"] != "NOT_SPLIT_LINEAGE_AND_TASK_ADMISSION_PENDING":
            raise ValueError("a lineage-safe train/test split has not been audited")
        if row["lineage_group_review"] != "PENDING_INDEPENDENT_REVIEW":
            raise ValueError("no lineage adjudication has occurred")
        if rec.get("pr_url") != row["pr_url"] or rec.get("repository") != repo:
            raise ValueError("broken raw-to-clean identity join")
        if rec.get("triage_status") != row["audit_status"]:
            raise ValueError("source status changed between raw and clean")
        observed = sorted(set(rec.get("production_languages") or []))
        if "|".join(observed) != row["observed_production_languages"]:
            raise ValueError("changed-source language evidence drift")
        prod_count = len(rec.get("production_files") or [])
        if row["changed_production_file_count"] != prod_count:
            raise ValueError("changed-source count drift")
        # Legacy audit records do not always record test_files; no unjustified
        # test-pass or hidden oracle conclusion is permitted by this number.
        for f in ("base_sha", "head_sha", "merge_commit_sha"):
            value = row[f]
            raw_value = rec.get(f) or ""
            if value != raw_value:
                raise ValueError("raw-to-clean immutable commit SHA mismatch")
            if value:
                if not HEX40.fullmatch(value):
                    raise ValueError("invalid immutable commit SHA in metadata")
                sha_occurrence[value].append((cid, f))
            elif row["metadata_source_status"] == "retrieved":
                raise ValueError("retrieved PR missing immutable SHA")
        for key in COLUMNS:
            if row[key] == "":
                miss[key] += 1
        owner_ids[repo.split("/", 1)[0].casefold()].append(cid)
        hints[row["lineage_group_hint"]].append(cid)
        reason = []
        if row["priority_class"] != "first_pass_manual_review":
            reason.append("not_first_pass_metadata_lead")
        if row["repository_license_spdx_metadata"] in (
                "", "NOASSERTION", "UNKNOWN"):
            reason.append("file_license_rights_not_established")
        if row["metadata_source_status"] != "retrieved":
            reason.append("raw_PR_metadata_not_retrieved")
        if row["search_language"] not in observed and prod_count:
            reason.append("changed_language_differs_or_unobserved")
        if rec.get("fork") or rec.get("parent_repo"):
            reason.append("fork_or_parent_lineage_review")
        if not row["changed_test_file_count"]:
            reason.append("no_changed_test_file_path_not_an_oracle")
        if reason:
            flags.append({"candidate_id": cid, "repository": repo,
                          "manual_flags": sorted(set(reason)),
                          "task_eligible": False})
    if any(language.get(s) != 10 for s in LANGUAGES):
        raise ValueError("120 PR frame must preserve 10 per each 12 search strata")
    if data.report.get("production_source_path_leads") != 62:
        raise ValueError("recompute the frozen discovery attrition baseline")
    if sum(r["review_shortlist"] == "TRUE" for r in rows) != 12:
        raise ValueError("review shortlist unexpectedly drifted")
    same_owner = {k: v for k, v in owner_ids.items() if len(v) > 1}
    same_parent_hint = {k: v for k, v in hints.items() if len(v) > 1}
    # SHA collisions by commit role can be legitimate branch ancestry; flag
    # only for human lineage review rather than automatic task deletion.
    sha_groups = {s: sorted({cid for cid, _ in ids})
                  for s, ids in sha_occurrence.items()
                  if len({cid for cid, _ in ids}) > 1}
    checks = tuple([
        {"id": "strict_grain", "status": "PASS", "records": len(rows),
         "meaning": "120 unique repository/PR identities at recorded grain"},
        {"id": "audit_join_coverage", "status": "PASS", "matched": len(audit_id),
         "meaning": "one audited metadata record per discovery row"},
        {"id": "source_language_retained", "status": "PASS", "strata": len(LANGUAGES),
         "meaning": "search strata and changed languages kept distinct"},
        {"id": "oracle_rights_leakage", "status": "PASS",
         "metadata_admissions": 0, "meaning": "no oracle/rights/task success label included"},
        {"id": "lineage_safe_split", "status": "BLOCKED",
         "meaning": "fork/alias/task-content overlap not independently adjudicated"},
        {"id": "runnable_execution", "status": "BLOCKED",
         "meaning": "no independent spec, file rights, sandbox or sealed oracle"},
    ])
    counts = data.report
    report = {
        "schema_version": "1.0",
        "quality_scope": "OFFLINE_METADATA_STRUCTURE_ONLY_NOT_CODE_OR_ORACLE_VALIDATION",
        "input_manifest_sha256": counts["discovery_manifest_sha256"],
        "candidate_pr_count": len(rows),
        "unique_repository_names": len(known_repo),
        "unique_pr_urls": len(known_urls),
        "audit_joined_rows": len(audit_id),
        "audit_outcome_counts": counts["status_counts"],
        "query_language_strata": dict(sorted(language.items())),
        "empty_metadata_cell_counts": dict(sorted(miss.items())),
        "potential_same_owner_groups_for_manual_review": dict(sorted(same_owner.items())),
        "potential_same_fork_parent_hint_groups_for_manual_review": dict(sorted(same_parent_hint.items())),
        "potential_shared_commit_sha_groups_for_manual_review": dict(sorted(sha_groups.items())),
        "manual_review_flags_count": len(flags),
        "unverified_file_rights_count": len(rows),
        "unverified_sealed_oracles_count": len(rows),
        "approved_executable_tasks": 0,
        "known_limitations": [
            "No changed-line AI provenance or file-level permissions established",
            "GitHub query language is not necessarily changed production language",
            "Changed test files are not sealed independent oracles",
            "Owner-sharing, fork hints, reused commit hashes flag potential overlap only",
            "Cross-repository near-duplicate source content not measured (source excluded)",
            "No safe train/test split or real binary executable task bundle",
            "Cannot infer AlphaCode-equivalent performance or dataset novelty",
        ],
        "checks": checks,
        "scientific_data_submission_ready": False,
    }
    return DatasetValidation(checks, report, tuple(flags))


def source_file_digests(manifest: Path, audit_paths: list[Path]) -> dict[str, str]:
    paths = [manifest, *audit_paths]
    if len(paths) != len(set(paths)):
        raise ValueError("repeated source file in provenance ledger")
    return {p.as_posix(): _digest(p.read_bytes()) for p in paths}


def release_integrity_manifest(data_files: dict[str, bytes],
                               sources: dict[str, str]) -> dict:
    if not data_files or any("/" in name or ".." in name for name in data_files):
        raise ValueError("only plain relative release filenames allowed")
    if len(set(data_files)) != len(data_files):
        raise ValueError("duplicate release filename")
    if any(len(d) != 64 or any(c not in "0123456789abcdef" for c in d)
           for d in sources.values()):
        raise ValueError("all provenance digests must be SHA256")
    return {
        "status": "DATASET_METADATA_RELEASE_NOT_EXECUTABLE",
        "hash_algorithm": "sha256",
        "source_snapshot_digests": dict(sorted(sources.items())),
        "output_digests": {
            name: {"sha256": _digest(raw), "bytes": len(raw)}
            for name, raw in sorted(data_files.items())
        },
        "no_outcome_labels": True,
        "no_data_license_approval_implied": True,
        "no_independently_verified_tasks": True,
    }
