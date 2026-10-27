"""Reproduce two genuine PR/issue chronology observations (NO code execution).

The pinned source read was independently inspected on GitHub API,
but the issue text at PR creation is NOT version-frozen by timestamps.
"""
import json
from pathlib import Path

from ucode.pending_review_packets import create_pending_review_packets
from ucode.issue_chronology import load_and_verify

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json"


def main():
    packets, _ = create_pending_review_packets()
    report = load_and_verify(SOURCE, packets)
    print(json.dumps(report, sort_keys=True, indent=2))
    print("ISSUE CREATION CHRONOLOGY ONLY: 0 VERIFIED PRE-PR BODY SNAPSHOTS, 0 TASKS ADMITTED.")


if __name__ == "__main__":
    main()
