"""Fail-closed contract check BEFORE any proposed real repository execution.

This module does NOT execute software, inspect remote license texts or attest
that a human review is genuine. A 'declared_complete' result means that
required evidence *references* exist and basic invariants are satisfied;
a separate authorized reviewer and hardened sandbox must verify them.

No third-party execution should ever run on the ordinary CI host.
"""
from dataclasses import dataclass
from pathlib import PurePosixPath
import re

from .audit import is_source_path, is_test_path, source_language

FULL_SHA = re.compile(r"^[a-fA-F0-9]{40}$")
DIGEST = re.compile(r"^sha256:[a-fA-F0-9]{64}$")
COHORTS = frozenset(("naturalistic_ai_pr", "new_model_generation"))


@dataclass(frozen=True)
class TaskEvidence:
    task_id: str
    lineage_group: str
    cohort: str
    repository: str
    base_sha: str
    patch_sha: str
    changed_production_paths: tuple[str, ...]
    claimed_changed_language: str
    authorship_or_generation_review_ref: str
    source_file_rights_review_ref: str
    independent_oracle_review_ref: str
    independent_oracle_sha256: str
    sealed_evaluator_only: bool
    image_digest: str
    runtime_nonroot: bool
    runtime_network_disabled: bool
    runtime_no_host_mounts: bool
    runtime_resource_limits: bool


@dataclass(frozen=True)
class GateResult:
    """Passing this static checklist is NOT a scientifically verified task."""
    status: str
    reasons: tuple[str, ...]


def assess_task_evidence(record: TaskEvidence) -> GateResult:
    """Check required immutable references, patch language and sandbox claims."""
    reasons: list[str] = []
    for name in ("task_id", "lineage_group", "repository"):
        x = getattr(record, name)
        if not isinstance(x, str) or not x.strip():
            reasons.append(f"missing_{name}")
    if record.cohort not in COHORTS:
        reasons.append("invalid_cohort")
    if not isinstance(record.repository, str) or record.repository.count("/") != 1:
        reasons.append("invalid_repository_full_name")
    for name in ("base_sha", "patch_sha"):
        x = getattr(record, name)
        if not isinstance(x, str) or not FULL_SHA.fullmatch(x):
            reasons.append(f"not_immutable_{name}")
    if isinstance(record.base_sha, str) and isinstance(record.patch_sha, str) and (
        record.base_sha == record.patch_sha
    ):
        reasons.append("patch_equal_to_base")
    paths = record.changed_production_paths
    if not isinstance(paths, tuple) or not paths:
        reasons.append("missing_production_paths")
        paths = ()
    if len(set(paths)) != len(paths):
        reasons.append("duplicate_changed_paths")
    actual_languages = set()
    for path in paths:
        if (not isinstance(path, str) or not path.strip()
                or "\\" in path or path.startswith("/")
                or ".." in PurePosixPath(path).parts):
            reasons.append("unsafe_source_path")
        elif not is_source_path(path) or is_test_path(path):
            reasons.append("nonproduction_source_path")
        else:
            lang = source_language(path)
            if lang:
                actual_languages.add(lang)
    if record.claimed_changed_language not in actual_languages:
        reasons.append("changed_language_mismatch")
    for name in ("authorship_or_generation_review_ref",
                 "source_file_rights_review_ref",
                 "independent_oracle_review_ref"):
        ref = getattr(record, name)
        if not isinstance(ref, str) or not ref.strip():
            reasons.append(f"missing_{name}")
    if not isinstance(record.independent_oracle_sha256, str) or not DIGEST.fullmatch(
        "sha256:" + record.independent_oracle_sha256
        if isinstance(record.independent_oracle_sha256, str)
           and len(record.independent_oracle_sha256) == 64
        else str(record.independent_oracle_sha256)
    ):
        reasons.append("unhashed_independent_oracle")
    if not isinstance(record.image_digest, str) or not DIGEST.fullmatch(record.image_digest):
        reasons.append("unpinned_container_image")
    for field in ("sealed_evaluator_only", "runtime_nonroot",
                  "runtime_network_disabled", "runtime_no_host_mounts",
                  "runtime_resource_limits"):
        if getattr(record, field) is not True:
            reasons.append(f"unsafe_or_unverified_{field}")
    return GateResult(
        status="declared_complete_requires_independent_verification"
               if not reasons else "blocked",
        reasons=tuple(dict.fromkeys(reasons)),
    )
