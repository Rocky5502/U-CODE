"""Private Go #43 domain decision concordance, with no executable-task admission.

Only an INDEPENDENT human domain owner may resolve historical game semantics.
These first-party structs validate privacy, source pins and disagreement
categories; no reviewer identity/evidence is authenticated and no oracle is
built, imported, executed or exposed to the coding policy.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import re

_STAGE = "GO43_SPEC_CONSISTENCY_REVIEW_ONLY_NOT_EXECUTABLE"
_REVIEW_STATES = frozenset((
    "PENDING", "RULE_MEMO_PRESENT_NOT_ATTESTED",
    "INSUFFICIENT_SOURCE_ERA_EVIDENCE", "REJECT_PROPOSED_TASK_SCOPE",
))
_FIELDS = frozenset((
    "candidate_id", "base_commit_sha40", "design_git_blob_sha40",
    "business_rules_git_blob_sha40", "ambiguity_id", "source_section",
    "reviewer_slot", "reviewer_identity", "verdict", "decision_memo_sha256",
    "normative_source_refs", "reviewer_note", "independent_approval",
))
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _require_packet(packet: dict) -> tuple[dict, ...]:
    if type(packet) is not dict or packet.get("stage") != _STAGE:
        raise ValueError("canonical verified source-era Go question packet required")
    if (packet.get("candidate_id") != 43
            or packet.get("task_scope") != "declared_microtask_not_full_PR"
            or packet.get("pinned_base_commit") != "ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a"
            or packet.get("task_admitted") is not False
            or packet.get("oracle_sealed") is not False
            or packet.get("external_execution_authorized") is not False
            or packet.get("independent_human_spec_resolution_received") is not False
            or packet.get("case_expected_outputs_included") is not False):
        raise ValueError("unapproved source-era packet cannot be promoted")
    docs = packet.get("pinned_original_documents")
    if type(docs) is not list or docs != [
        {"path": "docs/design.md",
         "git_blob_sha40": "b566ca7627b6518670a866a6a637bd5257e947f4"},
        {"path": "docs/淮安80分业务规则.md",
         "git_blob_sha40": "e71288e3127cb66f2471a5ddd2800092db0552cc"},
    ]:
        raise ValueError("two original documents required at one pre-fix base")
    items = packet.get("independent_decision_dependencies")
    if type(items) is not list or len(items) != 6:
        raise ValueError("exact six independent ambiguity questions required")
    ids = set()
    for entry in items:
        if (type(entry) is not dict
                or set(entry) != {"ambiguity_id", "original_section", "status",
                                  "affected_prospective_case_families"}
                or type(entry["ambiguity_id"]) is not str
                or not entry["ambiguity_id"]
                or entry["ambiguity_id"] in ids
                or entry.get("status") != "AWAITING_INDEPENDENT_DOMAIN_DECISION"):
            raise ValueError("Go ambiguity register malformed or self-resolved")
        ids.add(entry["ambiguity_id"])
    return tuple(items)


def blank_go43_domain_decisions(packet: dict) -> dict[str, tuple[dict, ...]]:
    """Create two *uncompleted* source-pinned inventories; no human reviews."""
    items = _require_packet(packet)
    output = {}
    for slot in ("A", "B"):
        output[slot] = tuple({
            "candidate_id": 43,
            "base_commit_sha40": packet["pinned_base_commit"],
            "design_git_blob_sha40": packet["pinned_original_documents"][0]["git_blob_sha40"],
            "business_rules_git_blob_sha40": packet["pinned_original_documents"][1]["git_blob_sha40"],
            "ambiguity_id": entry["ambiguity_id"],
            "source_section": entry["original_section"],
            "reviewer_slot": slot,
            "reviewer_identity": "",
            "verdict": "PENDING",
            "decision_memo_sha256": "",
            "normative_source_refs": [],
            "reviewer_note": "",
            "independent_approval": False,
        } for entry in items)
    return output


def _bounded_note(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and len(value) <= 2048


def _validate_one(
    actual: tuple[dict, ...], slot: str, expected: tuple[dict, ...]
) -> tuple[dict[str, dict], set[str]]:
    if type(actual) not in (tuple, list) or len(actual) != len(expected):
        raise ValueError("exact six Go domain decision rows per reviewer required")
    rows = {}
    names = set()
    immutable = (
        "candidate_id", "base_commit_sha40", "design_git_blob_sha40",
        "business_rules_git_blob_sha40", "ambiguity_id",
        "source_section", "reviewer_slot", "independent_approval",
    )
    originals = {r["ambiguity_id"]: r for r in expected}
    for obj in actual:
        if type(obj) is not dict or set(obj) != _FIELDS:
            raise ValueError("private Go decision schema drift or privileged field")
        key = obj.get("ambiguity_id")
        if key not in originals or key in rows:
            raise ValueError("unexpected or duplicate Go decision")
        base = originals[key]
        if any(type(obj.get(k)) is not type(base[k]) or obj[k] != base[k] for k in immutable):
            raise ValueError("original source pins, reviewer slot or nonapproval status altered")
        if obj.get("verdict") not in _REVIEW_STATES:
            raise ValueError("unknown domain reviewer verdict")
        if obj["verdict"] == "PENDING":
            if (obj["reviewer_identity"] != "" or obj["decision_memo_sha256"] != ""
                    or obj["normative_source_refs"] != [] or obj["reviewer_note"] != ""):
                raise ValueError("pending review must have no submitted private content")
        else:
            name = obj["reviewer_identity"]
            if not _bounded_note(name) or len(name) > 128:
                raise ValueError("completed review requires one bounded reviewer identity")
            names.add(name)
            if not _bounded_note(obj["reviewer_note"]):
                raise ValueError("completed review requires private rationale")
            refs = obj["normative_source_refs"]
            digest = obj["decision_memo_sha256"]
            if (type(refs) is not list or len(refs) > 8
                    or any(not _bounded_note(ref) or len(ref) > 512 for ref in refs)
                    or len(refs) != len(set(refs))):
                raise ValueError("invalid private source references")
            if obj["verdict"] == "RULE_MEMO_PRESENT_NOT_ATTESTED":
                if not refs or type(digest) is not str or not _SHA.fullmatch(digest):
                    raise ValueError("claimed rule memo requires refs and valid digest")
            elif digest != "" or refs:
                raise ValueError("unresolved or rejected rules must not masquerade as memo")
        rows[key] = obj
    if len(names) > 1:
        raise ValueError("one reviewer slot cannot mix identities")
    return rows, names


def triage_private_go43_domain_decisions(
    packet: dict, reviewer_a: tuple[dict, ...],
    reviewer_b: tuple[dict, ...],
) -> dict:
    """Redacted A/B claim concordance, never authenticated human adjudication.

    Matching digest is at most agreement on a caller-declared hash. It is
    neither human reviewer independence nor a valid oracle or authorization.
    """
    expected = blank_go43_domain_decisions(packet)
    a, na = _validate_one(reviewer_a, "A", expected["A"])
    b, nb = _validate_one(reviewer_b, "B", expected["B"])
    if na & nb:
        raise ValueError("two reviewer slots may not claim the same identity")
    statuses = []
    for row in expected["A"]:
        key = row["ambiguity_id"]
        x, y = a[key], b[key]
        if x["verdict"] == "PENDING" or y["verdict"] == "PENDING":
            status = "PENDING_INDEPENDENT_DOMAIN_REVIEW"
        elif x["verdict"] != y["verdict"]:
            status = "DIVERGENT_VERDICT_NEEDS_INDEPENDENT_ADJUDICATION"
        elif x["verdict"] == "RULE_MEMO_PRESENT_NOT_ATTESTED":
            if x["decision_memo_sha256"] != y["decision_memo_sha256"]:
                status = "DIVERGENT_MEMO_DIGEST_NEEDS_INDEPENDENT_ADJUDICATION"
            elif set(x["normative_source_refs"]) != set(y["normative_source_refs"]):
                status = "DIVERGENT_SOURCE_REFS_NEEDS_INDEPENDENT_ADJUDICATION"
            else:
                status = "MATCHING_UNVERIFIED_RULE_MEMO_CLAIMS_NOT_ADJUDICATED"
        elif x["verdict"] == "REJECT_PROPOSED_TASK_SCOPE":
            status = "BOTH_REJECT_SCOPE_NO_TASK_ADMISSION"
        else:
            status = "BOTH_INSUFFICIENT_SOURCE_EVIDENCE_NO_TASK_ADMISSION"
        statuses.append({
            "ambiguity_id": key,
            "triage_status": status,
            "independently_adjudicated": False,
            "oracle_case_gold_authorized": False,
        })
    counts = Counter(x["triage_status"] for x in statuses)
    return {
        "schema_version": "1.0",
        "stage": "PRIVATE_GO43_DOMAIN_REVIEW_TRIAGE_REDACTED_NO_APPROVAL",
        "candidate_id": 43,
        "original_pre_fix_base": packet["pinned_base_commit"],
        "total_domain_questions": 6,
        "statuses_public_ids_only": statuses,
        "counts_by_status": dict(sorted(counts.items())),
        "independent_human_identity_authenticated": False,
        "human_adjudication_completed": False,
        "rule_memoranda_contents_authenticated": False,
        "specification_normatively_approved": False,
        "task_admitted": False,
        "hidden_oracle_sealed": False,
        "external_source_executed": False,
        "real_model_results": 0,
        "remaining_php_go_admission_gates": 16,
        "warning": (
            "Agreement, even on all six private rule memo hashes, is only "
            "unverified supplied-claim concordance. Independent domain, "
            "rights, oracle and sandbox authorization are external."
        ),
    }
