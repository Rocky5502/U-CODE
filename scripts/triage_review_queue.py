"""Produce deterministic *manual-only* shortlist from the 120-PR screen.

Example: python -m scripts.triage_review_queue --limit 12
No external clone, network access, model inference or test execution.
"""
import argparse
import csv
import io
from pathlib import Path

from scripts.summarize_audit import load_manifest, load_records
from ucode.review_queue import select_review_queue

HEADERS = ("candidate_id", "repository", "url", "language",
           "priority_class", "production_path_count", "test_path_count",
           "reasons", "eligible")


def output_csv(queue) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADERS, lineterminator="\n")
    writer.writeheader()
    for item in queue:
        writer.writerow({
            "candidate_id": item.candidate_id, "repository": item.repository,
            "url": item.url, "language": item.language,
            "priority_class": item.priority_class,
            "production_path_count": item.production_path_count,
            "test_path_count": item.test_path_count,
            "reasons": ";".join(item.reasons),
            "eligible": "FALSE",
        })
    return stream.getvalue()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default="data/discovery/agent_pr_candidates_120.csv")
    p.add_argument("--audit-dir", default="data/audits/2026-10-24")
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--output")
    args = p.parse_args(argv)
    if args.limit < 0:
        p.error("limit must be nonnegative")
    m = load_manifest(args.manifest)
    records = load_records(args.audit_dir, m)
    queue = select_review_queue(records)
    print("MANUAL_REVIEW_ONLY source_path_candidates="
          f"{len(queue)} study_eligible=0 shortlisted_first_pass="
          f"{sum(q.priority_class=='first_pass_manual_review' for q in queue)}")
    csv_text = output_csv(queue[:args.limit or len(queue)])
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(csv_text, encoding="utf-8")
    else:
        print(csv_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
