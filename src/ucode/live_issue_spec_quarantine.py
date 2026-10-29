"""Fail-closed screening of present-day GitHub issue descriptions.

An issue's creation timestamp does NOT timestamp its current body. An Events or
Timeline page cannot be used as a version-control history of the issue body.
This module consumes metadata only and *never* authorizes task/policy access.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

_TOP = frozenset(("schema_version", "stage", "observed_on", "records"))
_ROW = frozenset((
    "candidate_id", "repository", "issue_url", "source_kind", "observed_at",
    "observed_issue_updated_at", "body_text_stored", "original_body_verified",
    "independent_spec_approval", "task_admitted",
))
_KIND = "CURRENT_LIVE_GITHUB_ISSUE"


def _utc(value: object) -> datetime:
    if type(value) is not str or not value.endswith("Z"):
        raise ValueError("timestamp must be canonical UTC Z")
    try:
        out = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if out.tzinfo is None or out.utcoffset().total_seconds() != 0:
        raise ValueError("UTC timezone required")
    if out.isoformat(timespec="seconds").replace("+00:00", "Z") != value:
        raise ValueError("timestamp must have seconds precision")
    return out.astimezone(timezone.utc)


def audit_live_issue_observations(observations: Mapping, chronology: Mapping) -> dict:
    """Strictly bound post-PR observations to pinned PHP/Go public source IDs.

    This is NOT an archival-capture verifier and has no positive admission
    state. Public observation, repository metadata, self-asserted flags and
    content hashes are never substitutes for independent source-era review.
    """
    if (type(observations) is not dict or set(observations) != _TOP
            or observations.get("schema_version") != "1.0"
            or observations.get("stage") != "LIVE_ISSUE_BODY_REVIEW_ONLY"):
        raise ValueError("invalid source-observation schema")
    day = observations["observed_on"]
    if type(day) is not str or len(day) != 10:
        raise ValueError("observation date must be canonical YYYY-MM-DD")
    try:
        from datetime import date
        parsed_day = date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError("invalid observation date") from exc
    if parsed_day.isoformat() != day:
        raise ValueError("noncanonical observation date")
    if (type(chronology) is not dict or chronology.get("schema_version") != "1.0"
            or type(chronology.get("records")) is not list):
        raise ValueError("missing source-era chronology")
    canonical = {}
    for source in chronology["records"]:
        if type(source) is not dict:
            raise ValueError("invalid chronology row")
        idx = source.get("candidate_id")
        if type(idx) is not int or idx in canonical:
            raise ValueError("duplicate/invalid source candidate")
        canonical[idx] = source
    if set(canonical) != {43, 104}:
        raise ValueError("unexpected canonical candidate roster")
    if type(observations["records"]) is not list or len(observations["records"]) != 2:
        raise ValueError("exactly two live issue observations required")
    output, seen = [], set()
    for item in observations["records"]:
        if type(item) is not dict or set(item) != _ROW:
            raise ValueError("unrecognized observation field or solution/oracle leakage")
        idx = item["candidate_id"]
        if type(idx) is not int or idx not in canonical or idx in seen:
            raise ValueError("unknown or repeated candidate")
        seen.add(idx)
        src = canonical[idx]
        if (item["repository"] != src["repository"]
                or item["issue_url"] != src["issue_url"]):
            raise ValueError("issue identity differs from original task")
        if item["source_kind"] != _KIND:
            raise ValueError("current issue review is not an immutable archive")
        for flag in ("body_text_stored", "original_body_verified",
                     "independent_spec_approval", "task_admitted"):
            if item[flag] is not False:
                raise ValueError("public observation cannot self-authorize or contain body")
        created = _utc(src["issue_created_at"])
        cutoff = _utc(src["pr_created_at"])
        updated = _utc(item["observed_issue_updated_at"])
        observed = _utc(item["observed_at"])
        if not created < cutoff:
            raise ValueError("issue did not precede PR in frozen chronology")
        if not created <= updated <= observed:
            raise ValueError("live issue update/observation chronology invalid")
        if observed.date().isoformat() != day:
            raise ValueError("observation timestamp/date mismatch")
        if observed < cutoff:
            raise ValueError("current live issue observation predates PR cutoff")
        output.append({
            "candidate_id": idx,
            "repository": src["repository"],
            "issue_to_pr_seconds": int((cutoff-created).total_seconds()),
            "current_issue_updated_after_pr": updated > cutoff,
            "issue_text_as_of_pr": "NOT_PROVEN",
            "policy_input_eligible": False,
            "independent_oracle_verified": False,
            "task_admitted": False,
        })
    if seen != set(canonical):
        raise ValueError("missing original issue observation")
    return {
        "status": "POST_PR_CURRENT_ISSUE_TEXT_QUARANTINED",
        "historical_issue_body_snapshots_verified": 0,
        "independent_functional_oracles_verified": 0,
        "eligible_real_tasks": 0,
        "external_code_executions": 0,
        "records": sorted(output, key=lambda row: row["candidate_id"]),
    }
