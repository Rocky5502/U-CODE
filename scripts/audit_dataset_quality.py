"""Offline full-dataset structural quality review with a reproducible receipt.

The public artifact contains PR metadata and QC/lineage REVIEW FLAGS only,
never downloaded source, hidden tests, oracle verdicts or training labels.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

from scripts.build_clean_pr_dataset import ROOT, SOURCE, AUDIT_DIR, DEFAULT_OUT
from scripts.summarize_audit import audit_files, load_manifest, load_records
from ucode.dataset_curation import build_dataset, write_dataset
from ucode.dataset_quality import (
    dataset_schema, release_integrity_manifest, source_file_digests,
    validate_release,
)


def audit_release(*, manifest_path=SOURCE, audit_dir=AUDIT_DIR,
                  output_dir=DEFAULT_OUT, review_limit=12):
    path = Path(manifest_path)
    records = load_manifest(path)
    audits = load_records(audit_dir, records)
    clean = build_dataset(records, audits, sha256(path.read_bytes()).hexdigest(),
                          review_limit)
    qc = validate_release(clean, audits)
    dest = Path(output_dir)
    hashes = write_dataset(clean, dest)
    extras = {
        "dataset_schema.json": dataset_schema(),
        "quality_report.json": qc.report,
        "manual_lineage_and_rights_flags.json": {
            "stage": "MANUAL_REVIEW_REQUIRED_NOT_VERIFIED",
            "records": qc.reviewer_leakage_flags,
            "all_tasks_not_admitted": True,
        },
    }
    for name, payload in extras.items():
        (dest/name).write_text(
            json.dumps(payload, sort_keys=True, indent=2)+"\n",
            encoding="utf-8")
    paths = [p for p in sorted(dest.iterdir())
             if p.is_file() and p.name != "release_integrity.json"]
    out_bytes = {p.name: p.read_bytes() for p in paths}
    source_digests = source_file_digests(
        path, audit_files(audit_dir), root=ROOT)
    receipt = release_integrity_manifest(out_bytes, source_digests)
    (dest/"release_integrity.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2)+"\n",
        encoding="utf-8")
    assert len(out_bytes) == 7
    return {
        "stage": "REPRODUCIBLE_METADATA_QA_NOT_SCIENTIFIC_TASK_ADMISSION",
        "file_count": 8, "output_dir": str(dest),
        "input_manifest_sha256": clean.report["discovery_manifest_sha256"],
        "quality_checks": list(qc.checks),
        "human_review_flags_count": len(qc.reviewer_leakage_flags),
        "release_sha256_files": len(receipt["output_digests"]),
        "experiment_eligible": 0,
        "scientific_data_submission_ready": False,
        "third_party_code_executed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=SOURCE)
    parser.add_argument("--audit-dir", type=Path, default=AUDIT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--review-limit", type=int, default=12)
    a = parser.parse_args(argv)
    result = audit_release(manifest_path=a.manifest, audit_dir=a.audit_dir,
                           output_dir=a.output_dir, review_limit=a.review_limit)
    print(json.dumps(result, sort_keys=True, indent=2))
    print("DATA QUALITY IS NOT TASK ADMISSION; FULL CODE/ORACLE STUDY BLOCKED.")


if __name__ == "__main__":
    main()
