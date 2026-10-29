"""Produce source-backed research status JSON and metric dictionary Markdown.

All data come from local, canonical repository metadata and registries.
This is NOT a statistical/empirical efficacy analysis or authenticated
real-world experimental readiness.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.audit_dataset_quality import audit_release
from scripts.build_clean_pr_dataset import ROOT
from scripts.verify_dataset_release import verify_dataset_release
from ucode.research_readiness import build_readiness_snapshot,readiness_markdown


def export_readiness(output_dir: Path) -> dict:
    output_dir=Path(output_dir)
    with TemporaryDirectory(prefix="ucode-release-quality-") as tmp:
        audit_release(output_dir=Path(tmp))
        verified=verify_dataset_release(tmp)
    frozen=json.loads((ROOT/"data/curated/2026-10-27/frozen_cleaning_summary.json").read_text("utf-8"))
    gates=json.loads((ROOT/"configs/ucode_work_remaining_gates_2026-10-27.json").read_text("utf-8"))
    protocol=json.loads((ROOT/"configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
    with (ROOT/"data/discovery/dataset_source_registry_v2_2026-10-24.csv").open(
            "r",encoding="utf-8",newline="") as handle:
        candidate_sources=list(csv.DictReader(handle))
    if any(x["local_execution"]!="not_executed" for x in candidate_sources):
        raise ValueError("unverified dataset execution promotion")
    snap=build_readiness_snapshot(frozen,gates,protocol,verified,len(candidate_sources))
    output_dir.mkdir(parents=True,exist_ok=True)
    output_json=output_dir/"research_readiness.json"
    output_md=output_dir/"RESEARCH_METRICS_AND_STATUS.md"
    output_json.write_text(
        json.dumps(snap.data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    output_md.write_text(readiness_markdown(snap),encoding="utf-8")
    return {
        "stage":snap.data["stage"],
        "status_files":[output_json.name,output_md.name],
        "metadata_discovery_records":snap.data["metadata"]["records"],
        "experimentally_qualified_tasks":0,
        "observed_metric_values_present":0,
        "actual_model_executions":0,
        "real_oracle_results":0,
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,
                        default=Path("dist/ucode-research-readiness"))
    args=parser.parse_args(argv)
    print(json.dumps(export_readiness(args.output_dir),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
