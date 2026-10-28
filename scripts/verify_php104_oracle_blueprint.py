"""Validate public-only PHP #104 oracle case coverage, no gold content or PHP.

The independent hidden oracle MUST be authored and stored outside the
public U-CODE repository by independent approved reviewers.
"""
import json
from pathlib import Path

from ucode.php104_oracle_review_blueprint import verify_php104_oracle_blueprint

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "data/admission"


def main():
    dossiers = [
        json.loads(line) for line in
        (A / "2026-10-25/pilot_dossiers.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    result = verify_php104_oracle_blueprint(
        json.loads((A / "2026-10-28/php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json").read_text("utf-8")),
        json.loads((A / "2026-10-28/php104_base_source_contract_leads.json").read_text("utf-8")),
        json.loads((A / "2026-10-27/two_candidate_issue_chronology_metadata.json").read_text("utf-8")),
        json.loads((A / "2026-10-27/two_candidate_pre_fix_tree_inventory.json").read_text("utf-8")),
        dossiers,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    print("REVIEW COVERAGE ONLY — ZERO SEALED ORACLES, ZERO QUALIFIED TASKS.")


if __name__ == "__main__":
    main()
