"""Frozen, evaluator-only, paired SE experiment auditing.

A preexecution policy receipt does not contain gold labels. Independent
evaluator verdicts are joined ONLY after the policies finish. This module
does not perform inference, clone repository code, or certify the sandbox.
No study data are currently available; all first-party tests use SYNTHETIC
fixtures, not measured U-CODE performance.
"""
from dataclasses import dataclass
from itertools import product
from math import isfinite
import re

from .evaluation import (
    EvaluationOutcome, PolicyMeasures, PairedDifference,
    measure_policy, paired_verified_success,
)
from .vector_policy import RESOURCE_FIELDS, ResourceVector

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT40 = re.compile(r"^[0-9a-f]{40}$")
TERMINAL_ACTIONS = {"release", "abstain"}
NONTERMINAL_FAILURES = {"timeout", "infrastructure_failure", "safety_block"}


def _nonblank(value):
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True)
class FrozenStudy:
    """Experiment matrix; models, budgets, tasks and groups must be frozen."""
    task_lineages: tuple[tuple[str, str], ...]
    model_ids: tuple[str, ...]
    policies: tuple[str, ...]
    seeds: tuple[int, ...]
    budgets: tuple[tuple[str, ResourceVector], ...]

    def __post_init__(self):
        arrays = (self.task_lineages, self.model_ids, self.policies,
                  self.seeds, self.budgets)
        if not all(isinstance(x, tuple) and bool(x) for x in arrays):
            raise ValueError("all confirmatory factors must be nonempty frozen tuples")
        tasks = [t for t, g in self.task_lineages]
        groups = [g for t, g in self.task_lineages]
        if not all(_nonblank(x) for x in tasks + groups):
            raise ValueError("task and lineage labels must be nonblank")
        if len(set(tasks)) != len(tasks):
            raise ValueError("duplicate task identity")
        for seq, name in ((self.model_ids, "model"),
                          (self.policies, "policy")):
            if any(not _nonblank(x) for x in seq) or len(set(seq)) != len(seq):
                raise ValueError("invalid/duplicate " + name)
        if any(type(n) is not int or n < 0 for n in self.seeds):
            raise ValueError("seeds must be nonnegative integers")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("duplicate seed")
        budget_keys = [b for b, _ in self.budgets]
        if any(not _nonblank(x) for x in budget_keys):
            raise ValueError("empty budget label")
        if len(set(budget_keys)) != len(budget_keys):
            raise ValueError("duplicate budget label")
        for _, budget in self.budgets:
            if not isinstance(budget, ResourceVector) or budget.is_free():
                raise ValueError("budget must be a nonzero resource vector")

    @property
    def expected_runs(self) -> int:
        return (len(self.task_lineages)*len(self.model_ids)
                *len(self.policies)*len(self.seeds)*len(self.budgets))


@dataclass(frozen=True)
class PolicyRunReceipt:
    """Public run trace; forbidden to contain any oracle correctness label."""
    task_id: str
    lineage_group: str
    model_id: str
    policy: str
    seed: int
    budget_id: str
    pre_fix_base_sha: str
    consumed: ResourceVector
    termination: str
    patch_sha256: str | None
    visible_policy_log_sha256: str
    actual_costs_measured: bool = True

    def __post_init__(self):
        if any(not _nonblank(v) for v in (self.task_id, self.lineage_group,
                                          self.model_id, self.policy,
                                          self.budget_id)):
            raise ValueError("run identifying fields required")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("nonnegative integer seed required")
        if not isinstance(self.pre_fix_base_sha, str) or not GIT40.fullmatch(self.pre_fix_base_sha):
            raise ValueError("immutable original pre-fix SHA40 required")
        if not isinstance(self.consumed, ResourceVector):
            raise ValueError("measured five-component cost vector required")
        if self.termination not in TERMINAL_ACTIONS | NONTERMINAL_FAILURES:
            raise ValueError("termination must distinguish release, abstain and failures")
        if self.termination == "release":
            if not isinstance(self.patch_sha256, str) or not SHA256.fullmatch(self.patch_sha256):
                raise ValueError("released patch must have SHA256 content fingerprint")
        elif self.patch_sha256 is not None:
            raise ValueError("abstain/failure must not contain released patch fingerprint")
        if not isinstance(self.visible_policy_log_sha256, str) or not SHA256.fullmatch(
                self.visible_policy_log_sha256):
            raise ValueError("visible policy log SHA256 required")
        if type(self.actual_costs_measured) is not bool or not self.actual_costs_measured:
            raise ValueError("forecasted/assumed costs cannot stand in as measured costs")

    @property
    def key(self):
        return (self.task_id, self.model_id, self.seed,
                self.budget_id, self.policy)


@dataclass(frozen=True)
class EvaluatorVerdict:
    """Evaluator-only record; must not appear in agent-visible protocol."""
    task_id: str
    model_id: str
    policy: str
    seed: int
    budget_id: str
    patch_sha256: str
    oracle_artifact_sha256: str
    oracle_passed: bool
    evaluator_log_sha256: str

    def __post_init__(self):
        if any(not _nonblank(x) for x in
               (self.task_id, self.model_id, self.policy, self.budget_id)):
            raise ValueError("verdict identifiers required")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("verdict seed must be nonnegative integer")
        for name in ("patch_sha256", "oracle_artifact_sha256",
                     "evaluator_log_sha256"):
            val = getattr(self, name)
            if not isinstance(val, str) or not SHA256.fullmatch(val):
                raise ValueError(name + " must be a SHA256 digest")
        if type(self.oracle_passed) is not bool:
            raise ValueError("independent oracle label must be boolean")

    @property
    def key(self):
        return (self.task_id, self.model_id, self.seed,
                self.budget_id, self.policy)


