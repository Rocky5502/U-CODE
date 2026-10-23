"""Summarize only canonical, deduplicated U-CODE GitHub PR audit records.

Read-only, standard-library-only. DOES NOT verify AI authorship, rights or tests.
Run from repository root:
  python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ALLOWED_STATES = {
    "production_source_path_detected",
    "test_only_source_change",
    "non_source_change",
    "empty_file_list_needs_review",
    "agent_or_merge_mismatch",
    "retrieval_failed",
    "rate_limited",
    "not_attempted_rate_limit",
}


def load_manifest(path: str | Path) -> dict[int, dict]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    manifest = {int(r["id"]): r for r in rows}
    if len(rows) != len(manifest):
        raise ValueError("duplicate candidate id in discovery manifest")
    return manifest


def audit_files(folder: str | Path) -> list[Path]:
    p = Path(folder)
    primary = p / "stratified_24_verified_metadata_with_triage.jsonl"
    paths = ([primary] if primary.exists() else []) + sorted(
        p.glob("stratified_offset*_ids*.jsonl")
    )
    if not paths:
        raise ValueError("no canonical stratified audit files found")
    # Intentionally exclude batch_01...batch_06 duplicates and any preliminary data.
    return paths


def load_records(folder: str | Path, manifest: dict[int, dict]) -> list[dict]:
    records = {}
    for path in audit_files(folder):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                idx = int(item["candidate_id"])
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError(f"malformed audit record {path}:{n}") from error
            if idx not in manifest:
                raise ValueError(f"candidate {idx} absent from manifest: {path}")
            if idx in records:
                raise ValueError(f"duplicate candidate id {idx}: {path}")
            target = manifest[idx]
            if item.get("repository") != target["repository"]:
                raise ValueError(f"candidate {idx} repository mismatch")
            expected_url = target["agent_pr_url"]
            if item.get("pr_url") != expected_url:
                raise ValueError(f"candidate {idx} PR URL mismatch")
            if item.get("triage_status") not in ALLOWED_STATES:
                raise ValueError(f"candidate {idx} has invalid status")
            if item.get("dataset_eligible") is not False:
                raise ValueError(f"candidate {idx} eligibility lacks evidence/false gate")
            records[idx] = item
    return [records[idx] for idx in sorted(records)]


def summarize(records: list[dict], manifest: dict[int, dict]) -> dict:
    if len({int(x["candidate_id"]) for x in records}) != len(records):
        raise ValueError("repeated candidate IDs")
    if len(records) > len(manifest):
        raise ValueError("screened more than discovery manifest")
    statuses = dict(sorted(Counter(x["triage_status"] for x in records).items()))
    languages = dict(sorted(Counter(x["discovery_language"] for x in records).items()))
    missing_shas = [
        x["candidate_id"] for x in records if x.get("triage_status") not in
        ("retrieval_failed", "rate_limited", "not_attempted_rate_limit")
        and not all(x.get(z) for z in ("base_sha", "head_sha", "merge_commit_sha"))
    ]
    mismatches = [
        x["candidate_id"] for x in records
        if x.get("production_files")
        and x["discovery_language"] not in x.get("production_languages", [])
    ]
    known_spdx = sum(bool(x.get("repository_license_spdx") and
                          x["repository_license_spdx"] not in
                          ("NOASSERTION", "UNKNOWN")) for x in records)
    return {
        "status": "metadata_screening_only_not_dataset_approval",
        "discovery_pool": len(manifest),
        "screened": len(records),
        "not_screened": len(manifest) - len(records),
        "source_status_counts": statuses,
        "by_discovery_language_screened": languages,
        "recognized_repository_spdx": known_spdx,
        "unknown_or_noassertion_repository_spdx": len(records) - known_spdx,
        "forks": sum(bool(x.get("fork")) for x in records),
        "language_mismatch_candidate_ids": mismatches,
        "missing_immutable_sha_candidate_ids": missing_shas,
        "independently_eligible_units": sum(x["dataset_eligible"] is True for x in records),
        "warning": ("PR account/merge/path metadata cannot prove AI line-level "
                    "authorship, permission to redistribute, or functional correctness."),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", default="data/audits/2026-10-24")
    parser.add_argument("--manifest", default="data/discovery/agent_pr_candidates_120.csv")
    parser.add_argument("--output", default=None, help="optional derived JSON file path")
    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)
    report = summarize(load_records(args.audit_dir, manifest), manifest)
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
