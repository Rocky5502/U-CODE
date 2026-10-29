"""Explicit evaluator-only data boundary for prospective U-CODE tasks.

These are metadata-only registration and leakage checks. They neither
authenticate independent reviewers nor isolate untrusted executable code.
This module has no execution or network functionality and cannot admit tasks.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from urllib.parse import urlsplit

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_SCOPE = {"full_pr", "declared_microtask"}
_REQUIRED_STATUS = "PROSPECTIVE_UNSEALED"
_FORBIDDEN_ROLE = {"author", "proposer", "implementer", "candidate_author"}


def _digest(value: str) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


@dataclass(frozen=True)
class EvaluatorRegistration:
    """Frozen policy-visible identity plus evaluator-only prospective metadata.

    Security boundary is conceptual until an independently audited runner
    enforces physical storage, filesystem, process and network isolation.
    """
    candidate_id: int
    repository: str
    issue_ref: str
    task_base_sha: str
    pre_fix_spec_blob_sha: str | None
    task_scope: str
    spec_language: str
    pr_authored_test_paths: tuple[str, ...]
    policy_visible_spec_refs: tuple[str, ...]
    evaluator_only_oracle_refs: tuple[str, ...]
    oracle_commitment_sha256: str | None
    oracle_author_role: str | None
    oracle_review_group: str | None
    model_train_lineage: str | None
    model_eval_lineage: str | None
    environment_image_digest: str | None
    runner_attestation_ref: str | None
    status: str = _REQUIRED_STATUS

    def __post_init__(self):
        if type(self.candidate_id) is not int or not 1 <= self.candidate_id <= 120:
            raise ValueError("candidate ID outside frozen corpus")
        if (type(self.repository) is not str or
                not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository) or
                any(part in (".", "..") for part in self.repository.split("/"))):
            raise ValueError("valid GitHub owner/repository identity required")
        # A GitHub-looking URL must not cross to another repo, include a
        # query/fragment, or point to a post-fix PR or an attacker endpoint.
        # The historical text inside a valid issue remains UNVERIFIED.
        if (type(self.issue_ref) is not str or
                not re.fullmatch("https://github[.]com/" +
                                 re.escape(self.repository) +
                                 r"/issues/[1-9][0-9]*", self.issue_ref)):
            raise ValueError("original issue URL must match source repository")
        if not isinstance(self.task_base_sha, str) or not _SHA40.fullmatch(self.task_base_sha):
            raise ValueError("base revision must be immutable git SHA40")
        if self.pre_fix_spec_blob_sha is not None and not _SHA40.fullmatch(
                self.pre_fix_spec_blob_sha):
            raise ValueError("spec blob must be SHA40")
        if self.task_scope not in _ALLOWED_SCOPE:
            raise ValueError("scope must disclose full PR versus microtask")
        if not self.spec_language:
            raise ValueError("specification language required")
        if self.status != _REQUIRED_STATUS:
            raise ValueError("cannot self-declare oracle sealing or execution eligibility")
        if not isinstance(self.pr_authored_test_paths, tuple):
            raise ValueError("PR-authored tests must be immutable list")
        if not isinstance(self.policy_visible_spec_refs, tuple):
            raise ValueError("visible spec references must be immutable")
        if not isinstance(self.evaluator_only_oracle_refs, tuple):
            raise ValueError("evaluator-only oracle references must be immutable")
        if any(not isinstance(s, str) or not s.strip()
               for s in (*self.pr_authored_test_paths,
                         *self.policy_visible_spec_refs,
                         *self.evaluator_only_oracle_refs)):
            raise ValueError("empty paths/references forbidden")
        if len(set(self.pr_authored_test_paths)) != len(self.pr_authored_test_paths):
            raise ValueError("duplicate PR-authored test path")
        if (set(self.policy_visible_spec_refs)
                & set(self.evaluator_only_oracle_refs)):
            raise ValueError("oracle reference directly leaked into visible spec")
        if (set(self.pr_authored_test_paths)
                & set(self.evaluator_only_oracle_refs)):
            raise ValueError("PR-authored tests cannot be held-out oracle artifacts")
        # These are GitHub-prefixed pre-fix task references, never places
        # to embed arbitrary network addresses, fragments, oracle URLs,
        # post-fix blobs, paths escaping the task repository or query tokens.
        # A mutable issue URL is still NOT a frozen pre-PR specification.
        prefix = "/" + self.repository + "/"
        for ref in self.policy_visible_spec_refs:
            parsed = urlsplit(ref)
            if (parsed.scheme != "https" or parsed.netloc != "github.com"
                    or parsed.query or parsed.fragment or parsed.username
                    or parsed.password or "%" in parsed.path
                    or not parsed.path.startswith(prefix)):
                raise ValueError("unsafe policy-visible specification reference")
            local_path = parsed.path[len(prefix):]
            issue = re.fullmatch(r"issues/[1-9][0-9]*", local_path)
            blob = re.fullmatch(r"blob/([0-9a-f]{40})/(.+)", local_path)
            if issue and ref != self.issue_ref:
                raise ValueError("policy-visible issue reference not task issue")
            if blob:
                blob_path = blob.group(2)
                if blob.group(1) != self.task_base_sha or any(
                    p in ("", ".", "..") for p in blob_path.split("/")
                ) or "\\" in blob_path:
                    raise ValueError("policy-visible spec must use pre-fix base")
            if not issue and not blob:
                raise ValueError("policy-visible spec must be task issue or pinned blob")
        if (self.oracle_commitment_sha256 is not None
                and not _digest(self.oracle_commitment_sha256)):
            raise ValueError("oracle commitment must be SHA256")
        if self.oracle_author_role is not None and self.oracle_author_role.lower() in _FORBIDDEN_ROLE:
            raise ValueError("oracle author cannot declare candidate implementer role")
        if self.model_train_lineage is not None and (
                self.model_train_lineage == self.model_eval_lineage):
            raise ValueError("training and evaluation lineage must differ")
        if (self.environment_image_digest is not None and
                not self.environment_image_digest.startswith("sha256:")):
            raise ValueError("execution image reference must be content-addressed")
        if self.environment_image_digest is not None and not _digest(
                self.environment_image_digest[len("sha256:"):]):
            raise ValueError("execution image digest must have 64 lowercase hex digits")


def policy_visible_registration(r: EvaluatorRegistration) -> dict:
    """Strict allowlist: oracle references/digests and evaluator labels absent.

    Even this serialized view must be inspected by an independent runner for
    secret-in-spec leakage and must not be used as a security isolation claim.
    """
    return {
        "candidate_id": r.candidate_id,
        "repository": r.repository,
        "issue_ref": r.issue_ref,
        "task_base_sha": r.task_base_sha,
        "task_scope": r.task_scope,
        "spec_language": r.spec_language,
        "policy_visible_spec_refs": list(r.policy_visible_spec_refs),
    }


def evaluate_registration(r: EvaluatorRegistration) -> dict:
    """Fail closed: metadata may help plan, never authorize execution."""
    reasons = []
    if r.pre_fix_spec_blob_sha is None:
        reasons.append("no_immutable_pre_fix_spec_blob")
    if not r.policy_visible_spec_refs:
        reasons.append("no_policy_visible_pre_fix_spec")
    if not r.evaluator_only_oracle_refs:
        reasons.append("no_separate_evaluator_oracle")
    if r.oracle_commitment_sha256 is None:
        reasons.append("oracle_not_committed")
    if r.oracle_author_role is None or r.oracle_review_group is None:
        reasons.append("independent_oracle_review_missing")
    if r.model_train_lineage is None or r.model_eval_lineage is None:
        reasons.append("group_disjointness_unverified")
    if r.environment_image_digest is None:
        reasons.append("runtime_image_unpinned")
    if r.runner_attestation_ref is None:
        reasons.append("isolated_runner_not_attested")
    if r.task_scope == "declared_microtask":
        reasons.append("microtask_not_full_pr_correctness")
    return {
        "candidate_id": r.candidate_id,
        "readiness": "BLOCKED_INDEPENDENT_ATTESTATION_REQUIRED",
        "missing_or_unverified": reasons,
        "policy_view_digest_sha256": sha256(json.dumps(
            policy_visible_registration(r),
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest(),
        "independently_admitted": False,
        "oracle_evaluations": 0,
    }


def registration_from_json(v: dict) -> EvaluatorRegistration:
    allowed = set(EvaluatorRegistration.__dataclass_fields__)
    if set(v) - allowed:
        raise ValueError("unknown registration fields; reject possible gold/test leakage")
    args = dict(v)
    for x in ("pr_authored_test_paths", "policy_visible_spec_refs",
              "evaluator_only_oracle_refs"):
        args[x] = tuple(v[x])
    return EvaluatorRegistration(**args)
