"""Verify extracted four-file U-CODE provenance WARNING bundle.

Checks immutable file hashes and structure, NOT independent repository
ancestry or absence of task contamination. No third-party code execution.
"""
import csv
from hashlib import sha256
import json
from pathlib import Path

EXPECTED = frozenset({
    "possible_lineage_components_NOT_SPLIT.csv",
    "potential_cross_task_links_REVIEW_ONLY.csv",
    "lineage_graph_report.json",
    "lineage_graph_integrity.json",
})


def verify_lineage_review(folder):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("missing metadata overlap-review folder")
    paths = {p.name: p for p in root.iterdir()}
    if (set(paths) != EXPECTED
        or any(not p.is_file() or p.is_symlink() for p in paths.values())):
        raise ValueError("unexpected, missing or linked overlap-review file")
    provenance = json.loads(
        paths["lineage_graph_integrity.json"].read_text("utf-8"))
    required = EXPECTED - {"lineage_graph_integrity.json"}
    if (provenance.get("stage") != "REVIEW_ONLY_NO_CONFIRMED_DUPLICATES_OR_SPLIT"
        or provenance.get("experiment_eligible") != 0
        or provenance.get("records") != 120
        or set(provenance.get("output_sha256", {})) != required):
        raise ValueError("unexpected graph metadata contract")
    for name in required:
        digest = sha256(paths[name].read_bytes()).hexdigest()
        if provenance["output_sha256"][name] != digest:
            raise ValueError("SHA256 mismatch for metadata overlap-review file")
    with paths["possible_lineage_components_NOT_SPLIT.csv"].open(
            newline="", encoding="utf-8") as f:
        components = list(csv.DictReader(f))
    with paths["potential_cross_task_links_REVIEW_ONLY.csv"].open(
            newline="", encoding="utf-8") as f:
        links = list(csv.DictReader(f))
    stats = json.loads(paths["lineage_graph_report.json"].read_text("utf-8"))
    if (len(components) != 120
        or len({r["candidate_id"] for r in components}) != 120
        or any(r["experiment_eligible"] != "FALSE" or
               r["train_test_split_status"] != "BLOCKED"
               for r in components)
        or stats.get("canonical_candidates") != 120
        or stats.get("independent_train_test_split_frozen") is not False
        or stats.get("independently_admitted_executable_tasks") != 0
        or sum(stats.get("relation_counts", {}).values()) != len(links)
        or any(r["independently_adjudicated"] != "FALSE"
               for r in links)):
        raise ValueError("overlap graph falsifies completeness or split status")
    return {
        "status": "HASH_CHECKED_POTENTIAL_LINEAGE_WARNING_ONLY",
        "candidate_records": 120,
        "review_warning_edges": len(links),
        "verified_duplicate_tasks": 0,
        "approved_executable_tasks": 0,
        "verified_leakage_free_split": False,
    }
