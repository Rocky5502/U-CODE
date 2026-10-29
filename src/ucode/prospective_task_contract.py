"""Strict public review *draft* for an independent prospective repair task.

Historical PR metadata is never rebranded as the original task specification.
The task requirements below are a NEW proposal, not independently approved,
not a policy-visible instruction, not a signed commitment, and not an oracle.
This library does not execute, fetch, authenticate, sign or approve anything.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import re
from typing import Mapping

_STAGE = "PROSPECTIVE_TASK_DRAFT_REVIEW_ONLY_NOT_POLICY_INPUT"
_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_RELATIVE = re.compile(r"[A-Za-z0-9_.+/-]+\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset((
    "schema_version", "stage", "candidate_id", "task_namespace",
    "repository", "base_sha", "source_observations",
    "proposal_creation_date", "requirement_statements",
    "task_scope", "historical_original_issue_body_attested",
    "proposed_spec_independently_reviewed", "file_reuse_rights_cleared",
    "hidden_oracle_independently_sealed", "toolchain_verified",
    "runner_physically_attested", "five_resource_meters_attested",
    "third_party_code_executed", "experiment_eligible",
))
_BLOCKED = (
    "historical_original_issue_body_attested",
    "proposed_spec_independently_reviewed",
    "file_reuse_rights_cleared",
    "hidden_oracle_independently_sealed",
    "toolchain_verified",
    "runner_physically_attested",
    "five_resource_meters_attested",
    "third_party_code_executed",
    "experiment_eligible",
)


@dataclass(frozen=True)
class ObservedSourceBlob:
    """Public read-only identity; NOT an authenticated rights statement."""
    observation_id: str
    path: str
    git_blob_sha: str

    def __post_init__(self):
        if (type(self.observation_id) is not str or
                not re.fullmatch(r"[A-Z][A-Z0-9_]{3,79}", self.observation_id)):
            raise ValueError("invalid source observation label")
        if (type(self.path) is not str or len(self.path) > 512 or
                not _RELATIVE.fullmatch(self.path) or
                any(segment in ("", ".", "..") for segment in self.path.split("/"))):
            raise ValueError("invalid relative pre-fix source path")
        if type(self.git_blob_sha) is not str or not _SHA40.fullmatch(self.git_blob_sha):
            raise ValueError("source blob must have immutable-looking SHA40")


@dataclass(frozen=True)
class ProspectiveReviewDraft:
    """Proposed requirements for EXTERNAL independent human review, no approval."""
    schema_version: str
    stage: str
    candidate_id: int
    task_namespace: str
    repository: str
    base_sha: str
    source_observations: tuple[ObservedSourceBlob, ...]
    proposal_creation_date: str
    requirement_statements: tuple[str, ...]
    task_scope: str
    historical_original_issue_body_attested: bool
    proposed_spec_independently_reviewed: bool
    file_reuse_rights_cleared: bool
    hidden_oracle_independently_sealed: bool
    toolchain_verified: bool
    runner_physically_attested: bool
    five_resource_meters_attested: bool
    third_party_code_executed: bool
    experiment_eligible: bool

    def __post_init__(self):
        if self.schema_version != "1.0" or self.stage != _STAGE:
            raise ValueError("prospective review draft cannot self-promote")
        if type(self.candidate_id) is not int or not 1 <= self.candidate_id <= 120:
            raise ValueError("candidate ID outside metadata lead cohort")
        if type(self.repository) is not str or not _REPO.fullmatch(self.repository) or any(
                x in (".", "..") for x in self.repository.split("/")):
            raise ValueError("invalid source repository identity")
        if (type(self.base_sha) is not str or
                not _SHA40.fullmatch(self.base_sha)):
            raise ValueError("pinned pre-fix Git SHA40 required")
        # Explicit prospective namespace prevents accidental joins with
        # historical PR task IDs and independently evaluated cohorts.
        if self.task_namespace != "prospective:source-lead:" + str(self.candidate_id):
            raise ValueError("prospective task must use separate namespace")
        if (type(self.proposal_creation_date) is not str or
                not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}",
                                 self.proposal_creation_date)):
            raise ValueError("explicit prospective creation date required")
        if self.task_scope not in ("new_prospective_repository_repair",
                                   "new_prospective_microtask"):
            raise ValueError("prospective full-repo/microtask scope required")
        if (type(self.source_observations) is not tuple or
                not self.source_observations or
                any(not isinstance(x, ObservedSourceBlob)
                    for x in self.source_observations)):
            raise ValueError("typed pre-fix source observation references required")
        if len(set(x.observation_id for x in self.source_observations)) != len(
                self.source_observations):
            raise ValueError("duplicate source observation IDs")
        if type(self.requirement_statements) is not tuple or not (
                2 <= len(self.requirement_statements) <= 12):
            raise ValueError("bounded new prospective requirements required")
        for statement in self.requirement_statements:
            if (type(statement) is not str or
                    not 20 <= len(statement) <= 500 or
                    any(ord(c) < 32 or ord(c) == 127 for c in statement)):
                raise ValueError("malformed/newline-bearing proposed requirement")
        # No field, caller or computed digest can grant a task admission.
        for field in _BLOCKED:
            if getattr(self, field) is not False:
                raise ValueError("public draft cannot claim independent approval or real task execution")

    @property
    def public_draft_sha256(self) -> str:
        """An *untrusted* content-change fingerprint; never a signed attestation."""
        encoded=json.dumps(asdict(self),sort_keys=True,
                           separators=(",",":"),ensure_ascii=True).encode("ascii")
        return sha256(encoded).hexdigest()

    def review_summary(self) -> dict:
        """Reviewer-facing only; explicitly forbidden for coding policy input."""
        return {
            "stage": self.stage,
            "namespace": self.task_namespace,
            "public_draft_sha256_untrusted": self.public_draft_sha256,
            "requirements_for_future_independent_review":
                len(self.requirement_statements),
            "read_only_source_observation_leads":
                len(self.source_observations),
            "historical_task_eligible": False,
            "prospective_task_eligible": False,
            "coding_agent_policy_input_approved": False,
            "hidden_oracle_authored": False,
            "real_repository_executions": 0,
            "unresolved_external_gates": list(_BLOCKED),
        }


def parse_prospective_review_draft(value: Mapping) -> ProspectiveReviewDraft:
    """Reject extra gold/PR patch fields and missing schema members."""
    if type(value) is not dict or set(value) != _FIELDS:
        raise ValueError("prospective draft requires exact safe review-only fields")
    sources=value["source_observations"]
    statements=value["requirement_statements"]
    if type(sources) is not list or type(statements) is not list:
        raise ValueError("source observations and proposals must be JSON arrays")
    allowed_source=frozenset(("observation_id", "path", "git_blob_sha"))
    if any(type(item) is not dict or set(item) != allowed_source for item in sources):
        raise ValueError("source observation schema forbids solution/test/gold data")
    return ProspectiveReviewDraft(
        **{key:value[key] for key in _FIELDS if key not in (
            "source_observations","requirement_statements")},
        source_observations=tuple(ObservedSourceBlob(**x) for x in sources),
        requirement_statements=tuple(statements),
    )


def validate_php104_prospective_draft(
    draft: ProspectiveReviewDraft, original_leads: Mapping,
) -> dict:
    """Cross-check static pinned source identities, NOT source authenticity.

    NO issue-body text, post-fix helper or PR-authored hidden test is used
    as a canonical requirement. This is a new prospective *proposal*.
    """
    if (draft.candidate_id != 104 or draft.repository != "mvdbos/php-spider"
            or draft.base_sha != "25e9b1cf855669c24ba1609c7d4cfcda17ac6217"):
        raise ValueError("PHP #104 original repository/base identity mismatch")
    if draft.proposal_creation_date < "2026-10-29":
        raise ValueError("new prospective task cannot claim creation before research draft")
    if original_leads.get("candidate_id") != 104 or original_leads.get(
            "base_commit") != draft.base_sha:
        raise ValueError("frozen source-lead evidence identity mismatch")
    original=original_leads.get("source_observations")
    if type(original) is not list:
        raise ValueError("source observation manifest required")
    expected={(r["id"],r["path"],r["git_blob_sha"]) for r in original}
    actual={(r.observation_id,r.path,r.git_blob_sha)
            for r in draft.source_observations}
    if actual != expected or len(draft.source_observations) != len(original):
        raise ValueError("prospective review draft changed pinned pre-fix source observations")
    if (original_leads.get("executable_task_admitted") is not False or
            original_leads.get("parent_issue_body_at_pr_time_archived") is not False):
        raise ValueError("historical lead metadata moved outside blocked state")
    return draft.review_summary()
