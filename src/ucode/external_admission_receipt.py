"""Offline Ed25519 verification of external G5 evidence envelopes (NO ADMISSION).

Security design:
* Signatures cover immutable, canonical, schema-versioned bytes binding the
  source-era task, declared specification, hidden-oracle commitment, sealed
  runner/toolchain, rights, split, and five-resource meter to each gate.
* Public verification keys are supplied via a SEPARATELY APPROVED OFFLINE
  trust policy. Never trust keys or approval flags embedded in reviewer forms.
* Require both reviewer slots and gate-specific independently governed roles.
* Signature checks prove only key possession and message integrity, NOT the
  human's identity/independence, source rights, oracle quality, sandbox
  isolation, physical metering or the actual content matching its digest.
* Even 16 mathematically verified signatures can NEVER authorize execution.
  A separately secured runner-side admission process must do that. This
  source-only package deliberately has no execute/admit entry point.
* Never commit completed private receipts, public keys tied to reviewers,
  source spec, hidden oracle details, private signing keys or reviewer notes.

Optional dependency: install the project's [admission] extra for cryptography.
All tests use freshly generated in-memory SYNTHETIC keys/receipts only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Mapping, Sequence

from .task_admission import REQUIRED_GATES

_SHA40=re.compile(r"^[0-9a-f]{40}$")
_SHA256=re.compile(r"^[0-9a-f]{64}$")
_ED25519_SIGNATURE=re.compile(r"^[0-9a-f]{128}$")
_TIME=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_REPOSITORY=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_VERSION="ucode-external-evidence-v1"
_SIGNATURE_DOMAIN=b"UCODE:EXTERNAL-ADMISSION-EVIDENCE:V1\n"
_ROLES={
    "immutable_prefixed_snapshot":"source_provenance",
    "line_level_authorship":"source_authorship",
    "file_specific_reuse_rights":"rights",
    "independent_functional_oracle":"oracle",
    "oracle_secrecy_and_split":"oracle",
    "sandbox_isolation":"runner_security",
    "reproducible_toolchain":"runner_security",
    "resource_limits":"resource_meters",
}
if set(_ROLES)!=set(REQUIRED_GATES):
    raise RuntimeError("signature role assignments do not cover admission gates")


def _hex(text: str, count: int, name: str):
    if (type(text) is not str or
            not (_SHA256 if count==64 else _SHA40).fullmatch(text)):
        raise ValueError(name+" requires lower-case SHA digest")


def _utc(text: str) -> datetime:
    if type(text) is not str or not _TIME.fullmatch(text):
        raise ValueError("UTC reviewer issue/expiry timestamp required")
    try:
        value=datetime.strptime(text,"%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError("invalid UTC reviewer timestamp") from exc
    return value.replace(tzinfo=timezone.utc)


def _canonical(obj: dict) -> bytes:
    # Explicit ASCII canonicalization; JSON strings/field names are validated
    # through typed dataclasses. Data is not automatically trusted.
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("utf-8")


@dataclass(frozen=True)
class ExternalTaskBinding:
    """Opaque immutable artifact *identifiers*; no source/oracle contents."""
    candidate_id: int
    repository: str
    pr_url: str
    task_base_sha40: str
    task_scope: str
    prospective_dossier_sha256: str
    source_era_spec_sha256: str
    independent_oracle_commitment_sha256: str
    sandbox_image_digest: str
    toolchain_lock_sha256: str
    resource_meter_profile_sha256: str
    repo_lineage_split_sha256: str
    rights_decision_sha256: str
    schema_version: str = _VERSION

    def __post_init__(self):
        if type(self.candidate_id) is not int or self.candidate_id not in (43,104):
            raise ValueError("only frozen PHP/Go pilot candidates supported")
        if (type(self.repository) is not str
                or not _REPOSITORY.fullmatch(self.repository)
                or any(x in (".","..") for x in self.repository.split("/"))):
            raise ValueError("immutable task repository identity required")
        if (type(self.pr_url) is not str or not
                re.fullmatch(r"https://github[.]com/"+re.escape(self.repository)+
                             r"/pull/[1-9][0-9]*",self.pr_url)):
            raise ValueError("PR must match exact repository and no redirects/query")
        _hex(self.task_base_sha40,40,"task base")
        if self.task_scope not in ("full_pr","declared_microtask"):
            raise ValueError("declaration must identify full PR or microtask")
        for name in (
            "prospective_dossier_sha256","source_era_spec_sha256",
            "independent_oracle_commitment_sha256","toolchain_lock_sha256",
            "resource_meter_profile_sha256","repo_lineage_split_sha256",
            "rights_decision_sha256",
        ):
            _hex(getattr(self,name),64,name)
        if (type(self.sandbox_image_digest) is not str or
                not self.sandbox_image_digest.startswith("sha256:")):
            raise ValueError("sandbox image must be OCI SHA256 digest")
        _hex(self.sandbox_image_digest[7:],64,"sandbox image")
        if self.schema_version!=_VERSION:
            raise ValueError("unsupported external evidence schema")

    def canonical_bytes(self) -> bytes:
        return _canonical({
            "schema_version":self.schema_version,
            "candidate_id":self.candidate_id,
            "repository":self.repository,
            "pr_url":self.pr_url,
            "task_base_sha40":self.task_base_sha40,
            "task_scope":self.task_scope,
            "prospective_dossier_sha256":self.prospective_dossier_sha256,
            "source_era_spec_sha256":self.source_era_spec_sha256,
            "independent_oracle_commitment_sha256":
                self.independent_oracle_commitment_sha256,
            "sandbox_image_digest":self.sandbox_image_digest,
            "toolchain_lock_sha256":self.toolchain_lock_sha256,
            "resource_meter_profile_sha256":self.resource_meter_profile_sha256,
            "repo_lineage_split_sha256":self.repo_lineage_split_sha256,
            "rights_decision_sha256":self.rights_decision_sha256,
        })

    @property
    def binding_sha256(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class TrustedExternalSigner:
    """A key supplied by a separately established independent trust policy.

    A public key and a role string do NOT alone prove an actual human's
    independence, authority or reviewer eligibility.
    """
    key_id: str
    public_key_hex: str
    gate_role: str
    reviewer_slot: str

    def __post_init__(self):
        if (type(self.key_id) is not str or
                not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}",self.key_id)):
            raise ValueError("nonempty stable signer key ID required")
        _hex(self.public_key_hex,64,"Ed25519 public key")
        if self.gate_role not in set(_ROLES.values()):
            raise ValueError("unknown independently approved review role")
        if self.reviewer_slot not in ("A","B"):
            raise ValueError("reviewer slot must be A or B")


@dataclass(frozen=True)
class ExternalGateSignature:
    """Detached signed *claim*, not a task admit/execute certificate."""
    candidate_id: int
    gate: str
    reviewer_slot: str
    signer_key_id: str
    binding_sha256: str
    evidence_sha256: str
    issued_at_utc: str
    expires_at_utc: str
    signature_hex: str
    schema_version: str = _VERSION

    def __post_init__(self):
        if type(self.candidate_id) is not int or self.candidate_id not in (43,104):
            raise ValueError("unknown candidate ID in detached evidence")
        if self.gate not in REQUIRED_GATES:
            raise ValueError("unknown signed evidence gate")
        if self.reviewer_slot not in ("A","B"):
            raise ValueError("unknown reviewer slot")
        if (type(self.signer_key_id) is not str or
                not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}",self.signer_key_id)):
            raise ValueError("invalid signer identity")
        _hex(self.binding_sha256,64,"binding")
        _hex(self.evidence_sha256,64,"evidence")
        if (type(self.signature_hex) is not str or
                not _ED25519_SIGNATURE.fullmatch(self.signature_hex)):
            raise ValueError("Ed25519 detached signature must be 64 bytes")
        issued=_utc(self.issued_at_utc)
        expiry=_utc(self.expires_at_utc)
        if expiry<=issued:
            raise ValueError("signature expires before issue")
        if (expiry-issued).total_seconds()>366*86400:
            raise ValueError("signature validity window exceeds 366 days")
        if self.schema_version!=_VERSION:
            raise ValueError("unknown signed evidence envelope schema")

    def message_bytes(self) -> bytes:
        return _SIGNATURE_DOMAIN+_canonical({
            "schema_version":self.schema_version,
            "candidate_id":self.candidate_id,
            "gate":self.gate,
            "reviewer_slot":self.reviewer_slot,
            "signer_key_id":self.signer_key_id,
            "binding_sha256":self.binding_sha256,
            "evidence_sha256":self.evidence_sha256,
            "issued_at_utc":self.issued_at_utc,
            "expires_at_utc":self.expires_at_utc,
        })


def assert_binding_matches_frozen_pilot(
    binding: ExternalTaskBinding, prospective_pilot: Mapping
) -> None:
    """Exact source-era identity checks against the canonical metadata pilot.

    A matching pilot still has all gates unapproved: checking metadata does
    not create an authenticated source-era specification or oracle.
    """
    if type(prospective_pilot) is not dict:
        raise TypeError("prospective pilot source metadata dictionary required")
    if (prospective_pilot.get("qualified_executable_tasks")!=0
            or prospective_pilot.get("independent_hidden_oracles_sealed")!=0
            or prospective_pilot.get("external_source_executed") is not False):
        raise ValueError("self-promoted public pilot is not an admission authority")
    candidates=prospective_pilot.get("candidates")
    if (type(candidates) is not list or len(candidates)!=2
            or [x.get("candidate_id") for x in candidates]!=[43,104]):
        raise ValueError("frozen pilot candidate cohort changed")
    row=next(x for x in candidates if x["candidate_id"]==binding.candidate_id)
    expected=(row["repository"],row["pr_url"],
              row["immutable_pre_fix_base_sha40"],row["task_scope"],
              row["dossier_sha256"])
    observed=(binding.repository,binding.pr_url,binding.task_base_sha40,
              binding.task_scope,binding.prospective_dossier_sha256)
    if observed!=expected:
        raise ValueError("external task envelope conflicts with source-era PR dossier")
    if (row.get("open_gate_count")!=8
            or row.get("independently_qualified") is not False
            or row.get("external_execution_allowed") is not False):
        raise ValueError("unapproved source-era dossier must remain review-only")


def verify_external_evidence_claims(
    binding: ExternalTaskBinding,
    receipts: Sequence[ExternalGateSignature],
    trusted_signers: Mapping[str,TrustedExternalSigner],
    *, prospective_pilot: dict, verification_time_utc: str,
) -> dict:
    """Check Ed25519 signatures offline; **always** refuse admission.

    Caller-supplied trust registry is a prerequisite, not an independently
    authenticated root. Verify that registry OUTSIDE this source-only code
    with an approved human authority. Verification here cannot inspect
    evidence content or validate legal/security findings.
    """
    if not isinstance(binding,ExternalTaskBinding):
        raise TypeError("frozen external task binding required")
    assert_binding_matches_frozen_pilot(binding,prospective_pilot)
    now=_utc(verification_time_utc)
    if (type(receipts) not in (tuple,list) or
            len(receipts)!=2*len(REQUIRED_GATES)):
        raise ValueError("exactly sixteen signed reviewer gate records required")
    if (type(trusted_signers) is not dict or
            not trusted_signers):
        raise ValueError("separately anchored external signer registry required")
    # Detect aliased public keys between distinct key IDs/reviewer roles.
    if any(type(k) is not str or not isinstance(v,TrustedExternalSigner)
           or k!=v.key_id for k,v in trusted_signers.items()):
        raise ValueError("malformed independent trust-anchor registry")
    pub=[k.public_key_hex for k in trusted_signers.values()]
    if len(pub)!=len(set(pub)):
        raise ValueError("aliased verifier public keys break role independence")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("install the optional [admission] cryptography extra") from exc

    pairs=set()
    by_gate={}
    for receipt in receipts:
        if not isinstance(receipt,ExternalGateSignature):
            raise ValueError("typed signed evidence records only")
        if (receipt.candidate_id!=binding.candidate_id or
                receipt.binding_sha256!=binding.binding_sha256):
            raise ValueError("receipt bound to a different immutable task context")
        pair=(receipt.gate,receipt.reviewer_slot)
        if pair in pairs:
            raise ValueError("duplicate reviewer slot on an admission gate")
        pairs.add(pair)
        if (receipt.signer_key_id not in trusted_signers):
            raise ValueError("untrusted signer's public key")
        signer=trusted_signers[receipt.signer_key_id]
        if (signer.reviewer_slot!=receipt.reviewer_slot or
                signer.gate_role!=_ROLES[receipt.gate]):
            raise ValueError("gate role and reviewer slot must match independent trust policy")
        if not _utc(receipt.issued_at_utc)<=now<_utc(receipt.expires_at_utc):
            raise ValueError("reviewer signed claim not valid at verification time")
        try:
            Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(signer.public_key_hex)
            ).verify(
                bytes.fromhex(receipt.signature_hex),receipt.message_bytes()
            )
        except (InvalidSignature,ValueError) as exc:
            raise ValueError("invalid detached Ed25519 evidence signature") from exc
        by_gate.setdefault(receipt.gate,[]).append(signer.public_key_hex)
    expected={(gate,slot) for gate in REQUIRED_GATES for slot in ("A","B")}
    if pairs!=expected:
        raise ValueError("missing independent reviewer gate signature")
    for gate,keys in by_gate.items():
        if len(keys)!=2 or len(set(keys))!=2:
            raise ValueError("both reviewer slots must use distinct signer keys")
    # The source repository has no ability to authenticate the externally
    # selected trust anchors, verify evidence bytes, attest review independence
    # or approve real execution. A valid signature cannot change that.
    return {
        "stage":"OFFLINE_EXTERNAL_SIGNATURE_CHECK_ONLY_NOT_ADMITTED",
        "candidate_id":binding.candidate_id,
        "binding_sha256":binding.binding_sha256,
        "signed_claims_verified":len(receipts),
        "reviewed_evidence_gates":len(REQUIRED_GATES),
        "all_signatures_valid_under_supplied_keys":True,
        "external_human_identity_independently_attested":False,
        "evidence_contents_validated":False,
        "sealed_oracle_independently_attested":False,
        "physical_sandbox_independently_attested":False,
        "scientific_task_admitted":False,
        "external_code_execution_authorized":False,
        "independent_runner_attestation_required":True,
    }
