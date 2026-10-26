"""Deterministic metadata-only PR screening for U-CODE.

All 120 discovered links stay in the denominator. Source-path review leads are
NOT executable tasks, passed oracles, per-line AI attribution, or cleared rights.
No external downloads or repository code execution; standard library only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from scripts.summarize_audit import ALLOWED_STATES
from ucode.review_queue import rank_candidate

LANGUAGES = ("Python", "JavaScript", "TypeScript", "Java", "Go", "Rust",
             "C++", "C", "C#", "Kotlin", "PHP", "Ruby")
COLUMNS = (
    "candidate_id", "repository", "pr_url", "search_language",
    "observed_production_languages", "changed_production_file_count",
    "changed_test_file_count", "audit_status", "metadata_source_status",
    "base_sha", "head_sha", "merge_commit_sha", "lineage_group_hint",
    "lineage_group_review", "repository_license_spdx_metadata",
    "source_rights_verified", "line_attribution_verified",
    "sealed_independent_oracle_verified", "sandbox_verified",
    "priority_class", "manual_review_reasons", "review_shortlist",
    "experiment_eligible", "split_status",
)
REVIEW_FIELDS = ("candidate_id", "repository", "pr_url",
                 "search_language", "observed_production_languages",
                 "priority_class", "manual_review_reasons",
                 "experiment_eligible")
SUMMARY_FIELDS = ("search_language", "discovered_prs",
                  "metadata_retrieved", "source_path_leads",
                  "first_pass_metadata_leads", "source_language_matched",
                  "source_language_mismatched_or_unobserved",
                  "shortlisted_for_manual_review", "experiment_eligible")
RECOVERABLE = {"retrieval_failed", "rate_limited", "not_attempted_rate_limit"}
SHA40 = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class CuratedDataset:
    rows: tuple[dict, ...]
    review_queue: tuple[dict, ...]
    language_summary: tuple[dict, ...]
    report: dict


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _github_pr_matches(repo: str, url: str) -> bool:
    p = urlparse(url)
    parts = p.path.strip("/").split("/")
    return (p.scheme == "https" and p.netloc.lower() == "github.com"
            and not p.username and not p.password and not p.query
            and len(parts) == 4 and parts[2] == "pull"
            and parts[3].isdigit() and int(parts[3]) > 0
            and "/".join(parts[:2]).lower() == repo.lower())


def _sha40(value: object) -> bool:
    return type(value) is str and len(value) == 40 and all(c in SHA40 for c in value)


def _known_rights(record: dict) -> bool:
    # An SPDX label on a repository root NEVER clears modified source files.
    return False


def _paths(record: dict):
    paths = record.get("production_files") or []
    tests = record.get("test_files")
    if tests is None:
        # Pre-2026-10-25 audit subset omits the test_files key.
        from ucode.audit import is_source_path, is_test_path
        tests = [p for p in (record.get("changed_paths") or [])
                 if is_source_path(p) and is_test_path(p)]
    if not isinstance(paths, list) or not isinstance(tests, list):
        raise ValueError("changed source/test paths must be lists")
    if any(type(x) is not str or not x for x in paths+tests):
        raise ValueError("malformed path")
    return paths, tests


def build_dataset(manifest: dict[int, dict], audit: list[dict],
                  source_manifest_sha256: str = "",
                  max_review: int = 12) -> CuratedDataset:
    if not manifest or type(max_review) is not int or not 0 <= max_review <= len(manifest):
        raise ValueError("nonempty manifest and valid review budget required")
    if len(audit) != len(manifest):
        raise ValueError("audit must explicitly account for EVERY discovered PR")
    index = {}
    for item in audit:
        cid = item.get("candidate_id")
        if type(cid) is not int or cid not in manifest or cid in index:
            raise ValueError("missing, unexpected or duplicate canonical audit ID")
        index[cid] = item
    rows = []
    seen_pr, seen_repo = set(), set()
    for cid in sorted(manifest):
        m, item = manifest[cid], index[cid]
        repo = m["repository"]
        url = m["agent_pr_url"]
        query_lang = m["query_language"]
        if query_lang not in LANGUAGES:
            raise ValueError("unexpected primary-language stratum")
        if item.get("repository") != repo or item.get("pr_url") != url:
            raise ValueError("canonical audit identity mismatch")
        if not _github_pr_matches(repo, url):
            raise ValueError("invalid Github PR URL, mismatch or unsafe query")
        if url.casefold() in seen_pr or repo.casefold() in seen_repo:
            raise ValueError("duplicate PR or repository; review group overlap")
        seen_pr.add(url.casefold())
        seen_repo.add(repo.casefold())
        status = item.get("triage_status")
        if status not in ALLOWED_STATES:
            raise ValueError("unrecognized audit triage status")
        if item.get("dataset_eligible") is not False:
            raise ValueError("no PR may self-promote to executable/eligible")
        if item.get("rights_cleared") is True or item.get("independent_oracle_verified") is True:
            raise ValueError("unreviewed rights or oracle may not be promoted")
        if item.get("test_execution") not in ("NOT_RUN", None):
            raise ValueError("external execution is not authorized")
        prod, tests = _paths(item)
        if status == "production_source_path_detected" and not prod:
            raise ValueError("production-source status needs source paths")
        if status != "production_source_path_detected" and prod:
            raise ValueError("non-production audit cannot carry production paths")
        shas = tuple(item.get(k) or "" for k in
                     ("base_sha", "head_sha", "merge_commit_sha"))
        if status not in RECOVERABLE and not all(_sha40(v) for v in shas):
            raise ValueError("retrieved PR needs immutable 40-hex base/head/merge SHAs")
        if any(v and not _sha40(v) for v in shas):
            raise ValueError("malformed present immutable SHA")
        observed = item.get("production_languages") or []
        if not isinstance(observed, list) or any(
            not isinstance(x, str) or not x for x in observed
        ):
            raise ValueError("invalid observed changed-path language")
        if not prod and observed:
            raise ValueError("no production file implies no observed production language")
        # Fork grouping is a HINT only: manual related-repo/alias review still needed.
        parent = item.get("parent_repo") if item.get("fork") else None
        if parent is not None and (not isinstance(parent, str) or "/" not in parent):
            raise ValueError("invalid fork parent")
        group = (parent or repo).casefold()
        lead = rank_candidate(item)
        priority = lead.priority_class if lead is not None else "excluded_from_source_review"
        reasons = list(lead.reasons) if lead else [status]
        if observed and query_lang not in observed:
            reasons.append("search_language_differs_from_production_path_language")
        if not observed and prod:
            reasons.append("changed_production_language_not_observed")
        if item.get("fork") and not parent:
            reasons.append("fork_parent_missing")
        rows.append({
            "candidate_id": cid,
            "repository": repo,
            "pr_url": url,
            "search_language": query_lang,
            "observed_production_languages": "|".join(sorted(set(observed))),
            "changed_production_file_count": len(prod),
            "changed_test_file_count": len(tests),
            "audit_status": status,
            "metadata_source_status": "retrieval_failed_or_unattempted"
                                      if status in RECOVERABLE else "retrieved",
            "base_sha": shas[0], "head_sha": shas[1], "merge_commit_sha": shas[2],
            "lineage_group_hint": group,
            "lineage_group_review": "PENDING_INDEPENDENT_REVIEW",
            "repository_license_spdx_metadata": str(item.get("repository_license_spdx") or ""),
            "source_rights_verified": "FALSE",
            "line_attribution_verified": "FALSE",
            "sealed_independent_oracle_verified": "FALSE",
            "sandbox_verified": "FALSE",
            "priority_class": priority,
            "manual_review_reasons": "|".join(sorted(set(reasons))),
            "review_shortlist": "FALSE",
            "experiment_eligible": "FALSE",
            "split_status": "NOT_SPLIT_LINEAGE_AND_TASK_ADMISSION_PENDING",
        })
    # A diversity-first SHORTLIST for manual work, not a final experimental sample.
    # Iterate priority strata and distinct query languages before repeating one.
    selected = []
    for cls in ("first_pass_manual_review", "second_pass_manual_review"):
        per_language = defaultdict(list)
        for row in rows:
            if row["priority_class"] == cls:
                per_language[row["search_language"]].append(row)
        for lng in LANGUAGES:
            per_language[lng].sort(key=lambda x: (
                0 if x["changed_test_file_count"] else 1,
                x["changed_production_file_count"], x["candidate_id"]))
        while any(per_language.values()) and len(selected) < max_review:
            for lng in LANGUAGES:
                if per_language[lng] and len(selected) < max_review:
                    selected.append(per_language[lng].pop(0))
        if len(selected) >= max_review:
            break
    chosen = {r["candidate_id"] for r in selected}
    for row in rows:
        row["review_shortlist"] = "TRUE" if row["candidate_id"] in chosen else "FALSE"
    order = {r["candidate_id"]: i for i, r in enumerate(selected)}
    shortlist = tuple({
        field: row[field] for field in REVIEW_FIELDS
    } for row in sorted(selected, key=lambda r: order[r["candidate_id"]]))
    summary = []
    for language in LANGUAGES:
        subset = [r for r in rows if r["search_language"] == language]
        src = [r for r in subset if r["audit_status"] == "production_source_path_detected"]
        summary.append({
            "search_language": language, "discovered_prs": len(subset),
            "metadata_retrieved": sum(r["metadata_source_status"] == "retrieved" for r in subset),
            "source_path_leads": len(src),
            "first_pass_metadata_leads": sum(
                r["priority_class"] == "first_pass_manual_review" for r in subset),
            "source_language_matched": sum(
                language in r["observed_production_languages"].split("|") for r in src),
            "source_language_mismatched_or_unobserved": sum(
                language not in r["observed_production_languages"].split("|") for r in src),
            "shortlisted_for_manual_review": sum(
                r["review_shortlist"] == "TRUE" for r in subset),
            "experiment_eligible": 0,
        })
    counts = Counter(r["audit_status"] for r in rows)
    by_changed_lang = Counter(
        lang for r in rows for lang in
        r["observed_production_languages"].split("|") if lang)
    report = {
        "schema_version": "1.0",
        "stage": "METADATA_ONLY_NO_EXECUTABLE_TASK_ADMISSION",
        "discovery_manifest_sha256": source_manifest_sha256,
        "discovered_pr_links": len(rows),
        "distinct_repository_names": len(seen_repo),
        "search_language_strata": len(LANGUAGES),
        "language_strata_count": {x["search_language"]: x["discovered_prs"]
                                  for x in summary},
        "metadata_retrieved": sum(r["metadata_source_status"] == "retrieved" for r in rows),
        "metadata_not_retrieved": sum(r["metadata_source_status"] != "retrieved" for r in rows),
        "status_counts": dict(sorted(counts.items())),
        "production_source_path_leads": counts.get("production_source_path_detected", 0),
        "changed_path_language_counts_not_task_counts": dict(sorted(by_changed_lang.items())),
        "source_language_mismatched_or_unobserved_leads": sum(
            r["source_language_mismatched_or_unobserved"] for r in summary),
        "first_pass_manual_review_leads": sum(
            r["priority_class"] == "first_pass_manual_review" for r in rows),
        "shortlisted_for_manual_review": len(shortlist),
        "independently_approved_executable_tasks": 0,
        "source_code_downloaded": False,
        "external_code_executed": False,
        "independent_train_test_split_frozen": False,
        "strata_meaning": "GitHub SEARCH language, not necessarily changed source language",
        "review_queue_is_not_an_experiment": True,
    }
    if any(x["experiment_eligible"] != "FALSE" for x in rows):
        raise ValueError("false task promotion")
    if sum(x["discovered_prs"] for x in summary) != len(rows):
        raise ValueError("missing or duplicated strata in language aggregation")
    return CuratedDataset(tuple(rows), shortlist, tuple(summary), report)


def as_csv(rows, fields) -> str:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n",
                            extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow({f: row[f] for f in fields})
    return out.getvalue()


def write_dataset(dataset: CuratedDataset, output_dir: str | Path) -> dict[str, str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "clean_metadata_120.csv": as_csv(dataset.rows, COLUMNS),
        "language_strata.csv": as_csv(dataset.language_summary, SUMMARY_FIELDS),
        "manual_review_12_NOT_EXECUTABLE.csv": as_csv(dataset.review_queue, REVIEW_FIELDS),
        "cleaning_report.json": json.dumps(dataset.report, sort_keys=True, indent=2) + "\n",
    }
    for name, text in artifacts.items():
        (root/name).write_text(text, encoding="utf-8", newline="")
    return {name: _sha_text(text) for name, text in artifacts.items()}