@dataclass(frozen=True)
class CompleteStudyAudit:
    expected_runs: int
    observed_runs: int
    complete_terminations: int
    incomplete_terminations: int
    by_failure_reason: tuple[tuple[str, int], ...]
    consumed_by_policy: tuple[tuple[str, ResourceVector], ...]
    verified_oracle_receipts: int
    outcomes: tuple[EvaluationOutcome, ...]


def audit_confirmatory_run_matrix(
    study: FrozenStudy,
    receipts: tuple[PolicyRunReceipt, ...],
    verdicts: tuple[EvaluatorVerdict, ...],
    *,
    require_complete: bool = True,
) -> CompleteStudyAudit:
    """Reject silent pair attrition, budget abuse and gold/patch mismatches.

    For incomplete runs, return attrition only by default; no outcome object
    is generated. Formal comparisons require require_complete=True.
    Even a valid matrix is NOT proof the oracle is hidden/independent; runner
    and reviewer attestations must be separately verified.
    """
    if not isinstance(study, FrozenStudy):
        raise TypeError("frozen study required")
    if not isinstance(receipts, tuple) or not isinstance(verdicts, tuple):
        raise ValueError("immutable receipt/verdict collections required")
    if study.expected_runs > 250000:
        raise ValueError("experiment matrix exceeds bounded audit capacity")
    expected = set(product(
        (x for x, _ in study.task_lineages),
        study.model_ids, study.seeds,
        (b for b, _ in study.budgets), study.policies,
    ))
    if len(receipts) != len(expected) or len({r.key for r in receipts}) != len(receipts):
        raise ValueError("incomplete or duplicated assigned policy run matrix")
    if set(r.key for r in receipts) != expected:
        raise ValueError("wrong models, policies, tasks, seeds or budget IDs")
    groups = dict(study.task_lineages)
    caps = dict(study.budgets)
    lineages_seen = {}
    aggregated = {p: {f: 0 for f in RESOURCE_FIELDS} for p in study.policies}
    failures = {n: 0 for n in sorted(NONTERMINAL_FAILURES)}
    release_map = {}
    for r in receipts:
        if not isinstance(r, PolicyRunReceipt):
            raise ValueError("receipt object must be typed")
        if r.lineage_group != groups[r.task_id]:
            raise ValueError("policy trace uses wrong repository/fork lineage")
        recorded = lineages_seen.setdefault(r.task_id, r.lineage_group)
        if recorded != r.lineage_group:
            raise ValueError("lineage for one task shifted between policies")
        if not caps[r.budget_id].affordable(r.consumed):
            raise ValueError("policy consumed more than assigned FIVE-resource cap")
        for field in RESOURCE_FIELDS:
            aggregated[r.policy][field] += getattr(r.consumed, field)
        if r.termination in NONTERMINAL_FAILURES:
            failures[r.termination] += 1
        if r.termination == "release":
            release_map[r.key] = r
    indexes = {}
    for v in verdicts:
        if not isinstance(v, EvaluatorVerdict):
            raise ValueError("verdict must be typed")
        if v.key in indexes:
            raise ValueError("duplicate evaluator verdict")
        if v.key not in release_map:
            raise ValueError("verdict for abstained, failed or unassigned patch")
        if v.patch_sha256 != release_map[v.key].patch_sha256:
            raise ValueError("evaluator received a patch different from released artifact")
        indexes[v.key] = v
    if set(indexes) != set(release_map):
        raise ValueError("released patch lacks independently recorded oracle verdict")
    failure_n = sum(failures.values())
    if failure_n and require_complete:
        raise ValueError("incomplete/time-out/safety-stop runs require explicit attrition report before paired inference")
    outcomes = []
    if not failure_n:
        for r in receipts:
            v = indexes.get(r.key)
            outcomes.append(EvaluationOutcome(
                task_id=r.task_id, lineage_group=r.lineage_group,
                model_id=r.model_id, seed=r.seed,
                budget_id=r.budget_id, policy=r.policy,
                released=r.termination == "release",
                oracle_passed=(v.oracle_passed if v else None),
            ))
    return CompleteStudyAudit(
        expected_runs=len(expected), observed_runs=len(receipts),
        complete_terminations=len(receipts)-failure_n,
        incomplete_terminations=failure_n,
        by_failure_reason=tuple(sorted(failures.items())),
        consumed_by_policy=tuple(
            (p, ResourceVector(**aggregated[p])) for p in study.policies
        ),
        verified_oracle_receipts=len(indexes),
        outcomes=tuple(outcomes),
    )


def compare_matched_policies(
    audit: CompleteStudyAudit, treatment: str, control: str,
    *, bootstrap_samples: int = 1000, seed: int = 2026,
) -> tuple[PolicyMeasures, PolicyMeasures, PairedDifference]:
    """Descriptive paired effect + release/conditional-risk metrics, no certificate."""
    if audit.incomplete_terminations or not audit.outcomes:
        raise ValueError("cannot estimate paired effects after unhandled attrition")
    compared = [o for o in audit.outcomes if o.policy in (treatment, control)]
    a = [x for x in compared if x.policy == treatment]
    b = [x for x in compared if x.policy == control]
    if not a or not b:
        raise ValueError("policies absent from experiment")
    return (measure_policy(a), measure_policy(b),
            paired_verified_success(compared, treatment, control,
                                    bootstrap_samples, seed))
