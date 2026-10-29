"""Recompute PR-metadata release semantics AFTER file hashes are validated.

This checks the public eight-file *metadata* snapshot's internally observable
grain, counts, strata, triage and review flags. It does not authenticate
GitHub, licenses, source provenance or hidden evaluator labels and can be
fooled by a malicious re-authoring of all files + their self-signed manifest.
"""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

from .dataset_curation import COLUMNS, LANGUAGES, REVIEW_FIELDS, SUMMARY_FIELDS
from .dataset_quality import REJECT_TASK_FIELDS, dataset_schema

STATUSES = frozenset({
    "production_source_path_detected", "test_only_source_change",
    "non_source_change", "empty_file_list_needs_review", "retrieval_failed",
})
FALSE_FLAGS = (
    "source_rights_verified", "line_attribution_verified",
    "sealed_independent_oracle_verified", "sandbox_verified",
    "experiment_eligible",
)


def _csv(root: Path, name: str, header: tuple[str, ...]) -> list[dict[str, str]]:
    with (root/name).open("r", encoding="utf-8", newline="") as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames != list(header):
            raise ValueError("metadata CSV schema changed: "+name)
        rows=list(reader)
    if any(set(row) != set(header) or None in row or
           any(value is None for value in row.values()) for row in rows):
        raise ValueError("malformed metadata CSV row: "+name)
    return rows


def _integer(raw: str, label: str) -> int:
    if not isinstance(raw,str) or not raw.isascii() or not raw.isdecimal():
        raise ValueError("invalid nonnegative integer in metadata: "+label)
    return int(raw)


