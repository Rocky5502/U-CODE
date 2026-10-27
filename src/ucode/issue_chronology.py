"""Check real GitHub issue/PR chronology against frozen candidate admission data.

An issue being CREATED before a PR is NOT evidence that its observed body
was unchanged or that a task-era oracle exists. This tool stores metadata,
never issue descriptions, source patches, test data or execution results.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import re

from .task_admission import parse_dossier

_FIELDS = frozenset({
    "candidate_id", "repository", "pr_number", "issue_number",
    "issue_url", "pr_url", "issue_title", "issue_created_at",
    "issue_updated_at", "issue_body_chars_observed", "pr_created_at",
    "pr_base_sha", "pr_head_sha", "pr_body_closing_reference_verified",
    "issue_text_at_pr_creation_immutably_archived",
    "source_issue_is_pull_request", "independently_verified_pre_pr_specification",
    "independent_oracle_verified", "source_rights_verified",
    "executable_task_approved",
})


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("ISO8601 string required")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO8601 timestamp") from exc
    if t.tzinfo is None:
        raise ValueError("timezone-aware GitHub timestamp required")
    return t.astimezone(timezone.utc)


def verify_issue_prepr_chronology(payload: dict, reviewer_packets) -> dict:
    """Fails closed on altered canonical metadata, unexpected authorizations."""
    if type(payload) is not dict or payload.get("status") != (
            "TWO_REAL_PR_CHRONOLOGY_LEADS_NOT_EXECUTABLE_TASKS"):
        raise ValueError("expected unapproved read-only issue audit")
    entries = payload.get("records")
    if type(entries) is not list or len(entries) != 2:
        raise ValueError("two read-only issue samples required")
    packet_by_id = {
        p["candidate_id"]: parse_dossier(p) for p in reviewer_packets
    }
    if len(packet_by_id) != len(reviewer_packets):
        raise ValueError("duplicate canonical reviewer candidate")
    seen, results = set(), []
    for row in entries:
        if type(row) is not dict or set(row) != _FIELDS:
            raise ValueError("unexpected issue metadata/possible oracle leakage")
        idx = row["candidate_id"]
        if type(idx) is not int or idx not in packet_by_id or idx in seen:
            raise ValueError("issue sample ID not in unique canonical review shortlist")
        seen.add(idx)
        d = packet_by_id[idx]
        repo = row["repository"]
        pr_no, issue_no = row["pr_number"], row["issue_number"]
        if type(pr_no) is not int or type(issue_no) is not int or pr_no <= 0 or issue_no <= 0:
            raise ValueError("invalid PR/issue number")
        if (repo != d.repository or row["pr_url"] != d.pr_url
                or row["pr_base_sha"] != d.base_sha
                or row["pr_head_sha"] != d.head_sha
                or row["pr_url"] != f"https://github.com/{repo}/pull/{pr_no}"
                or row["issue_url"] != f"https://github.com/{repo}/issues/{issue_no}"):
            raise ValueError("issue record identity or immutable PR SHA mismatch")
        if (type(row["issue_title"]) is not str
                or not row["issue_title"].strip()
                or type(row["issue_body_chars_observed"]) is not int
                or row["issue_body_chars_observed"] < 0):
            raise ValueError("invalid read-only issue summary")
        for key in (
            "issue_text_at_pr_creation_immutably_archived",
            "source_issue_is_pull_request",
            "independently_verified_pre_pr_specification",
            "independent_oracle_verified", "source_rights_verified",
            "executable_task_approved",
        ):
            if row[key] is not False:
                raise ValueError("issue audit cannot self-promote missing evidence")
        if row["pr_body_closing_reference_verified"] is not True:
            raise ValueError("recorded PR-to-issue link not verified")
        t_issue = _timestamp(row["issue_created_at"])
        t_updated = _timestamp(row["issue_updated_at"])
        t_pr = _timestamp(row["pr_created_at"])
        if t_updated < t_issue:
            raise ValueError("issue updated before issue creation")
        lag = int((t_pr - t_issue).total_seconds())
        if lag < 0:
            raise ValueError("supposed pre-PR issue was actually created after PR")
        results.append({
            "candidate_id": idx,
            "repository": repo,
            "issue_url": row["issue_url"],
            "lead_time_seconds": lag,
            "source_body_unchanged_at_pr_creation": "UNVERIFIED",
            "immutable_prefixed_issue_specification_verified": False,
            "review_priority": (
                "VERY_SHORT_PREPR_WINDOW_MANUAL_CONTEXT_CHECK"
                if lag < 60 else "TASK_ERA_BODY_VERSION_HISTORY_REVIEW"
            ),
            "task_admitted": False,
        })
    return {
        "status": "READ_ONLY_CHRONOLOGY_NOT_TASK_SPEC_VERIFICATION",
        "sample_count": 2,
        "source_issue_created_before_pr": 2,
        "issue_body_time_travel_verified": 0,
        "qualified_executable_tasks": 0,
        "third_party_code_executed": False,
        "records": sorted(results, key=lambda x: x["candidate_id"]),
    }


def load_and_verify(path: Path, reviewer_packets):
    return verify_issue_prepr_chronology(
        json.loads(Path(path).read_text("utf-8")), reviewer_packets)
