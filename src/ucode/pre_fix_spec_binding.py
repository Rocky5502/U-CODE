"""Read-only Go #43 pre-fix specification object crosswalk (NO task admission).

This module binds a candidate evaluator registration's public source ref to
a GitHub base-tree *entry* observed in an immutable commit tree, rather than
trusting a free-standing 40-hex string in a reviewer registration.

The caller-supplied metadata and version-pinned constants do NOT authenticate
GitHub, archival creation time, normative sufficiency, independent review,
source-file rights, hidden oracles or an execution sandbox.
"""
from __future__ import annotations

from datetime import date
import re
from typing import Mapping

from .evaluator_boundary import EvaluatorRegistration

_GO_ID = 43
_PHP_ID = 104
_GO_REPO = "PlayHuai/eighty-point-huai-an"
_GO_COMMIT = "ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a"
_GO_TREE = "e53fb011857926632c4a4ec8752425e0f2b41559"
_GO_DOC = "docs/design.md"
_GO_DOC_BLOB = "b566ca7627b6518670a866a6a637bd5257e947f4"
_GO_DOC_SIZE = 16052
_GO_URI = (
    f"https://github.com/{_GO_REPO}/blob/{_GO_COMMIT}/{_GO_DOC}"
)
_GO_SOURCE_API = (
    "GitHub REST git/trees/" + _GO_TREE + "?recursive=1"
)
_PHP_REPO = "mvdbos/php-spider"
_PHP_ISSUE = "https://github.com/mvdbos/php-spider/issues/168"
_PHP_COMMIT = "25e9b1cf855669c24ba1609c7d4cfcda17ac6217"
_FIELDS = frozenset((
    "schema_version", "stage", "observed_on", "source_api",
    "candidate_id", "repository", "task_base_sha", "base_tree_sha",
    "spec_path", "spec_blob_sha", "spec_blob_size_bytes",
    "spec_blob_type", "spec_blob_mode", "source_tree_truncated",
    "source_content_executed", "pre_pr_issue_body_version_proven",
    "document_normatively_approved_as_full_pr_spec",
    "independent_oracle_sealed", "source_file_rights_cleared",
    "experiment_eligible",
))
_FALSE_FIELDS = (
    "source_tree_truncated", "source_content_executed",
    "pre_pr_issue_body_version_proven",
    "document_normatively_approved_as_full_pr_spec",
    "independent_oracle_sealed", "source_file_rights_cleared",
    "experiment_eligible",
)


