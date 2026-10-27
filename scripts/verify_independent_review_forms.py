"""Offline verifier for exported TWO-REVIEWER BLANK evidence worksheets.

This is a consistency/integrity check against the canonical 120-PR metadata,
NOT signature authentication, real human annotation or task admission.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from ucode.pending_review_packets import create_pending_review_packets
from ucode.reviewer_adjudication import (
    adjudicate_review_disagreement,
)

EXPECTED_FILES = frozenset({
    "reviewer_A_96_PENDING.jsonl",
    "reviewer_B_96_PENDING.jsonl",
    "review_agreement_PENDING.json",
    "reviewer_forms_integrity.json",
})


def verify_blank_review_forms(folder: Path):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("reviewer release directory absent")
    files = list(root.iterdir())
    if {p.name for p in files} != EXPECTED_FILES:
        raise ValueError("missing or unexpected reviewer worksheet files")
    if any(not p.is_file() or p.is_symlink() for p in files):
        raise ValueError("symlinks or directories are not allowed")
    integrity = json.loads((root/"reviewer_forms_integrity.json").read_text("utf-8"))
    if (integrity.get("status") != "REVIEWER_FORMS_ONLY_NOT_ADJUDICATED"
        or integrity.get("no_oracle") is True
        or integrity.get("admitted_executable_tasks") != 0
        or integrity.get("model_inference_executed") is not False
        or integrity.get("two_reviewer_independence_not_authenticated") is not True
        or integrity.get("reviewer_signatures_fabricated") is not False):
        raise ValueError("reviewer release scientific safety contract invalid")
    files_to_verify = EXPECTED_FILES - {"reviewer_forms_integrity.json"}
    if set(integrity.get("artifact_checksums_sha256", {})) != files_to_verify:
        raise ValueError("reviewer digest registry incomplete")
    for name in files_to_verify:
        body = (root/name).read_bytes()
        if sha256(body).hexdigest() != integrity["artifact_checksums_sha256"][name]:
            raise ValueError("reviewer SHA256 corrupted: "+name)
    packets, _ = create_pending_review_packets()
    packet_hash = sha256(json.dumps(
        packets, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if integrity.get("input_review_packet_SHA256") != packet_hash:
        raise ValueError("review forms detached from frozen PR evidence packet")
    forms = {}
    for slot in ("A", "B"):
        path = root/f"reviewer_{slot}_96_PENDING.jsonl"
        forms[slot] = tuple(
            json.loads(line) for line in path.read_text("utf-8").splitlines()
            if line.strip()
        )
    result = adjudicate_review_disagreement(
        packets, forms["A"], forms["B"])
    report = json.loads((root/"review_agreement_PENDING.json").read_text("utf-8"))
    if report != result.summary or result.summary["completed_gate_pairs"] != 0:
        raise ValueError("reviewer forms unexpectedly completed or report inconsistent")
    return {
        "status": "TWO_REVIEWER_BLANK_FORMS_INTEGRITY_VERIFIED_NOT_APPROVED",
        "forms_verified": len(forms["A"])+len(forms["B"]),
        "completed_assessments": 0,
        "independently_admitted_tasks": 0,
        "human_identity_authenticated": False,
        "oracle_executed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(verify_blank_review_forms(args.folder), indent=2))


if __name__ == "__main__":
    main()
