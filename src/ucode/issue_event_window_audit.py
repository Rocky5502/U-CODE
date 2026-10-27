"""Read-only GitHub issue-event chronology; NEVER an issue-body time machine.

Events can establish some public actions around PR creation, but the issue
Events REST endpoint is not a versioned issue-text archive. Lack of an 'edited'
event cannot establish that current issue text existed before a PR. Only
reviewer-only metadata is processed here, never prompts, gold patches or tests.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from typing import Mapping
import re

from .issue_chronology import verify_issue_prepr_chronology

_EVENT_NAME = re.compile(r"^[a-z][a-z_-]{0,63}$")
_TOP = frozenset(("schema_version", "stage", "observed_on", "records"))
_RECORD = frozenset((
    "candidate_id", "repository", "issue_url", "events_api_url",
    "page_size", "full_history_verified", "issue_body_snapshot_verified",
    "task_admitted", "events",
))
_EVENT = frozenset(("event_id", "event", "created_at"))


def _utc(value: object) -> datetime:
    if type(value) is not str:
        raise ValueError("event timestamp must be a string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid event timestamp") from exc
    if result.tzinfo is None:
        raise ValueError("event timestamp must be timezone-aware")
    return result.astimezone(timezone.utc)


def verify_issue_event_windows(
    audit: Mapping, chronology: Mapping, reviewer_packets,
) -> dict:
    """Validate exact pinned candidates and calculate *observed* event counts.

    The scanner deliberately cannot approve independent specifications, source
    permissions, oracle secrecy, execution or task eligibility. Source API
    pagination/header completeness is NOT proven by a saved first page.
    """
    if (type(audit) is not dict or set(audit) != _TOP
            or audit["schema_version"] != "1.0"
            or audit["stage"] != "ISSUE_EVENT_FIRST_PAGE_REVIEW_ONLY"):
        raise ValueError("invalid metadata-only event audit schema")
    if type(audit["observed_on"]) is not str:
        raise ValueError("observation date must be YYYY-MM-DD")
    try:
        observation_day = date.fromisoformat(audit["observed_on"])
    except ValueError as exc:
        raise ValueError("invalid observation date") from exc
    if observation_day.isoformat() != audit["observed_on"]:
        raise ValueError("noncanonical observation date")
    if type(audit["records"]) is not list or len(audit["records"]) != 2:
        raise ValueError("two reviewer-only event windows required")

    verified = verify_issue_prepr_chronology(chronology, reviewer_packets)
    if verified["qualified_executable_tasks"] != 0:
        raise ValueError("source audit cannot authorize task execution")
    canonical = {x["candidate_id"]: x for x in chronology["records"]}
    if set(canonical) != {43, 104}:
        raise ValueError("unregistered real candidate identities")

    result = []
    seen_candidates = set()
    for rec in audit["records"]:
        if type(rec) is not dict or set(rec) != _RECORD:
            raise ValueError("unexpected event record or policy/oracle leakage")
        idx = rec["candidate_id"]
        if type(idx) is not int or idx not in canonical or idx in seen_candidates:
            raise ValueError("unknown or repeated candidate ID")
        seen_candidates.add(idx)
        src = canonical[idx]
        expect_url = (
            f"https://api.github.com/repos/{src['repository']}"
            f"/issues/{src['issue_number']}/events?per_page=100"
        )
        if (rec["repository"] != src["repository"]
                or rec["issue_url"] != src["issue_url"]
                or rec["events_api_url"] != expect_url):
            raise ValueError("observed issue-event URL disagrees with pinned task")
        if type(rec["page_size"]) is not int or rec["page_size"] != 100:
            raise ValueError("event REST page size must match observed query")
        for field in ("full_history_verified", "issue_body_snapshot_verified",
                      "task_admitted"):
            if rec[field] is not False:
                raise ValueError("event API page cannot self-certify external evidence")
        entries = rec["events"]
        if type(entries) is not list or not 1 <= len(entries) <= 100:
            raise ValueError("bounded first page with at least one event required")
        issue_at = _utc(src["issue_created_at"])
        pr_at = _utc(src["pr_created_at"])
        last_at = issue_at
        seen_event_ids = set()
        pre, post = Counter(), Counter()
        for item in entries:
            if type(item) is not dict or set(item) != _EVENT:
                raise ValueError("event metadata schema drift or potential gold leakage")
            event_id = item["event_id"]
            name = item["event"]
            if (type(event_id) is not int or event_id <= 0
                    or event_id in seen_event_ids):
                raise ValueError("duplicate/invalid public event ID")
            seen_event_ids.add(event_id)
            if type(name) is not str or not _EVENT_NAME.fullmatch(name):
                raise ValueError("invalid public event type")
            created = _utc(item["created_at"])
            if created < issue_at or created < last_at:
                raise ValueError("event precedes source issue or is out of order")
            if created.date() > observation_day:
                raise ValueError("event timestamp occurs after stated observation day")
            last_at = created
            (pre if created < pr_at else post)[name] += 1
        result.append({
            "candidate_id": idx,
            "repository": src["repository"],
            "issue_url": src["issue_url"],
            "observed_event_count": len(entries),
            "observed_pre_pr_events": sum(pre.values()),
            "observed_post_or_at_pr_events": sum(post.values()),
            "pre_pr_event_types": dict(sorted(pre.items())),
            "post_or_at_pr_event_types": dict(sorted(post.items())),
            "pre_pr_lead_seconds": int((pr_at - issue_at).total_seconds()),
            "issue_body_at_pr_creation": "NOT_VERIFIED_BY_EVENT_API",
            "task_admitted": False,
        })
    if seen_candidates != set(canonical):
        raise ValueError("missing pinned PHP or Go event audit")
    return {
        "status": "REVIEW_ONLY_EVENTS_DO_NOT_VERIFY_SPEC_TEXT",
        "source_page_completeness": "NOT_ATTESTED",
        "issue_body_at_pr_creation_verified": 0,
        "independent_oracles_verified": 0,
        "qualified_executable_tasks": 0,
        "external_code_executed": False,
        "records": sorted(result, key=lambda x: x["candidate_id"]),
    }