def audit_release_semantics(root: Path) -> dict:
    """Check a complete already-hash-verified directory; no execution.

    Restrict all observed counts to their proper grains: PR discovery is
    not source-language coverage, independent oracle, or accepted task.
    """
    if not isinstance(root,Path) or not root.is_dir():
        raise ValueError("metadata release path required")
    rows=_csv(root,"clean_metadata_120.csv",COLUMNS)
    strata=_csv(root,"language_strata.csv",SUMMARY_FIELDS)
    shortlist=_csv(root,"manual_review_12_NOT_EXECUTABLE.csv",REVIEW_FIELDS)
    cleaning=json.loads((root/"cleaning_report.json").read_text("utf-8"))
    quality=json.loads((root/"quality_report.json").read_text("utf-8"))
    schema=json.loads((root/"dataset_schema.json").read_text("utf-8"))
    flags=json.loads((root/"manual_lineage_and_rights_flags.json").read_text("utf-8"))

    if schema != dataset_schema() or (REJECT_TASK_FIELDS & set(COLUMNS)):
        raise ValueError("dataset schema/forbidden evaluator field mismatch")
    if len(rows)!=120 or len(strata)!=12 or len(shortlist)!=12:
        raise ValueError("120 records, twelve strata and twelve review leads required")
    if [x["search_language"] for x in strata] != list(LANGUAGES):
        raise ValueError("stratum order/languages do not match manifest")
    ids, urls, repos = set(),set(),set()
    summaries={}
    statuses=Counter()
    retrieved=0
    by_language={}
    selected={}
    changed_language_status=0
    for raw in rows:
        cid=_integer(raw["candidate_id"],"candidate_id")
        url=raw["pr_url"].casefold()
        repo=raw["repository"].casefold()
        if cid in ids or url in urls or repo in repos or not repo or not url:
            raise ValueError("duplicate/blank candidate, PR or repository at stated grain")
        ids.add(cid); urls.add(url); repos.add(repo)
        if raw["search_language"] not in LANGUAGES:
            raise ValueError("unregistered search language")
        if raw["audit_status"] not in STATUSES:
            raise ValueError("unknown triage status")
        if raw["metadata_source_status"] not in (
                "retrieved","retrieval_failed_or_unattempted"):
            raise ValueError("bad metadata retrieval status")
        if (raw["metadata_source_status"]=="retrieved") != (
                raw["audit_status"] != "retrieval_failed"):
            raise ValueError("retrieval and raw audit status inconsistent")
        if raw["split_status"]!="NOT_SPLIT_LINEAGE_AND_TASK_ADMISSION_PENDING":
            raise ValueError("an unreviewed split cannot claim approval")
        if raw["lineage_group_review"]!="PENDING_INDEPENDENT_REVIEW":
            raise ValueError("lineage review cannot be silently promoted")
        if any(raw[x]!="FALSE" for x in FALSE_FLAGS):
            raise ValueError("executable task/rights/oracle flag falsely promoted")
        prod=_integer(raw["changed_production_file_count"],"source_path_count")
        _integer(raw["changed_test_file_count"],"test_path_count")
        if (raw["audit_status"]=="production_source_path_detected")!=(prod>0):
            raise ValueError("production path/triage inconsistency")
        names=set(filter(None,raw["observed_production_languages"].split("|")))
        if prod==0 and names:
            raise ValueError("non-production row claims changed-source language")
        for f in ("base_sha","head_sha","merge_commit_sha"):
            v=raw[f]
            if v and (len(v)!=40 or any(c not in "0123456789abcdef" for c in v)):
                raise ValueError("invalid SHA in metadata")
            if raw["metadata_source_status"]=="retrieved" and not v:
                raise ValueError("retrieved PR lacks pinned SHA")
        lang=raw["search_language"]
        statuses[raw["audit_status"]]+=1
        retrieved+=raw["metadata_source_status"]=="retrieved"
        if lang not in by_language:
            by_language[lang]=[]
        by_language[lang].append(raw)
        if raw["review_shortlist"]=="TRUE":
            selected[cid]=raw
        elif raw["review_shortlist"]!="FALSE":
            raise ValueError("bad review shortlist flag")
        changed_language_status+=int(prod>0 and lang not in names)
    if len(ids)!=120 or len(selected)!=12 or set(ids)!=set(range(1,121)):
        raise ValueError("candidate denominator or shortlist incomplete")
    if dict(statuses)!=cleaning.get("status_counts"):
        raise ValueError("triage distribution does not reconcile")
    if sum(statuses.values())!=120 or statuses.get("production_source_path_detected")!=62:
        raise ValueError("source-path lead denominator mismatch")
    if retrieved!=119:
        raise ValueError("metadata retrieved denominator mismatch")
    for lang in LANGUAGES:
        rr=by_language.get(lang,[])
        if len(rr)!=10:
            raise ValueError("each original query stratum must contain ten records")
        src=[x for x in rr if x["audit_status"]=="production_source_path_detected"]
        expected={
            "discovered_prs":len(rr),
            "metadata_retrieved":sum(x["metadata_source_status"]=="retrieved" for x in rr),
            "source_path_leads":len(src),
            "first_pass_metadata_leads":sum(x["priority_class"]=="first_pass_manual_review" for x in rr),
            "source_language_matched":sum(lang in x["observed_production_languages"].split("|") for x in src),
            "source_language_mismatched_or_unobserved":sum(lang not in x["observed_production_languages"].split("|") for x in src),
            "shortlisted_for_manual_review":sum(x["review_shortlist"]=="TRUE" for x in rr),
            "experiment_eligible":0,
        }
        candidate=next(x for x in strata if x["search_language"]==lang)
        for key,value in expected.items():
            if _integer(candidate[key],key)!=value:
                raise ValueError("language-stratum CSV does not reconcile: "+lang+"/"+key)
        official=next((x for x in cleaning.get("by_search_language",[])
                       if x.get("search_language")==lang),None)
        if official is None or any(official.get(k)!=v for k,v in expected.items()):
            raise ValueError("language summary JSON disagrees with rows: "+lang)
    for row in shortlist:
        cid=_integer(row["candidate_id"],"shortlist_id")
        if cid not in selected or any(row[k]!=str(selected[cid][k]) for k in REVIEW_FIELDS):
            raise ValueError("review queue not a subset of flagged canonical rows")
    expected_report={
        "discovered_pr_links":120,
        "distinct_repository_names":120,
        "metadata_retrieved":retrieved,
        "metadata_not_retrieved":120-retrieved,
        "production_source_path_leads":statuses["production_source_path_detected"],
        "first_pass_manual_review_leads":sum(
            x["priority_class"]=="first_pass_manual_review" for x in rows),
        "shortlisted_for_manual_review":len(selected),
        "independently_approved_executable_tasks":0,
        "source_language_mismatched_or_unobserved_leads":changed_language_status,
    }
    if any(cleaning.get(k)!=v for k,v in expected_report.items()):
        raise ValueError("cleaning report totals do not reconcile to rows")
    if (cleaning.get("independent_train_test_split_frozen") is not False
        or cleaning.get("source_code_downloaded") is not False
        or cleaning.get("external_code_executed") is not False
        or cleaning.get("review_queue_is_not_an_experiment") is not True):
        raise ValueError("scientific-stage boundaries missing")
    if any(quality.get(k)!=v for k,v in {
        "candidate_pr_count":120, "unique_repository_names":120,
        "unique_pr_urls":120,"audit_joined_rows":120,
        "approved_executable_tasks":0,
    }.items()):
        raise ValueError("quality report count disagreement")
    if (quality.get("scientific_data_submission_ready") is not False
        or quality.get("query_language_strata") != {x:10 for x in sorted(LANGUAGES)}
        or quality.get("audit_outcome_counts")!=dict(statuses)):
        raise ValueError("quality stage or strata disagreement")
    if (flags.get("all_tasks_not_admitted") is not True
        or flags.get("stage")!="MANUAL_REVIEW_REQUIRED_NOT_VERIFIED"
        or type(flags.get("records")) is not list
        or any(x.get("task_eligible") is not False for x in flags["records"])):
        raise ValueError("review flags cannot grant task admission")
    return {
        "status":"CROSS_FILE_SEMANTICS_CONSISTENT_METADATA_ONLY",
        "pr_discovery_rows":len(rows),
        "query_language_strata":len(strata),
        "metadata_retrieved":retrieved,
        "production_source_path_leads":statuses["production_source_path_detected"],
        "shortlisted_manual_review":len(selected),
        "approved_executable_tasks":0,
        "sealed_oracle_outcomes":0,
        "actual_changed_language_coverage_verified":False,
        "source_rights_independently_audited":False,
    }
