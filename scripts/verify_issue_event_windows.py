"""Offline verifier for observed first-page public GitHub issue events.

No web request, repository checkout, source execution or oracle access.
"""
import json
from pathlib import Path

from ucode.issue_event_window_audit import verify_issue_event_windows
from ucode.pending_review_packets import create_pending_review_packets

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json"
EVENTS = ROOT / "data/admission/2026-10-28/two_candidate_issue_event_first_pages.json"


def main():
    packets, _ = create_pending_review_packets()
    output = verify_issue_event_windows(
        json.loads(EVENTS.read_text("utf-8")),
        json.loads(ISSUES.read_text("utf-8")),
        packets,
    )
    print(json.dumps(output, sort_keys=True, indent=2))
    print("ISSUE EVENT TIMESTAMPS DO NOT PROVE AS-OF-PR TEXT: ZERO TASKS ADMITTED.")


if __name__ == "__main__":
    main()
