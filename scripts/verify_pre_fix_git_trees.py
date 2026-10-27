"""Verify reproducible source-free pre-fix PHP/Go Git tree inventory."""
import json
from pathlib import Path

from ucode.pre_fix_tree_audit import verify_tree_snapshot

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "data/admission/2026-10-27/two_candidate_pre_fix_tree_inventory.json"
DOSSIERS = ROOT / "data/admission/2026-10-25/pilot_dossiers.jsonl"


def main():
    print(json.dumps(verify_tree_snapshot(TREE, DOSSIERS),
                     indent=2, sort_keys=True))
    print("NO CODE CHECKOUT, BUILD, ORACLE OR TASK APPROVAL PERFORMED.")


if __name__ == "__main__":
    main()
