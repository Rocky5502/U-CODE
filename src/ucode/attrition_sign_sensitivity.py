"""Postterminal missingness-sign sensitivity for a paired U-CODE evaluation.

ALL outputs are evaluator-side STRUCTURAL diagnostics from caller-supplied
records. Neither a plausible evaluator digest nor this arithmetic proves an
independently qualified oracle, trustworthy metering, or a real experiment.
No code generation, model inference, external repository execution, network
calls, file accesses or policy decisions occur here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experiment_contract import EvaluatorVerdict, FrozenStudy, PolicyRunReceipt
from .frozen_oracle_contract import FrozenOracleManifest
from .postterminal_accounting import postterminal_contrast


@dataclass(frozen=True)
class AttritionSignSensitivity:
    """Sharp binary-outcome missingness envelope; not a confidence interval."""

    treatment_policy: str
    control_policy: str
    assigned_matched_pairs: int
    treatment_infrastructure_missing: int
    control_infrastructure_missing: int
    total_unknown_binary_outcomes: int
    treatment_known_verified_successes: int
    control_known_verified_successes: int
    known_outcome_difference_numerator: int
    lower_difference_numerator: int
    upper_difference_numerator: int
    lower_effect: float
    upper_effect: float
    interval_width: float
    attainable_effect_signs: tuple[str, ...]
    sign_robust_to_all_binary_completions: bool
    point_identified_under_binary_missingness: bool
    suppressed_bootstrap_despite_identified_itt: bool
    treatment_observed_wrong_release_risk: float | None
    control_observed_wrong_release_risk: float | None
    treatment_potential_wrong_release_risk_bounds: tuple[float, float] | None
    control_potential_wrong_release_risk_bounds: tuple[float, float] | None
    named_lineages_independently_authenticated: bool = False
    oracle_independently_authenticated: bool = False
    real_experiment_proven: bool = False
    stage: str = "POSTTERMINAL_SHARP_BINARY_ATTRITION_DIAGNOSTIC_NOT_A_REAL_RESULT"


def audit_attrition_sign_sensitivity(
    study: FrozenStudy,
    receipts: tuple[PolicyRunReceipt, ...],
    verdicts: tuple[EvaluatorVerdict, ...],
    treatment_policy: str,
    control_policy: str,
    *,
    frozen_oracles: FrozenOracleManifest | None = None,
) -> AttritionSignSensitivity:
    """Explain treatment-minus-control bounds without dropping assignments.

    Known releases have binary evaluator verdicts, while abstentions,
    timeouts and safety stops produce zero verified full-task success.
    Every infrastructure-failure cell is treated as a separate *unknown*
    binary outcome between zero and one. No missing-at-random assumption.

    With N matched assignments, verified successes s_t and s_c, and unknown
    cells u_t and u_c, the sharp arithmetic endpoints are

        L_num = s_t - s_c - u_c
        U_num = s_t - s_c + u_t

    and L=L_num/N, U=U_num/N. Every integer total between the endpoints is
    attainable under *unrestricted* binary completions; therefore reported
    sign sets are exact for this specified missingness model. These bounds
    make no inference about the true missing values or independent evidence.
    """
    # Reuse the canonical strict matrix, role-separated verdict, consistent
    # task oracle, patched artifact and all-five-budget validations. This
    # step does NOT establish external receipt or source authenticity.
    audit = postterminal_contrast(
        study, receipts, verdicts, treatment_policy, control_policy,
        bootstrap_samples=0, frozen_oracles=frozen_oracles,
    )
    n = audit.assigned_pairs
    if type(n) is not int or n <= 0:
        raise AssertionError("nonempty matched assigned denominator required")
    t, c = audit.treatment, audit.control
    u_t, u_c = t.infrastructure_failures, c.infrastructure_failures
    s_t, s_c = t.verified_successes, c.verified_successes
    lo_num = s_t - s_c - u_c
    hi_num = s_t - s_c + u_t
    bounds = audit.paired_success_bounds
    if (bounds.assigned_pairs != n or t.assigned != n or c.assigned != n
            or bounds.infrastructure_failure_cells != u_t + u_c
            or bounds.known_pair_differences + bounds.partially_observed_pairs != n
            or bounds.lower_effect != lo_num / n
            or bounds.upper_effect != hi_num / n
            or not -n <= lo_num <= hi_num <= n):
        raise AssertionError("missingness accounting/denominator drift across modules")
    # Category partition invariants must remain explicit, even if a future
    # refactor modifies one arm's accounting.
    for arm in (t, c):
        if (arm.releases_with_verdict + arm.abstentions + arm.timeouts
                + arm.safety_blocks + arm.infrastructure_failures != n
                or arm.known_wrong_releases + arm.verified_successes
                != arm.releases_with_verdict):
            raise AssertionError("terminal denominator/category partition drift")
    signs = tuple(label for label, possible in (
        ("NEGATIVE", lo_num < 0),
        ("ZERO", lo_num <= 0 <= hi_num),
        ("POSITIVE", hi_num > 0),
    ) if possible)
    if not signs:
        raise AssertionError("at least one outcome sign must be attainable")
    identified = lo_num == hi_num
    return AttritionSignSensitivity(
        treatment_policy=treatment_policy,
        control_policy=control_policy,
        assigned_matched_pairs=n,
        treatment_infrastructure_missing=u_t,
        control_infrastructure_missing=u_c,
        total_unknown_binary_outcomes=u_t + u_c,
        treatment_known_verified_successes=s_t,
        control_known_verified_successes=s_c,
        known_outcome_difference_numerator=s_t - s_c,
        lower_difference_numerator=lo_num,
        upper_difference_numerator=hi_num,
        lower_effect=lo_num / n,
        upper_effect=hi_num / n,
        interval_width=(u_t + u_c) / n,
        attainable_effect_signs=signs,
        sign_robust_to_all_binary_completions=len(signs) == 1,
        point_identified_under_binary_missingness=identified,
        suppressed_bootstrap_despite_identified_itt=(
            identified and audit.paired_complete_case_estimate is None
        ),
        treatment_observed_wrong_release_risk=t.observed_wrong_release_risk,
        control_observed_wrong_release_risk=c.observed_wrong_release_risk,
        treatment_potential_wrong_release_risk_bounds=t.wrong_release_risk_bounds,
        control_potential_wrong_release_risk_bounds=c.wrong_release_risk_bounds,
    )
