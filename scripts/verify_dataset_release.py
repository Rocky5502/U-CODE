"""Verify reproducible, source-free U-CODE metadata ZIP after extraction.

Uses only the files in the directory and SHA256. Does NOT authenticate
the publisher, original GitHub claims, licenses or an independent oracle.
For trusted origin, compare the manifest itself against an independently
pinned Git commit or artifact digest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from ucode.release_semantics import audit_release_semantics

RELEASE_FILES = frozenset({
    "clean_metadata_120.csv", "language_strata.csv",
    "manual_review_12_NOT_EXECUTABLE.csv", "cleaning_report.json",
    "dataset_schema.json", "quality_report.json",
    "manual_lineage_and_rights_flags.json", "release_integrity.json",
})


def verify_dataset_release(folder: str | Path) -> dict:
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("dataset release directory does not exist")
    actual = {p.name for p in root.iterdir()}
    if actual != RELEASE_FILES:
        raise ValueError("missing or unexpected data release files")
    if any(not p.is_file() or p.is_symlink()
           for p in root.iterdir()):
        raise ValueError("symlinks and nonfile release entries are forbidden")
    receipt = json.loads((root/"release_integrity.json").read_text("utf-8"))
    if (receipt.get("status") != "DATASET_METADATA_RELEASE_NOT_EXECUTABLE"
            or receipt.get("hash_algorithm") != "sha256"
            or set(receipt.get("output_digests", {}))
            != (RELEASE_FILES - {"release_integrity.json"})
            or receipt.get("no_outcome_labels") is not True
            or receipt.get("no_independently_verified_tasks") is not True):
        raise ValueError("untrusted or incomplete release integrity contract")
    hashes = {}
    for name, record in sorted(receipt["output_digests"].items()):
        raw = (root/name).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if (type(record) is not dict or set(record) != {"sha256", "bytes"}
                or record["sha256"] != sha or record["bytes"] != len(raw)):
            raise ValueError("release SHA256 or byte length mismatch: " + name)
        hashes[name] = sha
    report = json.loads((root/"cleaning_report.json").read_text("utf-8"))
    quality = json.loads((root/"quality_report.json").read_text("utf-8"))
    if (report.get("discovered_pr_links") != 120
            or quality.get("candidate_pr_count") != 120
            or report.get("independently_approved_executable_tasks") != 0
            or quality.get("approved_executable_tasks") != 0
            or quality.get("scientific_data_submission_ready") is not False):
        raise ValueError("dataset counts/task admission do not match release")
    semantic = audit_release_semantics(root)
    return {
        "status": "SHA256_AND_CROSS_FILE_SEMANTICS_CONSISTENT_METADATA_ONLY",
        "semantic_audit": semantic,
        "files_verified": len(hashes),
        "metadata_record_count": 120,
        "independently_verified_tasks": 0,
        "physical_source_claims_authenticated": False,
        "all_files_hash_consistent": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path,
                        help="directory of extracted eight-file source-free dataset")
    args = parser.parse_args(argv)
    print(json.dumps(verify_dataset_release(args.folder),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
