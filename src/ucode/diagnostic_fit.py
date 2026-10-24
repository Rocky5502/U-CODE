"""Leakage-aware, TRAIN-ONLY binary diagnostic likelihood estimation.

This module estimates observation likelihoods P(+|acceptable) and
P(-|unacceptable) for the *same* model and action on independently
labeled training tasks. It does not fit a calibrated patch-success prior,
make a risk certificate, run repository code or use evaluation labels.

Group partitions are explicit and disjoint; fitting fails closed if a
validation/evaluation record is accidentally mixed into training.
"""
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from typing import Sequence

from .vector_policy import DIAGNOSTICS, DiagnosticForecast, ResourceVector


@dataclass(frozen=True)
class GroupPartitions:
    train: frozenset[str]
    validation: frozenset[str]
    evaluation: frozenset[str]

    def __post_init__(self) -> None:
        groups = (self.train, self.validation, self.evaluation)
        if any(not g for g in groups):
            raise ValueError("train, validation and evaluation group sets must be nonempty")
        if any(not isinstance(x, str) or not x.strip()
               for g in groups for x in g):
            raise ValueError("group identifiers must be nonempty strings")
        if any(a & b for i, a in enumerate(groups) for b in groups[i + 1:]):
            raise ValueError("train/validation/evaluation lineage groups overlap")

    def partition(self, group_id: str) -> str:
        if group_id in self.train:
            return "train"
        if group_id in self.validation:
            return "validation"
        if group_id in self.evaluation:
            return "evaluation"
        raise ValueError("group is not assigned to an immutable partition")


@dataclass(frozen=True)
class DiagnosticTrainingRecord:
    """One pre-oracle diagnostic followed by an independent training label.

    evidence_time and oracle_time must use the same monotonically comparable
    clock. Merely setting these metadata fields is not evidence of independent
    execution; separate source/oracle audit must establish that in real data.
    """
    task_id: str
    lineage_group: str
    model_id: str
    action: str
    positive_evidence: bool
    oracle_acceptable: int
    evidence_time: int
    oracle_time: int
    oracle_id: str

    def __post_init__(self) -> None:
        for name in ("task_id", "lineage_group", "model_id", "oracle_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
        if self.action not in DIAGNOSTICS:
            raise ValueError("unsupported diagnostic observation type")
        if type(self.positive_evidence) is not bool:
            raise ValueError("positive_evidence must be a boolean")
        if type(self.oracle_acceptable) is not int or self.oracle_acceptable not in (0, 1):
            raise ValueError("independent label must be binary integer 0/1")
        for name in ("evidence_time", "oracle_time"):
            t = getattr(self, name)
            if type(t) is not int or t < 0:
                raise ValueError(f"{name} must be an integer timestamp >=0")
        if self.evidence_time >= self.oracle_time:
            raise ValueError("diagnostic evidence must precede independent oracle label")


@dataclass(frozen=True)
class FrozenDiagnosticLikelihood:
    """A frozen conditional diagnostic likelihood, not calibrated success."""
    model_id: str
    action: str
    sensitivity: float
    specificity: float
    acceptable_n: int
    unacceptable_n: int
    train_group_count: int
    training_fingerprint: str

    def forecast(self, cost: ResourceVector) -> DiagnosticForecast:
        return DiagnosticForecast(self.action, self.sensitivity,
                                  self.specificity, cost)


def fit_diagnostic_likelihood(
    records: Sequence[DiagnosticTrainingRecord],
    partitions: GroupPartitions,
    model_id: str,
    action: str,
    minimum_per_class: int = 5,
    minimum_groups: int = 2,
    pseudocount: float = 1.0,
) -> FrozenDiagnosticLikelihood:
    """Estimate likelihoods only from all and exclusively training rows.

    Fit is invalid if a non-training group, duplicate task ID, wrong
    model/action or insufficient representation reaches this function. These
    restrictions prevent accidental evaluation-label tuning, but do not prove
    upstream third-party provenance or an independently sealed oracle.
    """
    if not model_id or not model_id.strip() or action not in DIAGNOSTICS:
        raise ValueError("valid specific model and diagnostic action required")
    if type(minimum_per_class) is not int or minimum_per_class < 1:
        raise ValueError("minimum_per_class must be >=1")
    if type(minimum_groups) is not int or minimum_groups < 2:
        raise ValueError("minimum_groups must be >=2")
    if not isfinite(pseudocount) or pseudocount <= 0:
        raise ValueError("pseudocount must be positive finite")
    if not records:
        raise ValueError("no diagnostic training records")

    seen: set[str] = set()
    groups: set[str] = set()
    positives = negatives = true_positive = true_negative = 0
    for r in records:
        if partitions.partition(r.lineage_group) != "train":
            raise ValueError("validation/evaluation group labels are forbidden in fitting")
        if r.model_id != model_id or r.action != action:
            raise ValueError("cross-model or cross-action training is forbidden")
        if r.task_id in seen:
            raise ValueError("duplicate task_id can cause task/label pseudoreplication")
        seen.add(r.task_id)
        groups.add(r.lineage_group)
        if r.oracle_acceptable:
            positives += 1
            true_positive += int(r.positive_evidence)
        else:
            negatives += 1
            true_negative += int(not r.positive_evidence)
    if min(positives, negatives) < minimum_per_class:
        raise ValueError("too few independently labeled positive/negative training tasks")
    if len(groups) < minimum_groups:
        raise ValueError("too few independent repository/fork lineage groups")

    # Beta(pseudocount, pseudocount) posterior means: finite in sparse strata.
    sensitivity = (true_positive + pseudocount) / (positives + 2 * pseudocount)
    specificity = (true_negative + pseudocount) / (negatives + 2 * pseudocount)
    # Hash stable row identifiers, timestamps and outcomes for immutable
    # reproducibility; a hash is not a provenance attestation or a source license.
    lines = sorted(
        f"{r.task_id}\t{r.lineage_group}\t{r.model_id}\t{r.action}\t"
        f"{int(r.positive_evidence)}\t{r.oracle_acceptable}\t"
        f"{r.evidence_time}\t{r.oracle_time}\t{r.oracle_id}"
        for r in records
    )
    fingerprint = sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
    return FrozenDiagnosticLikelihood(model_id, action, sensitivity, specificity,
                                      positives, negatives, len(groups), fingerprint)
