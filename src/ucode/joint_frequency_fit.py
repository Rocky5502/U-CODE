"""Leakage-aware, lineage-balanced TRAIN-ONLY categorical joint R/S/V baseline.

Eight outcomes (R high, S high, candidate VALID), from prospectively fixed
PUBLIC context buckets. Group-balanced smoothed frequencies are a minimal
conditional joint-model control. This is NOT a strong feature-trained model,
a security-certifying classifier, or a fitted real-project model.

IMPORTANT: Training/validation record *labels* are evaluator-/trainer-side
data. Never persist records or the hidden evaluation labels in public policy
metadata. Group IDs, pre-outcome times and label provenance supplied by a
caller are structural CLAIMS, not independent verification/attestation.
One fixed candidate per task is required to avoid pseudoreplication.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite, log
from typing import Sequence

from .dependence_robust_acquisition import (
    RobustParetoProposal, TwoPointOutcome,
)
from .diagnostic_fit import GroupPartitions
from .vector_policy import ResourceVector

_ACTIONS = frozenset(("generate","repair"))
_ATOMS = tuple((r,s,v) for r in (0,1) for s in (0,1) for v in (0,1))
_STATUS = "TRAIN_ONLY_SMOOTHED_CATEGORICAL_JOINT_NOT_ATTESTED_NOT_CALIBRATED"
_VALIDATION_STATUS = "HELDOUT_VALIDATION_DESCRIPTIVE_ONLY_NOT_TEST_EVALUATION"


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _probability(value: float) -> bool:
    return type(value) in (int, float) and isfinite(value) and 0 <= value <= 1


def _valid_sha256(value: str) -> bool:
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _label_pair(name: str, value: int) -> None:
    if type(value) is not int or value not in (0,1):
        raise ValueError(name + " must be a binary integer 0/1, not bool or missing")


@dataclass(frozen=True)
class JointOutcomeLabel:
    """One independently adjudicable *training or validation* observation.

    R/S labels must remain DEFINED and independently assessed even when
    candidate_valid=0, under a frozen protocol. No imputation or post-fix
    PR-authored test is accepted as a substitute for such assessment.
    """
    task_id: str
    lineage_group: str
    proposal_id: str
    model_id: str
    model_checkpoint_sha256: str
    action: str
    public_context_bucket: str
    preoutcome_snapshot_sha256: str
    preoutcome_time: int
    label_time: int
    labeling_protocol_id: str
    reliability_high: int
    safety_high: int
    candidate_valid: int
    training_label_ref: str

    def __post_init__(self):
        for key in ("task_id","lineage_group","proposal_id","model_id",
                    "public_context_bucket","labeling_protocol_id",
                    "training_label_ref"):
            value = getattr(self,key)
            if type(value) is not str or not value.strip() or len(value)>256:
                raise ValueError(key + " requires bounded nonempty text")
        if self.action not in _ACTIONS:
            raise ValueError("only generate or repair candidate outcomes may be fitted")
        if not _valid_sha256(self.preoutcome_snapshot_sha256):
            raise ValueError("pre-outcome snapshot requires lower-case SHA256")
        if not _valid_sha256(self.model_checkpoint_sha256):
            raise ValueError("immutable model checkpoint requires lower-case SHA256")
        if (type(self.preoutcome_time) is not int
                or type(self.label_time) is not int
                or self.preoutcome_time<0 or self.preoutcome_time>=self.label_time):
            raise ValueError("pre-outcome public features must precede training labels")
        for field in ("reliability_high","safety_high","candidate_valid"):
            _label_pair(field,getattr(self,field))

    @property
    def atom_index(self) -> int:
        return 4*self.reliability_high + 2*self.safety_high + self.candidate_valid


@dataclass(frozen=True)
class FrozenJointFrequency:
    model_id: str
    model_checkpoint_sha256: str
    action: str
    public_context_bucket: str
    labeling_protocol_id: str
    masses: tuple[float, ...]
    training_task_count: int
    training_lineage_count: int
    smoothing_per_atom: float
    training_fingerprint_sha256: str
    training_task_hashes: tuple[str, ...]
    training_proposal_hashes: tuple[str, ...]
    training_snapshot_hashes: tuple[str, ...]
    status: str = _STATUS

    def __post_init__(self):
        if self.status != _STATUS:
            raise ValueError("this baseline cannot self-promote into an attested model")
        if not _valid_sha256(self.model_checkpoint_sha256):
            raise ValueError("frozen checkpoint requires 64-hex digest")
        if not _valid_sha256(self.training_fingerprint_sha256):
            raise ValueError("training fingerprint requires 64-hex digest")
        for hashes in (self.training_task_hashes,
                       self.training_proposal_hashes,
                       self.training_snapshot_hashes):
            if (type(hashes) is not tuple
                    or len(hashes) != self.training_task_count
                    or len(set(hashes)) != len(hashes)
                    or tuple(sorted(hashes)) != hashes
                    or any(not _valid_sha256(h) for h in hashes)):
                raise ValueError("unique sorted complete SHA256 overlap ledger required")
        if (type(self.masses) is not tuple or len(self.masses)!=8
                or any(not _probability(x) for x in self.masses)
                or abs(sum(self.masses)-1.)>1e-10):
            raise ValueError("eight valid normalized joint atom masses required")
        if self.action not in _ACTIONS:
            raise ValueError("joint training model must be candidate-producing")
        if (type(self.training_task_count) is not int
                or self.training_task_count<8
                or type(self.training_lineage_count) is not int
                or self.training_lineage_count<2):
            raise ValueError("minimum sample and lineage support required")
        if (type(self.smoothing_per_atom) not in (float,int)
                or not isfinite(self.smoothing_per_atom)
                or self.smoothing_per_atom<=0):
            raise ValueError("positive smoothing required")

    def marginal_high(self) -> tuple[float,float,float]:
        return tuple(sum(m for m,atom in zip(self.masses,_ATOMS) if atom[d])
                     for d in range(3))

    def proposal(
        self, action_id: str,
        reliability_levels: tuple[float,float],
        safety_levels: tuple[float,float],
        cost: ResourceVector,
    ) -> RobustParetoProposal:
        """Construct a candidate with SAME marginals for every comparison."""
        p,q,v=self.marginal_high()
        if (type(reliability_levels) is not tuple or len(reliability_levels)!=2
                or type(safety_levels) is not tuple or len(safety_levels)!=2):
            raise TypeError("frozen two-point support required")
        return RobustParetoProposal(
            action_id,self.action,
            TwoPointOutcome(*reliability_levels,p),
            TwoPointOutcome(*safety_levels,q),
            v,cost,
        )


@dataclass(frozen=True)
class JointValidationMetrics:
    model_id: str
    model_checkpoint_sha256: str
    action: str
    public_context_bucket: str
    validation_tasks: int
    validation_lineages: int
    categorical_eight_class_brier: float
    categorical_log_loss: float
    marginal_brier_mean: float
    marginal_absolute_calibration_error: tuple[float,float,float]
    lineage_balanced_categorical_brier: float
    lineage_balanced_categorical_log_loss: float
    lineage_balanced_marginal_brier_mean: float
    lineage_balanced_marginal_absolute_gap: tuple[float,float,float]
    status: str = _VALIDATION_STATUS


def _canonical_row(row: JointOutcomeLabel) -> str:
    return json.dumps(
        [row.task_id,row.lineage_group,row.proposal_id,row.model_id,
         row.model_checkpoint_sha256,row.action,
         row.public_context_bucket,row.preoutcome_snapshot_sha256,
         row.preoutcome_time,row.label_time,row.labeling_protocol_id,
         row.reliability_high,row.safety_high,row.candidate_valid,
         row.training_label_ref],
        ensure_ascii=False,separators=(",",":"),
    )


def _selected_rows(
    rows: Sequence[JointOutcomeLabel], partitions: GroupPartitions,
    model_id: str, checkpoint_sha256: str, action: str,
    bucket: str, protocol: str, fold: str,
    min_rows: int, min_lineages: int,
    prohibited_task_hashes: frozenset[str] = frozenset(),
    prohibited_proposal_hashes: frozenset[str] = frozenset(),
    prohibited_snapshot_hashes: frozenset[str] = frozenset(),
) -> tuple[JointOutcomeLabel,...]:
    if not isinstance(partitions,GroupPartitions):
        raise TypeError("typed and separated repository/fork groups required")
    if not _valid_sha256(checkpoint_sha256):
        raise ValueError("frozen checkpoint SHA256 identity required")
    for v in (model_id,bucket,protocol):
        if type(v) is not str or not v.strip():
            raise ValueError("model, public context and fixed label protocol are required")
    if action not in _ACTIONS:
        raise ValueError("only generate/repair fitted labels permitted")
    if type(min_rows) is not int or min_rows<1:
        raise ValueError("positive minimum number of rows required")
    if type(min_lineages) is not int or min_lineages<2:
        raise ValueError("at least two repository lineages required")
    seq=tuple(rows)
    if not seq:
        raise ValueError("empty outcome records")
    groups=set()
    tasks=set()
    proposals=set()
    snapshots=set()
    for row in seq:
        if not isinstance(row,JointOutcomeLabel):
            raise TypeError("typed joint outcome label required")
        if partitions.partition(row.lineage_group)!=fold:
            raise ValueError("validation/evaluation group labels forbidden in training or vice versa")
        if (row.model_id,row.model_checkpoint_sha256,row.action,
            row.public_context_bucket,row.labeling_protocol_id)!=(
                model_id,checkpoint_sha256,action,bucket,protocol):
            raise ValueError("mixing models/checkpoints, actions, public contexts or labeling protocol is forbidden")
        if row.task_id in tasks:
            raise ValueError("one prospectively fixed candidate per task; duplicate task")
        if row.proposal_id in proposals:
            raise ValueError("duplicate candidate proposal across distinct tasks")
        if row.preoutcome_snapshot_sha256 in snapshots:
            raise ValueError("duplicate candidate public snapshot across distinct tasks")
        tasks.add(row.task_id)
        proposals.add(row.proposal_id)
        snapshots.add(row.preoutcome_snapshot_sha256)
        groups.add(row.lineage_group)
        if _digest(row.task_id) in prohibited_task_hashes:
            raise ValueError("train/validation task overlap, even under renamed lineage")
        if _digest(row.proposal_id) in prohibited_proposal_hashes:
            raise ValueError("train/validation candidate overlap under different task ID")
        if row.preoutcome_snapshot_sha256 in prohibited_snapshot_hashes:
            raise ValueError("train/validation public snapshot overlap across task IDs")
    if len(seq)<min_rows or len(groups)<min_lineages:
        raise ValueError("insufficient per-context task or repository lineage support")
    return seq


def fit_training_joint_frequency(
    rows: Sequence[JointOutcomeLabel], partitions: GroupPartitions,
    model_id: str, action: str, public_context_bucket: str,
    labeling_protocol_id: str, *, model_checkpoint_sha256: str,
    smoothing_per_atom: float=.25,
    minimum_training_tasks: int=8,
    minimum_lineages: int=2,
    minimum_class_lineages: int=2,
) -> FrozenJointFrequency:
    """Fit a group-balanced joint 8-cell categorical baseline on TRAIN ONLY.

    The distribution is smoothed across groups. Each independent *declared*
    lineage has equal total weight, instead of giving the largest repository
    unlimited influence. Model/context/labeling protocol pooling is refused.
    This is a simple frequency control, NOT a feature-rich predictor.
    """
    if (type(smoothing_per_atom) not in (int,float)
            or not isfinite(smoothing_per_atom)
            or smoothing_per_atom<=0):
        raise ValueError("positive finite categorical pseudocount required")
    if type(minimum_class_lineages) is not int or minimum_class_lineages<2:
        raise ValueError("at least two lineages supporting each marginal class")
    seq=_selected_rows(
        rows, partitions,model_id,model_checkpoint_sha256,
        action,public_context_bucket,labeling_protocol_id,
        "train",minimum_training_tasks,minimum_lineages,
    )
    grouped={}
    supports=[[set(),set()] for _ in range(3)]
    for row in seq:
        a=grouped.setdefault(row.lineage_group,[0]*8)
        a[row.atom_index]+=1
        for d,x in enumerate((row.reliability_high,row.safety_high,row.candidate_valid)):
            supports[d][x].add(row.lineage_group)
    if any(min(len(x) for x in groups)<minimum_class_lineages
           for groups in supports):
        raise ValueError("insufficient class-conditional repository lineages")
    counts=[float(smoothing_per_atom)]*8
    for group in sorted(grouped):
        cell_counts=grouped[group]
        n=sum(cell_counts)
        for i,count in enumerate(cell_counts):
            counts[i]+=count/n  # each declared source lineage contributes total one
    denominator=sum(counts)
    masses=tuple(value/denominator for value in counts)
    fingerprint=_digest(json.dumps(
        ["ucode-train-only-joint-rsv-v1",sorted(_canonical_row(r) for r in seq)],
        ensure_ascii=False,separators=(",",":"),
    ))
    return FrozenJointFrequency(
        model_id,model_checkpoint_sha256,action,public_context_bucket,
        labeling_protocol_id,masses,
        len(seq),len(grouped),float(smoothing_per_atom),fingerprint,
        tuple(sorted(_digest(r.task_id) for r in seq)),
        tuple(sorted(_digest(r.proposal_id) for r in seq)),
        tuple(sorted(r.preoutcome_snapshot_sha256 for r in seq)),
    )


def validate_frozen_joint_frequency(
    forecast: FrozenJointFrequency, rows: Sequence[JointOutcomeLabel],
    partitions: GroupPartitions, *, minimum_validation_tasks: int=4,
    minimum_validation_lineages: int=2,
) -> JointValidationMetrics:
    """Score on VALIDATION groups only; no refit and no evaluation-label access.

    A descriptive validation Brier/log score is not a calibration guarantee,
    and MUST NOT be used as an evaluation/test score. Any tuning based on
    these scores requires separate preregistration and a subsequent test fold.
    """
    if not isinstance(forecast,FrozenJointFrequency):
        raise TypeError("frozen trained joint frequency required")
    seq=_selected_rows(
        rows,partitions,forecast.model_id,forecast.model_checkpoint_sha256,
        forecast.action,forecast.public_context_bucket,
        forecast.labeling_protocol_id,
        "validation",minimum_validation_tasks,minimum_validation_lineages,
        frozenset(forecast.training_task_hashes),
        frozenset(forecast.training_proposal_hashes),
        frozenset(forecast.training_snapshot_hashes),
    )
    prob=forecast.masses
    m=forecast.marginal_high()
    n=len(seq)
    brier=sum(sum(
        (prob[j]-(1. if j==row.atom_index else 0.))**2
        for j in range(8)) for row in seq)/n
    logloss=-sum(log(prob[row.atom_index]) for row in seq)/n
    margin=sum(
        sum((m[i]-v)**2 for i,v in enumerate((
            row.reliability_high,row.safety_high,row.candidate_valid
        ))) for row in seq)/(3*n)
    fields=("reliability_high","safety_high","candidate_valid")
    observed=[sum(getattr(row,key) for row in seq)/n for key in fields]

    # Report BOTH task-weighted and equal-lineage-weighted diagnostics.
    # Training fits one total vote per lineage. A pooled validation mean
    # silently changes the estimand whenever repository sizes differ.
    by_group: dict[str,list[JointOutcomeLabel]] = {}
    for row in seq:
        by_group.setdefault(row.lineage_group,[]).append(row)
    group_brier=[]
    group_log=[]
    group_marginal=[]
    group_gaps=[]
    for lineage in sorted(by_group):
        subset=by_group[lineage]
        group_n=len(subset)
        group_brier.append(sum(
            sum((prob[j]-(1. if j==row.atom_index else 0.))**2
                for j in range(8)) for row in subset)/group_n)
        group_log.append(-sum(log(prob[row.atom_index])
                              for row in subset)/group_n)
        group_marginal.append(sum(
            sum((m[i]-getattr(row,key))**2
                for i,key in enumerate(fields))
            for row in subset)/(3*group_n))
        group_prevalence=[
            sum(getattr(row,key) for row in subset)/group_n
            for key in fields
        ]
        group_gaps.append(tuple(abs(m[i]-group_prevalence[i])
                                for i in range(3)))
    num_groups=len(by_group)
    return JointValidationMetrics(
        forecast.model_id, forecast.model_checkpoint_sha256,
        forecast.action,forecast.public_context_bucket,
        n,num_groups,brier,logloss,margin,
        tuple(abs(m[i]-observed[i]) for i in range(3)),
        sum(group_brier)/num_groups,sum(group_log)/num_groups,
        sum(group_marginal)/num_groups,
        tuple(sum(gap[i] for gap in group_gaps)/num_groups
              for i in range(3)),
    )
