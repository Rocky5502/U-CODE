"""Evaluator-only leave-one-repository-lineage-out sensitivity analysis.

All input oracle labels are supplied by the caller: this module NEVER
certifies oracle independence, source rights, pre-fix history, model weights,
task admissions, or real execution. Use only POST-terminal evaluation data.
It cannot estimate population effects from synthetic examples.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .evaluation import EvaluationOutcome, paired_verified_success


@dataclass(frozen=True)
class LineageOmission:
    """Descriptive effect when all assignments of one fork family are omitted."""

    lineage_group: str
    omitted_pairs: int
    omitted_success_delta_sum: int
    remaining_pairs: int
    effect_without_lineage: float | None
    absolute_effect_shift: float | None
    strict_sign_reversal: bool | None


@dataclass(frozen=True)
class LineageInfluenceAudit:
    """Not a significance test, confidence interval, or authenticity claim."""

    treatment_policy: str
    control_policy: str
    paired_assignments: int
    nominal_lineage_groups: int
    observed_assignment_level_effect: float
    largest_lineage_assignment_fraction: float
    leave_one_lineage_out: tuple[LineageOmission, ...]
    maximum_absolute_effect_shift: float | None
    number_of_strict_sign_reversals: int
    any_leave_one_lineage_effect_undefined: bool
    declares_independent_lineages_attested: bool = False
    certifies_real_model_experiment: bool = False


def analyze_lineage_influence(
    outcomes: Sequence[EvaluationOutcome],
    treatment_policy: str,
    control_policy: str,
) -> LineageInfluenceAudit:
    """Expose single-lineage dependence of a matched assignment-level ITT.

    For paired delta_i in {-1,0,1}, define effect = sum(delta_i)/N.
    With lineage g excluded, effect(-g) =
        (sum(delta_i) - sum(delta_i for i in g)) / (N - N_g).
    This respects all matched task/model/seed/budget assignments and omits
    ALL repeated observations of the withheld repository/fork family.

    For only one lineage, the leave-one-out denominator is zero, so it MUST
    report None (not zero). The estimate remains assignment-weighted because
    the frozen primary endpoint is per assigned task, not per repository.
    A grouping label here is caller-declared, not source authenticated.
    """
    if not isinstance(outcomes, (tuple, list)):
        raise TypeError("bounded typed outcome sequence required")
    if not outcomes or len(outcomes) > 250000:
        raise ValueError("nonempty bounded paired outcome table required")
    # Reuse the mature paired contract for identity, duplicate, type, exact
    # matching, release/abstain and lineage consistency. No bootstrap needed.
    paired = paired_verified_success(
        outcomes, treatment_policy, control_policy, bootstrap_samples=0
    )
    buckets: dict[tuple[str, str, int, str], dict[str, EvaluationOutcome]] = {}
    for outcome in outcomes:
        buckets.setdefault(outcome.key, {})[outcome.policy] = outcome

    by_lineage: dict[str, list[int]] = {}
    for key in sorted(buckets):
        records = buckets[key]
        tr = records[treatment_policy]
        ct = records[control_policy]
        by_lineage.setdefault(tr.lineage_group, []).append(
            tr.verified_success - ct.verified_success
        )
    n = paired.pairs
    total = paired.positive_discordant - paired.negative_discordant
    if len(buckets) != n or sum(map(len, by_lineage.values())) != n:
        raise RuntimeError("matched audit and lineage accounting differ")
    rows = []
    for group in sorted(by_lineage):
        deltas = by_lineage[group]
        removed = len(deltas)
        left = n - removed
        omitted_sum = sum(deltas)
        remainder_effect = (total - omitted_sum) / left if left else None
        shift = (abs(remainder_effect - paired.effect_success_difference)
                 if remainder_effect is not None else None)
        flips = ((paired.effect_success_difference * remainder_effect) < 0
                 if remainder_effect is not None else None)
        rows.append(LineageOmission(
            lineage_group=group,
            omitted_pairs=removed,
            omitted_success_delta_sum=omitted_sum,
            remaining_pairs=left,
            effect_without_lineage=remainder_effect,
            absolute_effect_shift=shift,
            strict_sign_reversal=flips,
        ))
    shifts = [row.absolute_effect_shift for row in rows
              if row.absolute_effect_shift is not None]
    return LineageInfluenceAudit(
        treatment_policy=treatment_policy,
        control_policy=control_policy,
        paired_assignments=n,
        nominal_lineage_groups=len(rows),
        observed_assignment_level_effect=paired.effect_success_difference,
        largest_lineage_assignment_fraction=max(
            len(deltas) for deltas in by_lineage.values()) / n,
        leave_one_lineage_out=tuple(rows),
        maximum_absolute_effect_shift=max(shifts) if shifts else None,
        number_of_strict_sign_reversals=sum(
            row.strict_sign_reversal is True for row in rows
        ),
        any_leave_one_lineage_effect_undefined=any(
            row.effect_without_lineage is None for row in rows
        ),
    )
