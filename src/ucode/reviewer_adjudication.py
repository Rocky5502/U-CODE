"""Independent two-reviewer evidence worksheet for U-CODE candidate PRs.

Source-free administrative workflow. Generating blank forms is NOT research
annotation. A pair of reviews is NOT executable-task authorization, even with
perfect reviewer agreement: external adjudication, sealed oracle and runner
approval remain separate security/scientific gates.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .task_admission import REQUIRED_GATES, parse_dossier, dossier_sha256

SLOTS = ("A", "B")
VERDICTS = frozenset({
    "PENDING", "EVIDENCE_PRESENT_NOT_ATTESTED", "INSUFFICIENT_INFORMATION",
    "REJECTED_WITH_REASON",
})
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FIELDS = frozenset({
    "candidate_id", "repository", "pr_url", "packet_sha256", "gate",
    "reviewer_slot", "reviewer_identity", "verdict", "evidence_refs",
    "evidence_sha256", "reviewer_note", "independent_approval",
})


@dataclass(frozen=True)
class PairedReviewAudit:
    statuses: tuple[dict, ...]
    summary: dict


def blank_independent_forms(packets: tuple[dict, ...]) -> dict[str, tuple[dict, ...]]:
    """Generate independent identical work inventories with no claimed evidence."""
    if not packets or len(packets) != 12:
        raise ValueError("frozen twelve evidence packets required")
    seen = set()
    per_slot = {slot: [] for slot in SLOTS}
    for obj in packets:
        task = parse_dossier(obj)
        if task.candidate_id in seen or task.evidence_stage != "MANUAL_REVIEW_ONLY":
            raise ValueError("duplicate or ineligible review packet")
        seen.add(task.candidate_id)
        if any(g.status != "PENDING" for g in task.gates):
            raise ValueError("only pending unapproved packets may be reviewed")
        digest = dossier_sha256(obj)
        for slot in SLOTS:
            for gate in REQUIRED_GATES:
                per_slot[slot].append({
                    "candidate_id": task.candidate_id,
                    "repository": task.repository,
                    "pr_url": task.pr_url,
                    "packet_sha256": digest,
                    "gate": gate,
                    "reviewer_slot": slot,
                    "reviewer_identity": "",
                    "verdict": "PENDING",
                    "evidence_refs": [],
                    "evidence_sha256": "",
                    "reviewer_note": "",
                    "independent_approval": False,
                })
    return {slot: tuple(records) for slot, records in per_slot.items()}


def _validate_forms(forms: tuple[dict, ...], slot: str, expected: tuple[dict, ...]):
    if not isinstance(forms, (tuple, list)) or len(forms) != len(expected):
        raise ValueError("full 12 by 8 reviewer inventory required")
    actual = {}
    named = set()
    for row in forms:
        if type(row) is not dict or set(row) != FIELDS:
            raise ValueError("review schema drift / unknown privileged field")
        if row.get("reviewer_slot") != slot:
            raise ValueError("independent reviewer slot mismatch")
        if row.get("independent_approval") is not False:
            raise ValueError("worksheet cannot self-approve a task")
        if row.get("verdict") not in VERDICTS:
            raise ValueError("unknown reviewer verdict")
        key = (row.get("candidate_id"), row.get("gate"))
        if key in actual:
            raise ValueError("duplicate candidate/gate review")
        actual[key] = row
        if row["verdict"] == "PENDING":
            if (row["reviewer_identity"] or row["evidence_refs"]
                    or row["evidence_sha256"] or row["reviewer_note"]):
                raise ValueError("pending review must not contain fabricated review evidence")
        else:
            who = row.get("reviewer_identity")
            if type(who) is not str or not who.strip() or len(who) > 128:
                raise ValueError("completed reviewer finding needs an actual reviewer identity")
            named.add(who)
            if type(row["reviewer_note"]) is not str or not row["reviewer_note"].strip():
                raise ValueError("non-pending reviewer conclusion requires reasoning")
            refs = row["evidence_refs"]
            if type(refs) is not list or any(type(ref) is not str or not ref.strip()
                                              for ref in refs):
                raise ValueError("reviewer evidence references must be a list of nonempty strings")
            evidence = row["evidence_sha256"]
            if row["verdict"] == "EVIDENCE_PRESENT_NOT_ATTESTED":
                if not refs or type(evidence) is not str or not SHA256.fullmatch(evidence):
                    raise ValueError("positive evidence observation needs refs and SHA256")
            elif evidence and (type(evidence) is not str or not SHA256.fullmatch(evidence)):
                raise ValueError("review evidence SHA256 malformed")
    if set(actual) != {
        (item["candidate_id"], item["gate"]) for item in expected
    }:
        raise ValueError("missing or unexpected candidate/gate keys")
    for item in expected:
        got = actual[(item["candidate_id"], item["gate"])]
        for name in ("candidate_id", "repository", "pr_url", "packet_sha256", "gate"):
            if got[name] != item[name]:
                raise ValueError("reviewer altered immutable PR/packet/gate identity")
    if len(named) > 1:
        raise ValueError("one reviewer slot cannot impersonate multiple identities")
    return actual, named


def adjudicate_review_disagreement(packets, reviewer_a, reviewer_b) -> PairedReviewAudit:
    """Expose disagreement and evidence gaps; NEVER automate human adjudication."""
    expected = blank_independent_forms(tuple(packets))
    a, identities_a = _validate_forms(tuple(reviewer_a), "A", expected["A"])
    b, identities_b = _validate_forms(tuple(reviewer_b), "B", expected["B"])
    if identities_a & identities_b:
        raise ValueError("independent reviewer identities must differ")
    outcomes = []
    paired_completed = 0
    pairs_agree = 0
    for item in expected["A"]:
        key = (item["candidate_id"], item["gate"])
        x, y = a[key], b[key]
        both = x["verdict"] != "PENDING" and y["verdict"] != "PENDING"
        if both:
            paired_completed += 1
            pairs_agree += (x["verdict"] == y["verdict"])
        status = ("PENDING_REVIEWS" if not both else
                  "REVIEWERS_AGREE_NOT_ADJUDICATED" if x["verdict"] == y["verdict"]
                  else "REVIEWER_DISAGREEMENT_NEEDS_ADJUDICATION")
        outcomes.append({
            "candidate_id": item["candidate_id"], "gate": item["gate"],
            "status": status, "independently_adjudicated": False,
            "task_authorized_for_experiment": False,
        })
    total = len(outcomes)
    return PairedReviewAudit(tuple(outcomes), {
        "status": "REVIEW_WORKSHEET_NO_AUTO_ADMISSION",
        "candidate_count": 12,
        "total_independent_gate_pairs": total,
        "completed_gate_pairs": paired_completed,
        "pending_gate_pairs": total - paired_completed,
        "agreement_fraction_completed_pairs": (
            None if not paired_completed else pairs_agree/paired_completed),
        "disagreements_on_completed_pairs": paired_completed-pairs_agree,
        "unresolved_independent_adjudications": total,
        "independently_admitted_executable_tasks": 0,
        "oracle_runs": 0,
        "external_code_executions": 0,
        "reviewer_A_identity_recorded": bool(identities_a),
        "reviewer_B_identity_recorded": bool(identities_b),
    })
