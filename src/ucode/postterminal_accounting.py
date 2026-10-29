"""Evaluator-side bounded accounting, postterminal ONLY (not policy input).

The caller must supply the COMPLETE frozen assignment/receipt matrix and
ALL independent verdicts for releases. Reuses the experiment-contract
checker to reject missing/duplicate assignment cells, cross-policy
checkpoint/permission changes, and patch/oracle mismatches.

Infrastructure failures have unknown success AND release outcomes; we
report sharp elementary worst/best missingness bounds, NOT confidence
intervals, causal claims, calibrated risk, or independent oracle proof.
No model or repository code is executed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .attrition_bounds import BoundedPairedEffect, paired_effect_attrition_bounds
from .evaluation import PairedDifference, paired_verified_success
from .experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix,
)
from .vector_policy import RESOURCE_FIELDS


@dataclass(frozen=True)
class ArmPostterminalMetrics:
    policy: str
    assigned: int
    releases_with_verdict: int
    verified_successes: int
    known_wrong_releases: int
    abstentions: int
    timeouts: int
    safety_blocks: int
    infrastructure_failures: int
    full_task_success_bounds: tuple[float, float]
    release_coverage_bounds: tuple[float, float]
    observed_wrong_release_risk: float | None
    wrong_release_risk_bounds: tuple[float, float] | None
    mean_reported_cost_per_assignment: tuple[tuple[str, float], ...]
    # Missingness intervals and population-release risk are different objects.
    interval_kind: str = "WORST_BEST_MISSING_INFRA_NOT_CONFIDENCE_INTERVAL"
    authenticated_meter: bool = False
    independently_authenticated_oracle: bool = False


@dataclass(frozen=True)
class PostterminalContrast:
    treatment: ArmPostterminalMetrics
    control: ArmPostterminalMetrics
    assigned_pairs: int
    paired_success_bounds: BoundedPairedEffect
    paired_complete_case_estimate: PairedDifference | None
    stage: str = "STRUCTURAL_EVALUATOR_SIDE_ACCOUNTING_NOT_VERIFIED_REAL_TRIAL"
    real_trial_approved: bool = False


def _arm(
    name: str, rows: Sequence[PolicyRunReceipt],
    verdicts: dict[tuple, EvaluatorVerdict],
) -> ArmPostterminalMetrics:
    n=len(rows)
    if n==0:
        raise ValueError("no assigned policy cells")
    status={x:0 for x in (
        "release", "abstain", "timeout", "safety_block",
        "infrastructure_failure")}
    consumed={f:0.0 for f in RESOURCE_FIELDS}
    successes=wrong=0
    for r in rows:
        status[r.termination]+=1
        for k in RESOURCE_FIELDS:
            consumed[k]+=getattr(r.consumed,k)
        if r.termination=="release":
            v=verdicts[r.key]
            successes+=int(v.oracle_passed is True)
            wrong+=int(v.oracle_passed is False)
    released=status["release"]
    unknown=status["infrastructure_failure"]
    # Known negative terminations (incl. timeout) are task failures, never
    # mysteriously removed from the intent-to-treat population.
    success=(successes/n, (successes+unknown)/n)
    coverage=(released/n, (released+unknown)/n)
    observed_risk=wrong/released if released else None
    # All missing infra outcomes might release a passing or failing patch.
    # The denominator for these bounds includes potential unknown releases;
    # when there are none and no observed releases, risk is UNDEFINED.
    risk=(
        (wrong/(released+unknown),
         (wrong+unknown)/(released+unknown))
        if released+unknown else None
    )
    if successes+wrong!=released or sum(status.values())!=n:
        raise AssertionError("postterminal category counts must partition assignments")
    return ArmPostterminalMetrics(
        policy=name,assigned=n,releases_with_verdict=released,
        verified_successes=successes,known_wrong_releases=wrong,
        abstentions=status["abstain"],timeouts=status["timeout"],
        safety_blocks=status["safety_block"],
        infrastructure_failures=unknown,
        full_task_success_bounds=success,
        release_coverage_bounds=coverage,
        observed_wrong_release_risk=observed_risk,
        wrong_release_risk_bounds=risk,
        mean_reported_cost_per_assignment=tuple(
            (k,consumed[k]/n) for k in RESOURCE_FIELDS
        ),
    )


def postterminal_contrast(
    study: FrozenStudy,
    receipts: tuple[PolicyRunReceipt, ...],
    verdicts: tuple[EvaluatorVerdict, ...],
    treatment: str,
    control: str,
    *,
    bootstrap_samples: int = 1000,
    seed: int = 2026,
) -> PostterminalContrast:
    """Return only structurally grounded metrics after terminal receipt audit.

    A successful call validates the local submitted records, NOT their
    independent authenticity. Do not use for synthetic data in paper Results.
    Bootstrap summary is suppressed if any arm has incomplete outcome.
    """
    if not isinstance(study,FrozenStudy):
        raise TypeError("frozen study required")
    if (type(treatment) is not str or type(control) is not str
            or treatment==control or treatment not in study.policies
            or control not in study.policies):
        raise ValueError("distinct preregistered treatment/control required")
    if (type(bootstrap_samples) is not int or bootstrap_samples<0
            or type(seed) is not int):
        raise ValueError("nonnegative bootstrap size and integer seed required")
    # Require all assignments, all released-patch verdicts and exact identity
    # alignment even when infra failure is unobserved.
    audit=audit_confirmatory_run_matrix(
        study,receipts,verdicts,require_complete=False)
    lookup={v.key:v for v in verdicts}
    a=_arm(treatment,tuple(r for r in receipts if r.policy==treatment),lookup)
    b=_arm(control,tuple(r for r in receipts if r.policy==control),lookup)
    if a.assigned!=b.assigned:
        raise ValueError("different treatment and control assigned populations")
    bounded=paired_effect_attrition_bounds(
        study,receipts,verdicts,treatment,control)
    if bounded.assigned_pairs!=a.assigned:
        raise AssertionError("paired assignment denominator drift")
    point=None
    if audit.incomplete_terminations==0:
        compared=tuple(o for o in audit.outcomes if o.policy in (treatment,control))
        point=paired_verified_success(
            compared,treatment,control,bootstrap_samples=bootstrap_samples,
            seed=seed)
        if not (bounded.lower_effect-1e-12<=point.effect_success_difference
                <=bounded.upper_effect+1e-12):
            raise AssertionError("paired point estimate outside missingness bounds")
    return PostterminalContrast(
        treatment=a,control=b,assigned_pairs=bounded.assigned_pairs,
        paired_success_bounds=bounded,paired_complete_case_estimate=point)
