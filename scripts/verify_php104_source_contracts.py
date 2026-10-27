"""Offline PHP #104 pre-fix source-behavior and parent-issue feasibility check.

Reads checked-in metadata ONLY. No PHP, Git clone, third-party installer or
independent hidden evaluator is invoked.
"""
import json
from pathlib import Path

from ucode.php104_source_contract_audit import verify_php104_source_contract_leads

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/admission"
LEDGER = BASE / "2026-10-28/php104_base_source_contract_leads.json"
CHRONOLOGY = BASE / "2026-10-27/two_candidate_issue_chronology_metadata.json"
TREE = BASE / "2026-10-27/two_candidate_pre_fix_tree_inventory.json"
DOSSIERS = BASE / "2026-10-25/pilot_dossiers.jsonl"


def main():
    dossiers = [json.loads(line) for line in
                DOSSIERS.read_text("utf-8").splitlines() if line.strip()]
    result = verify_php104_source_contract_leads(
        json.loads(LEDGER.read_text("utf-8")),
        json.loads(CHRONOLOGY.read_text("utf-8")),
        json.loads(TREE.read_text("utf-8")),
        dossiers,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PHP PRE-FIX SOURCE BEHAVIOR LEADS ARE NOT TASK APPROVAL OR SEALED ORACLES.")


if __name__ == "__main__":
    main()