def verify_go43_document_tree_binding(
    snapshot: Mapping,
    go_registration: EvaluatorRegistration,
    original_tree_inventory: Mapping,
) -> dict:
    """Require an exact, independently inspectable pre-fix file *identity*.

    Official observed source tree entry:
      docs/design.md; regular Git blob mode 100644; 16052 bytes;
      blob b566ca... at commit ec41b..., tree e53fb...

    A correct Git blob/commit correspondence is a source-identity property,
    NOT proof that this broad design doc specifies the 2026-10 PR correctly.
    """
    if type(snapshot) is not dict or set(snapshot) != _FIELDS:
        raise ValueError("pre-fix design document snapshot schema drift")
    expected = {
        "schema_version": "1.0",
        "stage": "GO43_PRE_FIX_DOCUMENT_BLOB_METADATA_ONLY",
        "source_api": _GO_SOURCE_API,
        "candidate_id": _GO_ID,
        "repository": _GO_REPO,
        "task_base_sha": _GO_COMMIT,
        "base_tree_sha": _GO_TREE,
        "spec_path": _GO_DOC,
        "spec_blob_sha": _GO_DOC_BLOB,
        "spec_blob_size_bytes": _GO_DOC_SIZE,
        "spec_blob_type": "blob",
        "spec_blob_mode": "100644",
    }
    for key, value in expected.items():
        if type(snapshot[key]) is not type(value) or snapshot[key] != value:
            raise ValueError("document tree entry differs from pinned source: "+key)
    if type(snapshot["observed_on"]) is not str:
        raise ValueError("noncanonical observation date")
    try:
        observed = date.fromisoformat(snapshot["observed_on"])
    except ValueError as exc:
        raise ValueError("invalid source observation date") from exc
    if observed.isoformat() != snapshot["observed_on"] or observed < date(2026, 10, 30):
        raise ValueError("noncanonical/retrospective source observation date")
    if any(snapshot[key] is not False for key in _FALSE_FIELDS):
        raise ValueError("tree metadata cannot approve oracle, rights or execution")
    if type(original_tree_inventory) is not dict:
        raise ValueError("typed original tree inventory required")
    rows = original_tree_inventory.get("records")
    if type(rows) is not list or len(rows) != 2:
        raise ValueError("two historical PHP/Go base tree records required")
    by_id = {}
    for row in rows:
        if type(row) is not dict or type(row.get("candidate_id")) is not int:
            raise ValueError("invalid original tree identity")
        if row["candidate_id"] in by_id:
            raise ValueError("duplicate tree identity")
        by_id[row["candidate_id"]] = row
    if set(by_id) != {_GO_ID, _PHP_ID}:
        raise ValueError("canonical original tree identities absent")
    go_tree = by_id[_GO_ID]
    if (go_tree.get("repository") != _GO_REPO
            or go_tree.get("base_commit") != _GO_COMMIT
            or go_tree.get("base_tree_sha") != _GO_TREE
            or go_tree.get("tree_recursion_truncated") is not False):
        raise ValueError("pre-fix source tree contradicts original frozen inventory")
    if not isinstance(go_registration, EvaluatorRegistration):
        raise TypeError("typed evaluator registration required")
    if (go_registration.candidate_id != _GO_ID
            or go_registration.repository != _GO_REPO
            or go_registration.task_base_sha != _GO_COMMIT
            or go_registration.pre_fix_spec_blob_sha != _GO_DOC_BLOB
            or go_registration.policy_visible_spec_refs != (_GO_URI,)):
        raise ValueError(
            "Go registration unbound: immutable pre-fix document URL/blob mismatch"
        )
    return {
        "candidate_id": _GO_ID,
        "status": "IMMUTABLE_BASE_DOCUMENT_IDENTITY_MATCHED_NOT_APPROVED_SPEC",
        "pre_fix_document_blob_sha": _GO_DOC_BLOB,
        "pre_fix_document_path": _GO_DOC,
        "metadata_tree_entry_consistent": True,
        "historical_issue_body_version_authenticated": False,
        "full_pr_behavioral_specification_approved": False,
        "independent_functional_oracle_available": False,
        "eligible_for_real_experiment": False,
    }


def verify_php104_mutable_issue_quarantine(
    php_registration: EvaluatorRegistration,
) -> dict:
    """An issue URL/creation time cannot prove the body at historical cutoff.

    The new PHP prospective draft is a *different task namespace*, not an
    attested source-era original-issue snapshot. This historical record may
    NOT self-declare a pre-fix specification from a fake blob SHA or URL.
    """
    if not isinstance(php_registration, EvaluatorRegistration):
        raise TypeError("typed evaluator registration required")
    if (php_registration.candidate_id != _PHP_ID
            or php_registration.repository != _PHP_REPO
            or php_registration.task_base_sha != _PHP_COMMIT
            or php_registration.issue_ref != _PHP_ISSUE
            or php_registration.pre_fix_spec_blob_sha is not None
            or php_registration.policy_visible_spec_refs != (_PHP_ISSUE,)):
        raise ValueError("unverified PHP historical issue cannot be a pinned spec")
    return {
        "candidate_id": _PHP_ID,
        "status": "MUTABLE_HISTORICAL_ISSUE_BODY_QUARANTINED",
        "original_issue_body_at_pre_pr_cutoff_verified": False,
        "independent_specification_approved": False,
        "policy_input_authorized": False,
        "eligible_for_real_experiment": False,
    }
