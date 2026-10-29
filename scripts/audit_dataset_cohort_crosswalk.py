"""Reconcile frozen 120-PR discovery rows to current 13-source catalog.

Metadata-only data-quality inspection: exact PR identity, categorical grain,
language-stratum preservation and no quiet experiment promotion. This does
not fetch, download or execute third-party source, models or oracles.
"""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/"data/discovery/agent_pr_candidates_120.csv"
CLEAN = ROOT/"data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv"
SOURCES = ROOT/"data/discovery/dataset_source_registry_v2_2026-10-24.csv"
LEGACY = ROOT/"data/discovery/dataset_source_registry.csv"
SUMMARY = ROOT/"data/curated/2026-10-27/frozen_cleaning_summary.json"

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def inspect_cohorts(raw: list[dict], curated: list[dict],
                    external: list[dict], legacy: list[dict],
                    summary: dict) -> dict:
    if type(raw) is not list or type(curated) is not list:
        raise ValueError("metadata rows must be lists")
    if len(raw)!=120 or len(curated)!=120:
        raise ValueError("120 discovery and 120 curated rows required")
    source_cols = {"dataset","unit","primary_url","access_state",
                   "license_rights","oracle_status","local_execution",
                   "distinct_cohort","risk_or_limit"}
    if len(external)!=13 or any(set(r)!=source_cols for r in external):
        raise ValueError("exact thirteen source catalog with canonical columns required")
    if len(legacy)!=10:
        raise ValueError("original ten-lead legacy catalog is a different inventory")
    valid_classes={"Naturalistic","Controlled_generation","Attribution_only",
                   "Auxiliary_training","Efficiency_secondary"}
    if (len({r["dataset"] for r in external})!=13 or
        any(not r["primary_url"].startswith("https://") or
            r["distinct_cohort"] not in valid_classes or
            r["local_execution"]!="not_executed"
            for r in external)):
        raise ValueError("external registry includes duplicate, non-HTTPS or falsely qualified source")
    if len({r["dataset"] for r in legacy})!=10:
        raise ValueError("legacy candidate source names must remain distinct")
    if any(not r["source_url"].startswith("https://")
           or r["local_status"]!="not_downloaded" for r in legacy):
        raise ValueError("legacy source inventory is not a downloaded task set")
    raw_ids, clean_ids={}, {}
    for r in raw:
        if set(r) != {"id","query_language","repository","agent_pr_url",
                      "discovery_query","discovery_date","provenance_status",
                      "license_status","test_status","source_code_status"}:
            raise ValueError("source manifest schema mismatch")
        if (r["provenance_status"]!="UNVERIFIED_CANDIDATE"
            or any(r[x]!="NOT_CHECKED" for x in
                    ("license_status","test_status","source_code_status"))):
            raise ValueError("raw discovery rows cannot self-certify source rights")
        idx=int(r["id"])
        if idx in raw_ids: raise ValueError("duplicate raw candidate ID")
        raw_ids[idx]=r
    for r in curated:
        if set(r)!={"candidate_id","repository","pr_url","search_language",
                    "source_qualification","task_admission",
                    "independent_oracle","split_status"}:
            raise ValueError("curated discovery frame schema mismatch")
        idx=int(r["candidate_id"])
        if idx in clean_ids: raise ValueError("duplicate curated candidate ID")
        clean_ids[idx]=r
    if set(raw_ids)!=set(range(1,121)) or set(clean_ids)!=set(raw_ids):
        raise ValueError("missing/extra candidate identity")
    counts=Counter()
    for idx, src in raw_ids.items():
        obj=clean_ids[idx]
        if ((obj["repository"],obj["pr_url"],obj["search_language"]) !=
            (src["repository"],src["agent_pr_url"],src["query_language"])):
            raise ValueError("curated row changes repository/PR/stratum identity")
        if (obj["source_qualification"]!="DISCOVERY_ONLY"
            or obj["task_admission"]!="NOT_ADMITTED"
            or obj["independent_oracle"]!="NOT_VERIFIED"
            or obj["split_status"]!="NOT_SPLIT"):
            raise ValueError("curated metadata must not claim executable task/oracle/split")
        counts[src["query_language"]]+=1
    if len(counts)!=12 or set(counts.values())!={10}:
        raise ValueError("twelve source search strata must contain ten discovery rows each")
    if (summary.get("status")!="METADATA_ONLY_NO_TASK_APPROVAL"
        or summary.get("discovered_pr_links")!=120
        or summary.get("metadata_retrieved")!=119
        or summary.get("production_source_path_leads")!=62
        or summary.get("independently_approved_executable_tasks")!=0
        or sum(summary.get("status_counts",{}).values())!=120):
        raise ValueError("frozen dataset status summary inconsistent with qualified scope")
    return {
        "status":"METADATA_RECONCILED_NOT_EXECUTABLE",
        "source_discovery_rows":120,
        "search_language_strata":dict(sorted(counts.items())),
        "external_source_catalog_leads":13,
        "legacy_catalog_leads":10,
        "source_catalog_cohorts":dict(sorted(Counter(
            r["distinct_cohort"] for r in external).items())),
        "retrieved_pr_metadata":119,
        "production_source_path_leads":62,
        "independent_executable_tasks":0,
        "licensed_repacked_datasets":0,
        "downloaded_external_datasets_verified":0,
        "test_labels_or_sealed_oracles_exported":0,
    }

def main() -> None:
    result=inspect_cohorts(
        read_csv(RAW),read_csv(CLEAN),read_csv(SOURCES),read_csv(LEGACY),
        json.loads(SUMMARY.read_text(encoding="utf-8")))
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
