"""Partial-identification bounds for paired software-agent experiments.

A *measured* terminal timeout/safety block that releases no patch has
success=0 for full-task success; infrastructure failure can be genuinely
unobserved and is conservatively [0,1]. These are deterministic worst/best
bounds, NOT confidence intervals or a causal identification theorem.

The checker first validates the complete randomized task/model/seed/budget/
policy assignment and gold/patch matching with experiment_contract.py.
"""
from dataclasses import dataclass

from .experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix,
)


@dataclass(frozen=True)
class BoundedPairedEffect:
    assigned_pairs: int
    known_pair_differences: int
    partially_observed_pairs: int
    infrastructure_failure_cells: int
    timeouts_as_nonrelease_failures: int
    safety_blocks_as_nonrelease_failures: int
    lower_effect: float
    upper_effect: float
    interval_kind: str = "worst_best_case_partial_identification_not_confidence_interval"

    @property
    def point_identified(self):
        return self.lower_effect == self.upper_effect


def paired_effect_attrition_bounds(
    study: FrozenStudy,
    receipts: tuple[PolicyRunReceipt, ...],
    verdicts: tuple[EvaluatorVerdict, ...],
    treatment_policy: str,
    control_policy: str,
) -> BoundedPairedEffect:
    """Task-level success difference with completely unknown infra failures.

    No policy can silently relabel its own timeout or safety block as
    abstention: all original status fields are retained and counted.
    Release correctness requires a verified evaluator verdict. Comparing
    unavailable policy names, unpaired runs or falsified hashes fails.
    """
    if treatment_policy == control_policy or any(
        p not in study.policies for p in (treatment_policy, control_policy)
    ):
        raise ValueError("distinct preregistered treatment and comparator required")
    audit_confirmatory_run_matrix(
        study, receipts, verdicts, require_complete=False)
    indexed = {r.key: r for r in receipts}
    evaluator = {v.key: v.oracle_passed for v in verdicts}
    lows, highs = [], []
    partial = infra = timeout = blocked = 0
    for task_id, _ in study.task_lineages:
        for model in study.model_ids:
            for seed in study.seeds:
                for budget_id, _ in study.budgets:
                    suffix = (task_id, model, seed, budget_id)
                    a = indexed[suffix + (treatment_policy,)]
                    b = indexed[suffix + (control_policy,)]
                    def interval(r):
                        if r.termination == "release":
                            score = int(evaluator[r.key])
                            return score, score
                        if r.termination == "infrastructure_failure":
                            return 0, 1
                        # Abstain, timeout or safety stop released no patch;
                        # task-level verified success is zero.
                        return 0, 0
                    low_a, high_a = interval(a)
                    low_b, high_b = interval(b)
                    lows.append(low_a - high_b)
                    highs.append(high_a - low_b)
                    partial += int(low_a != high_a or low_b != high_b)
                    for r in (a, b):
                        infra += int(r.termination == "infrastructure_failure")
                        timeout += int(r.termination == "timeout")
                        blocked += int(r.termination == "safety_block")
    n = len(lows)
    if n == 0:
        raise ValueError("no preregistered paired assignments")
    return BoundedPairedEffect(
        assigned_pairs=n,
        known_pair_differences=n-partial,
        partially_observed_pairs=partial,
        infrastructure_failure_cells=infra,
        timeouts_as_nonrelease_failures=timeout,
        safety_blocks_as_nonrelease_failures=blocked,
        lower_effect=sum(lows)/n,
        upper_effect=sum(highs)/n,
    )
