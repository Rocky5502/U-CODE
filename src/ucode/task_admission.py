"""No-execution admission dossier for externally sourced repository tasks.

This code deliberately does NOT assert code authorship, license validity,
safe execution, or independent functional correctness. It turns metadata
leads into machine-checked *pending human evidence work*, never automatic
experiment eligibility. All input records are non-executable JSON.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_GATES = (
    "immutable_prefixed_snapshot",
    "line_level_authorship",
    "file_specific_reuse_rights",
    "independent_functional_oracle",
    "oracle_secrecy_and_split",
    "sandbox_isolation",
    "reproducible_toolchain",
    "resource_limits",
)
STATUS = {"PENDING", "FAILED", "EVIDENCE_PRESENT_NOT_ATTESTED"}


@dataclass(frozen=True)
class GateRecord:
    """A reviewable evidence claim; NOT a cryptographic signed attestation."""
    gate: str
    status: str
    evidence_refs: tuple[str, ...] = ()
    evidence_sha256: str | None = None
    reviewer: str | None = None
    reviewer_role: str | None = None
    note: str = ""

    def __post_init__(self):
        if self.gate not in REQUIRED_GATES:
            raise ValueError("unrecognized admission gate")
        if self.status not in STATUS:
            raise ValueError("status must stay pending, failed or unattested")
        if not isinstance(self.evidence_refs, tuple):
            raise ValueError("evidence_refs must be immutable")
        if any(not isinstance(p, str) or not p.strip()
               for p in self.evidence_refs):
            raise ValueError("blank or invalid evidence reference")
        if self.evidence_sha256 is not None and not SHA64.fullmatch(self.evidence_sha256):
            raise ValueError("evidence digest must be a 64-hex SHA256")
        if self.status == "EVIDENCE_PRESENT_NOT_ATTESTED" and (
                not self.evidence_refs or not self.evidence_sha256
                or not self.reviewer or not self.reviewer_role):
            raise ValueError("reported evidence requires refs, digest and named reviewer")
        if self.status == "FAILED" and not self.note:
            raise ValueError("failure requires a written reason")


@dataclass(frozen=True)
class TaskAdmissionDossier:
    candidate_id: int
    repository: str
    pr_url: str
    base_sha: str
    head_sha: str
    merge_commit_sha: str
    changed_production_paths: tuple[str, ...]
    changed_test_paths: tuple[str, ...]
    repository_spdx: str | None
    gates: tuple[GateRecord, ...]
    narrative: str
    evidence_stage: str = "MANUAL_REVIEW_ONLY"

    def __post_init__(self):
        if type(self.candidate_id) is not int or not 1 <= self.candidate_id <= 120:
            raise ValueError("candidate ID must belong to frozen 120-link pool")
        if (not isinstance(self.repository, str) or
                not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
                                 self.repository)):
            raise ValueError("invalid repository")
        number = r"[1-9][0-9]*"
        if not re.fullmatch(
            "https://github[.]com/" + re.escape(self.repository) +
            "/pull/" + number, self.pr_url):
            raise ValueError("PR URL does not match repository identity")
        if not all(SHA40.fullmatch(h) for h in (
                self.base_sha, self.head_sha, self.merge_commit_sha)):
            raise ValueError("immutable Git revision anchors are required")
        if not isinstance(self.changed_production_paths, tuple) or not self.changed_production_paths:
            raise ValueError("at least one observed production path required")
        if not isinstance(self.changed_test_paths, tuple):
            raise ValueError("test path tuple required, even when empty")
        if (len(set(self.changed_production_paths + self.changed_test_paths))
                != len(self.changed_production_paths + self.changed_test_paths)):
            raise ValueError("duplicate source/test path")
        for p in self.changed_production_paths + self.changed_test_paths:
            if not isinstance(p, str) or not p or p.startswith("/") or "\x00" in p:
                raise ValueError("bad PR-relative file path")
            if ".." in p.split("/") or "\\" in p or ":" in p or p.startswith("./"):
                raise ValueError("PR-relative path traversal or ambiguity")
        if self.evidence_stage != "MANUAL_REVIEW_ONLY":
            raise ValueError("dossier cannot declare research admission")
        if not isinstance(self.narrative, str) or not self.narrative.strip():
            raise ValueError("review narrative required")
        gate_names = [g.gate for g in self.gates]
        if len(gate_names) != len(set(gate_names)) or set(gate_names) != set(REQUIRED_GATES):
            raise ValueError("exactly one record for each required gate")


@dataclass(frozen=True)
class AdmissionAssessment:
    candidate_id: int
    stage: str
    open_gates: tuple[str, ...]
    failed_gates: tuple[str, ...]
    reported_evidence: tuple[str, ...]
    eligible_for_experiment: bool
    requires_independent_adjudication: bool


def assess_dossier(dossier: TaskAdmissionDossier) -> AdmissionAssessment:
    """A complete stack of *claimed evidence* is not proof of oracle isolation.

    Any actual promotion to an executable task must use a **separate signed
    independent human/runner approval path**, deliberately not offered here.
    """
    if not isinstance(dossier, TaskAdmissionDossier):
        raise TypeError("TaskAdmissionDossier required")
    failed = tuple(g.gate for g in dossier.gates if g.status == "FAILED")
    open_ = tuple(g.gate for g in dossier.gates if g.status == "PENDING")
    claims = tuple(g.gate for g in dossier.gates
                   if g.status == "EVIDENCE_PRESENT_NOT_ATTESTED")
    state = "REJECT_FOR_PILOT" if failed else (
        "NEEDS_EVIDENCE" if open_ else "EXTERNAL_ADJUDICATION_REQUIRED")
    return AdmissionAssessment(dossier.candidate_id, state, open_,
                               failed, claims, False, True)


def parse_dossier(obj: Mapping) -> TaskAdmissionDossier:
    """Reject unregistered approval fields while preserving historical ledger notes.

    The extra four legacy screening descriptors remain metadata-only and
    have NO admission authority; neither root SPDX nor a bot account
    attests file-level rights or authorship.
    """
    if not isinstance(obj, Mapping):
        raise ValueError("admission dossier must be an object")
    allowed = {
        "candidate_id", "repository", "pr_url", "base_sha", "head_sha",
        "merge_commit_sha", "changed_production_paths", "changed_test_paths",
        "repository_spdx", "gates", "narrative", "evidence_stage",
        "research_language", "root_license_blob_sha",
        "observed_bot_account", "coauthorship_note",
    }
    if set(obj) - allowed:
        raise ValueError("unknown dossier fields; no self-authorized admission")
    gate_allowed = {
        "gate", "status", "evidence_refs", "evidence_sha256",
        "reviewer", "reviewer_role", "note",
    }
    if not isinstance(obj.get("gates"), list):
        raise ValueError("admission gates must be an array")
    for x in obj["gates"]:
        if not isinstance(x, Mapping) or set(x) - gate_allowed:
            raise ValueError("unknown admission gate field; no oracle or approval leakage")
    gates = tuple(GateRecord(
        gate=x["gate"], status=x["status"],
        evidence_refs=tuple(x.get("evidence_refs", [])),
        evidence_sha256=x.get("evidence_sha256"),
        reviewer=x.get("reviewer"), reviewer_role=x.get("reviewer_role"),
        note=x.get("note", ""),
    ) for x in obj["gates"])
    return TaskAdmissionDossier(
        candidate_id=obj["candidate_id"], repository=obj["repository"],
        pr_url=obj["pr_url"], base_sha=obj["base_sha"],
        head_sha=obj["head_sha"], merge_commit_sha=obj["merge_commit_sha"],
        changed_production_paths=tuple(obj["changed_production_paths"]),
        changed_test_paths=tuple(obj["changed_test_paths"]),
        repository_spdx=obj.get("repository_spdx"), gates=gates,
        narrative=obj["narrative"],
        evidence_stage=obj.get("evidence_stage", "MANUAL_REVIEW_ONLY"),
    )


def validate_dossier_against_metadata(
    dossier: TaskAdmissionDossier, record: Mapping, manifest: Mapping,
) -> None:
    """Reject changed PR identity, SHAs or paths and mismatched discovery ID."""
    if dossier.candidate_id != int(record["candidate_id"]):
        raise ValueError("dossier candidate ID differs from immutable PR record")
    discovered = manifest[dossier.candidate_id]
    if (dossier.pr_url != discovered["agent_pr_url"]
            or dossier.repository != discovered["repository"]):
        raise ValueError("dossier does not match frozen discovery manifest")
    for attr, field in (
        ("base_sha", "base_sha"), ("head_sha", "head_sha"),
        ("merge_commit_sha", "merge_commit_sha")):
        if getattr(dossier, attr) != record.get(field):
            raise ValueError("dossier immutable PR SHA mismatch")
    known_paths = set(record.get("changed_paths") or [])
    if any(p not in known_paths for p in (
            dossier.changed_production_paths + dossier.changed_test_paths)):
        raise ValueError("dossier cites changed source absent from PR file list")
    if set(dossier.changed_production_paths) != set(record.get("production_files") or []):
        raise ValueError("production file set differs from canonical metadata")
    recorded_tests = record.get("test_files")
    if recorded_tests is not None and (
            set(dossier.changed_test_paths) != set(recorded_tests)):
        raise ValueError("test file set differs from canonical metadata")
    if len(dossier.changed_test_paths) != len(set(dossier.changed_test_paths)):
        raise ValueError("duplicate changed test path")
    if record.get("triage_status") != "production_source_path_detected":
        raise ValueError("dossier PR is not even a production-source-path lead")
    if dossier.repository_spdx != record.get("repository_license_spdx"):
        raise ValueError("repository SPDX differs from canonical PR metadata")


def dossier_sha256(payload: Mapping) -> str:
    """Content fingerprint of JSON record, NOT a proof of claim authenticity."""
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()
