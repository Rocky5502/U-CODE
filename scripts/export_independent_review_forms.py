"""Create segregated A/B, 96-gate reviewer forms without reviewer claims.

Outputs contain post-fix PR URLs and are NEVER permissible coding-agent prompts.
The blinded research workflow is achieved by separately distributing forms
to reviewers; the code cannot prove reviewers are independent humans.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from ucode.pending_review_packets import create_pending_review_packets
from ucode.reviewer_adjudication import (
    SLOTS, blank_independent_forms, adjudicate_review_disagreement,
)


def export_blank_reviewer_forms(output_dir: Path):
    packets, source_summary = create_pending_review_packets()
    forms = blank_independent_forms(packets)
    audit = adjudicate_review_disagreement(packets, forms["A"], forms["B"])
    if (audit.summary["completed_gate_pairs"] != 0
            or audit.summary["independently_admitted_executable_tasks"] != 0):
        raise ValueError("blank review forms cannot be completed/admitted")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for slot in SLOTS:
        files[f"reviewer_{slot}_96_PENDING.jsonl"] = "".join(
            json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n"
            for v in forms[slot]
        )
    files["review_agreement_PENDING.json"] = (
        json.dumps(audit.summary, indent=2, sort_keys=True) + "\n")
    for name, body in files.items():
        (output_dir/name).write_text(body, encoding="utf-8")
    integrity = {
        "status": "REVIEWER_FORMS_ONLY_NOT_ADJUDICATED",
        "input_review_packet_SHA256": sha256(
            json.dumps(packets, sort_keys=True, separators=(",", ":"))
            .encode("utf-8")
        ).hexdigest(),
        "artifact_checksums_sha256": {
            k: sha256(v.encode("utf-8")).hexdigest()
            for k, v in sorted(files.items())
        },
        "two_reviewer_independence_not_authenticated": True,
        "reviewer_signatures_fabricated": False,
        "admitted_executable_tasks": 0,
        "model_inference_executed": False,
    }
    (output_dir/"reviewer_forms_integrity.json").write_text(
        json.dumps(integrity, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return audit.summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path("dist/ucode-independent-reviewers-only"))
    args = parser.parse_args(argv)
    result = export_blank_reviewer_forms(args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("BLANK INDEPENDENT REVIEW FORMS ONLY / ZERO TASK ADMISSIONS.")


if __name__ == "__main__":
    main()
