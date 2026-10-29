"""Print a source-only, negative-evidence report; never export issue-body text."""
from __future__ import annotations
import json
from pathlib import Path
from ucode.live_issue_spec_quarantine import audit_live_issue_observations

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data/admission/2026-10-29/live_issue_current_body_review_metadata.json"
CHRONOLOGY = ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json"

def main() -> None:
    observed = json.loads(CURRENT.read_text(encoding="utf-8"))
    chronology = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    print(json.dumps(audit_live_issue_observations(observed, chronology), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
