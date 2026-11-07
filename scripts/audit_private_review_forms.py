"""Local-only redacted triage of COMPLETED A/B evidence-review worksheets.

Accepts externally completed JSONL reviewer files. Rechecks every row against
the canonical 12 pending source-era PR dossiers and existing A/B schema.
Outputs ONLY public candidate ID, gate, a disagreement status and aggregate
non-admission counts; never outputs reviewer names, notes, evidence links or
artifact digests. Does not authenticate a human, verify the content of an
evidence file or authorize a task. Do NOT upload private filled review forms
to this public repository or its GitHub Actions artifacts.

This module is an OFFLINE inbox validator, not a task-admission authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ucode.pending_review_packets import create_pending_review_packets
from ucode.reviewer_adjudication import adjudicate_review_disagreement

_MAX_INPUT_BYTES = 2 * 1024 * 1024
_MAX_LINE_BYTES = 32 * 1024
_EXPECTED_ROWS = 12 * 8


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON review field rejected")
        result[key] = value
    return result


def _reject_nonjson_constant(value: str):
    raise ValueError("non-JSON NaN/Infinity review value rejected")


def read_private_review_rows(path: Path) -> tuple[dict, ...]:
    """Bounded parser; rejects symlinks, malformed JSON and duplicate keys.

    The unredacted contents live in local memory for validation ONLY.
    They are never returned by the public summarizer.
    """
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError("local reviewer input must be a regular non-symlink file")
    payload = p.read_bytes()
    if not payload or len(payload) > _MAX_INPUT_BYTES:
        raise ValueError("reviewer input exceeds safe file-size bound or is empty")
    lines = payload.splitlines()
    if len(lines) != _EXPECTED_ROWS:
        raise ValueError("expected the complete 96-row reviewer input inventory")
    rows = []
    for line in lines:
        if not line or len(line) > _MAX_LINE_BYTES:
            raise ValueError("blank or overlong private reviewer row")
        try:
            item = json.loads(
                line.decode("utf-8"),
                object_pairs_hook=_object_without_duplicates,
                parse_constant=_reject_nonjson_constant,
            )
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid UTF-8 JSON reviewer row") from exc
        if type(item) is not dict:
            raise ValueError("reviewer row must be JSON object")
        rows.append(item)
    return tuple(rows)


def audit_private_review_forms(
    reviewer_a_path: Path, reviewer_b_path: Path,
) -> dict:
    """Redact private evidence and names; never grant task admission.

    Existing adjudication requires the entire 12x8x2 inventory to match
    frozen source packets, blocks fake approval fields, checks reviewer
    slot identity consistency and notes all unresolved findings.
    """
    a = Path(reviewer_a_path)
    b = Path(reviewer_b_path)
    if a.resolve() == b.resolve():
        raise ValueError("reviewer A and B must supply distinct local files")
    forms_a = read_private_review_rows(a)
    forms_b = read_private_review_rows(b)
    packets, _ = create_pending_review_packets()
    audit = adjudicate_review_disagreement(packets, forms_a, forms_b)
    counts = audit.summary
    states = tuple({
        "candidate_id": row["candidate_id"],
        "gate": row["gate"],
        "triage_status": row["status"],
        "adjudicated": False,
        "eligible_for_experiment": False,
    } for row in audit.statuses)
    if len(states) != _EXPECTED_ROWS or any(
            row["adjudicated"] or row["eligible_for_experiment"]
            for row in states):
        raise AssertionError("no public audit may self-authorize task admission")
    return {
        "schema_version": "1.0",
        "status": "LOCAL_REVIEW_INPUT_TRIAGE_ONLY_NOT_INDEPENDENT_ADMISSION",
        "reviewed_source_leads": 12,
        "gate_pairs": _EXPECTED_ROWS,
        "paired_nonpending_claims": counts["completed_gate_pairs"],
        "pending_gate_pairs": counts["pending_gate_pairs"],
        "verdict_agreement_fraction_on_paired_claims":
            counts["agreement_fraction_completed_pairs"],
        "disagreement_pairs": counts["disagreements_on_completed_pairs"],
        "positive_evidence_digest_mismatch_pairs":
            counts["positive_evidence_digest_mismatches"],
        "positive_evidence_reference_mismatch_pairs":
            counts["positive_evidence_reference_mismatches"],
        "statuses_public_only": states,
        "reviewer_identity_authenticated": False,
        "reviewer_independence_authenticated": False,
        "evidence_contents_authenticated": False,
        "independent_oracle_sealed": False,
        "independently_admitted_executable_tasks": 0,
        "external_source_executed": False,
        "llm_runs": 0,
        "output_contains_reviewer_names_notes_or_evidence": False,
        "warning": (
            "These are unverified reviewer-submitted claims. Even 96 matching "
            "positive verdicts do not authorize any task, model trial or "
            "independent oracle. Separate signed external approval is mandatory."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", required=True, type=Path)
    parser.add_argument("--reviewer-b", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional REDACTED status-only JSON path")
    args = parser.parse_args(argv)
    report = audit_private_review_forms(args.reviewer_a, args.reviewer_b)
    blob = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        output = args.output
        if output.resolve() in (args.reviewer_a.resolve(),
                                args.reviewer_b.resolve()):
            raise ValueError("redacted output must not overwrite private reviewer inputs")
        if output.is_symlink():
            raise ValueError("refusing to overwrite a symlinked summary path")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(blob, encoding="utf-8")
    print(blob, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
