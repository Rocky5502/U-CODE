"""Check the newly proposed PHP #104 repair draft, NEVER admit or execute.

Only source-controlled JSON and first-party Python are read. This draft
is NOT a historical original specification or a policy-visible task.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucode.prospective_task_contract import (
    parse_prospective_review_draft, validate_php104_prospective_draft,
)

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DRAFT=ROOT/"data/admission/2026-10-29/php104_NEW_PROSPECTIVE_DRAFT_REVIEW_ONLY.json"
DEFAULT_SOURCE=ROOT/"data/admission/2026-10-28/php104_base_source_contract_leads.json"


def validate_pending_php104_draft(
    draft_path: Path=DEFAULT_DRAFT, source_path: Path=DEFAULT_SOURCE,
) -> dict:
    obj=json.loads(Path(draft_path).read_text("utf-8"))
    source=json.loads(Path(source_path).read_text("utf-8"))
    draft=parse_prospective_review_draft(obj)
    report=validate_php104_prospective_draft(draft,source)
    if (report["historical_task_eligible"] or
            report["prospective_task_eligible"] or
            report["coding_agent_policy_input_approved"] or
            report["real_repository_executions"]):
        raise AssertionError("unapproved prospective draft promoted to real task")
    return report


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--draft",type=Path,default=DEFAULT_DRAFT)
    p.add_argument("--sources",type=Path,default=DEFAULT_SOURCE)
    args=p.parse_args()
    print(json.dumps(validate_pending_php104_draft(args.draft,args.sources),
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()
