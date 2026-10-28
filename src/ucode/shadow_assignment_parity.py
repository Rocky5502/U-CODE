"""Prospective parity audit for assigned, evaluator-blind policy opportunities.

A matching budget alone does not mean two search policies received the same
candidate-generation opportunities. This module audits the *assigned* public
task context, candidate archive, opportunity catalogue, tool access and
hardware/model identity for every policy in the complete frozen matrix.

It is deliberately SHADOW/PLANNING ONLY. A SHA field is a declared identity,
not an authenticated attestation; real source access, sealed oracles, measured
costs, independent execution and model inference are NOT implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import re

from .experiment_contract import FrozenStudy
from .vector_policy import RESOURCE_FIELDS, ResourceVector

_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_STAGE = "SHADOW_ASSIGNMENT_NOT_EXECUTED"


def _check_digest(value: str, sha40: bool = False) -> None:
    if (type(value) is not str or
            not (_SHA40 if sha40 else _SHA256).fullmatch(value)):
        raise ValueError("immutable public identity must be lowercase SHA40/SHA256")


@dataclass(frozen=True)
class AssignedOpportunity:
    task_id: str
    lineage_group: str
    model_id: str
    policy_id: str
    seed: int
    budget_id: str
    pre_fix_base_sha40: str
    model_checkpoint_sha40: str
    task_spec_sha256: str
    public_candidate_archive_sha256: str
    common_opportunity_catalog_sha256: str
    tool_access_sha256: str
    environment_image_sha256: str
    resource_cap: ResourceVector
    stage: str = _STAGE

    def __post_init__(self):
        for key in ("task_id", "lineage_group", "model_id", "policy_id",
                    "budget_id"):
            value = getattr(self, key)
            if type(value) is not str or not value.strip() or len(value) > 256:
                raise ValueError("bounded nonempty assigned identity required")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("assigned seed must be nonnegative integer")
        for key in ("pre_fix_base_sha40", "model_checkpoint_sha40"):
            _check_digest(getattr(self, key), sha40=True)
        for key in ("task_spec_sha256", "public_candidate_archive_sha256",
                    "common_opportunity_catalog_sha256", "tool_access_sha256",
                    "environment_image_sha256"):
            _check_digest(getattr(self, key))
        if not isinstance(self.resource_cap, ResourceVector) or self.resource_cap.is_free():
            raise ValueError("assigned five-vector budget must be positive")
        if self.stage != _STAGE:
            raise ValueError("assignment does not certify real execution")


@dataclass(frozen=True)
class ShadowParityAudit:
    status: str
    expected_assignments: int
    verified_shadow_assignments: int
    matrix_pairs: int
    policies_per_pair: int
    declared_assignment_digest: str
    approved_real_tasks: int = 0
    verified_model_executions: int = 0
    authenticated_shared_draws: bool = False
    independent_oracle_results: int = 0


def audit_shadow_assignment_parity(
    study: FrozenStudy,
    assignments: tuple[AssignedOpportunity, ...],
) -> ShadowParityAudit:
    """Fail on missing arms or any policy-specific opportunity/source mismatch.

    Equal nominal opportunity hashes DO NOT prove equal actual candidate
    samples. Independent replay and runner attestations remain mandatory.
    """
    if not isinstance(study, FrozenStudy) or type(assignments) is not tuple:
        raise ValueError("frozen study and immutable assignment tuple required")
    if study.expected_runs > 250000:
        raise ValueError("unbounded assignment matrix")
    if len(assignments) != study.expected_runs:
        raise ValueError("incomplete or duplicated eight-policy assignment matrix")
    expected = set(product(
        (x for x, _ in study.task_lineages), study.model_ids, study.seeds,
        (name for name, _ in study.budgets), study.policies))
    groups = dict(study.task_lineages)
    caps = dict(study.budgets)
    seen = set()
    by_pair = {}
    bases = {}
    revisions = {}
    specifications = {}
    environments = {}
    tools = {}
    for a in assignments:
        if not isinstance(a, AssignedOpportunity):
            raise TypeError("typed assigned opportunities required")
        key = (a.task_id, a.model_id, a.seed, a.budget_id, a.policy_id)
        if key not in expected or key in seen:
            raise ValueError("unregistered or duplicate policy assignment")
        seen.add(key)
        if a.lineage_group != groups[a.task_id] or a.resource_cap != caps[a.budget_id]:
            raise ValueError("lineage or hard five-budget assignment mismatch")
        for registry, registry_key, value, label in (
            (bases, a.task_id, a.pre_fix_base_sha40, "pre-fix source base"),
            (specifications, a.task_id, a.task_spec_sha256, "visible task spec"),
            (revisions, a.model_id, a.model_checkpoint_sha40, "model checkpoint"),
            (environments, a.model_id, a.environment_image_sha256, "environment"),
            (tools, a.task_id, a.tool_access_sha256, "tool availability"),
        ):
            if registry_key in registry and registry[registry_key] != value:
                raise ValueError("policy matching drift in " + label)
            registry[registry_key] = value
        pair = key[:-1]
        public = (a.task_spec_sha256, a.public_candidate_archive_sha256,
                  a.common_opportunity_catalog_sha256, a.tool_access_sha256,
                  a.environment_image_sha256, a.resource_cap)
        if pair in by_pair and by_pair[pair] != public:
            raise ValueError("assigned policies have unequal public opportunities")
        by_pair[pair] = public
    if seen != expected:
        raise ValueError("incomplete assigned policy coverage")

    # Digest is reproducible but does not prove the asserted hashes/rights.
    rows = [{
        "task": a.task_id, "lineage": a.lineage_group, "model": a.model_id,
        "seed": a.seed, "budget": a.budget_id, "policy": a.policy_id,
        "base": a.pre_fix_base_sha40, "checkpoint": a.model_checkpoint_sha40,
        "spec": a.task_spec_sha256,
        "archive": a.public_candidate_archive_sha256,
        "opportunities": a.common_opportunity_catalog_sha256,
        "tools": a.tool_access_sha256, "environment": a.environment_image_sha256,
        "cap": {f: getattr(a.resource_cap, f) for f in RESOURCE_FIELDS},
    } for a in sorted(assignments, key=lambda x:
                       (x.task_id,x.model_id,x.seed,x.budget_id,x.policy_id))]
    digest = sha256(json.dumps(rows,sort_keys=True,
                               separators=(",",":")).encode()).hexdigest()
    return ShadowParityAudit(
        status="SHADOW_PARITY_VALIDATED_NOT_EXECUTED",
        expected_assignments=len(expected),
        verified_shadow_assignments=len(assignments),
        matrix_pairs=len(by_pair),
        policies_per_pair=len(study.policies),
        declared_assignment_digest=digest,
    )
