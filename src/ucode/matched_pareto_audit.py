"""S03 evaluator-only matched six-objective Pareto and exact hypervolume audit.

The SIX objectives are postterminal evaluator-CLAIMED full-task success
(maximize) and each of the FIVE reported resource costs (minimize).
This is structural bookkeeping, not an independent oracle or meter proof.
No model inference, third-party code, shell, GPU or network is executed.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix,
)
from .frozen_oracle_contract import FrozenOracleManifest
from .vector_policy import RESOURCE_FIELDS, ResourceVector

# Exact union slicing has combinatorial cost. This first-party diagnostic
# deliberately supports the original eight-policy study, not arbitrary data.
MAX_PARETO_POLICIES = 8


@dataclass(frozen=True)
class ParetoArm:
    """All quantities are declarations in submitted source-only receipts."""

    policy: str
    evaluator_claimed_success_rate: float
    total_reported_cost: ResourceVector

    def __post_init__(self) -> None:
        if type(self.policy) is not str or not self.policy.strip():
            raise ValueError("nonblank policy ID required")
        score = self.evaluator_claimed_success_rate
        if (type(score) not in (int, float)
                or not isfinite(score) or not 0 <= score <= 1):
            raise ValueError("finite claimed full-task success in [0,1] required")
        if type(self.total_reported_cost) is not ResourceVector:
            raise TypeError("five-component declared ResourceVector required")


@dataclass(frozen=True)
class ParetoBudgetAudit:
    """Descriptive fixed-cap report, NEVER an empirical performance claim."""

    model_id: str
    budget_id: str
    matched_assignments_per_policy: int
    six_objectives: tuple[str, ...]
    declared_budget_per_assignment: ResourceVector
    arms: tuple[ParetoArm, ...]
    nondominated_policies: tuple[str, ...]
    identical_tradeoff_ties: tuple[tuple[str, str], ...]
    dominated_by: tuple[tuple[str, tuple[str, ...]], ...]
    exact_normalized_hypervolume: float
    marginal_hypervolume_by_policy: tuple[tuple[str, float], ...]
    all_cost_vectors_componentwise_within_caps: bool = True
    reported_costs_independently_measured: bool = False
    hidden_oracles_independently_authenticated: bool = False
    licensed_models_and_tasks_qualified: bool = False
    real_experiment_approved: bool = False
    stage: str = "SYNTHETIC_OR_DECLARED_POSTTERMINAL_PARETO_NOT_REAL_RESULTS"


def dominates(a: ParetoArm, b: ParetoArm) -> bool:
    """Strong Pareto dominance: no worse on all six and strictly better on one."""
    if type(a) is not ParetoArm or type(b) is not ParetoArm:
        raise TypeError("typed Pareto arms required")
    return (
        a.evaluator_claimed_success_rate >= b.evaluator_claimed_success_rate
        and all(getattr(a.total_reported_cost, dim)
                <= getattr(b.total_reported_cost, dim)
                for dim in RESOURCE_FIELDS)
        and (
            a.evaluator_claimed_success_rate > b.evaluator_claimed_success_rate
            or any(getattr(a.total_reported_cost, dim)
                   < getattr(b.total_reported_cost, dim)
                   for dim in RESOURCE_FIELDS)
        )
    )


def _strict_positive_caps(cap: ResourceVector) -> None:
    if type(cap) is not ResourceVector:
        raise TypeError("typed five-dimensional reference budget required")
    if any(getattr(cap, dim) <= 0 for dim in RESOURCE_FIELDS):
        raise ValueError(
            "exact normalized hypervolume needs strictly positive "
            "caps in ALL five resource dimensions; zero cap is undefined"
        )


def _benefit_vector(
    arm: ParetoArm, cap: ResourceVector,
) -> tuple[float, ...]:
    """Six gains: claimed success; five normalized resource SAVINGS."""
    gains = [float(arm.evaluator_claimed_success_rate)]
    for dim in RESOURCE_FIELDS:
        actual = getattr(arm.total_reported_cost, dim)
        maximum = getattr(cap, dim)
        if actual > maximum:
            raise ValueError("declared resource cost exceeds FIVE-resource cap: " + dim)
        if not isfinite(actual) or not isfinite(maximum):
            raise ValueError("nonfinite resource cannot define a Pareto point")
        saving = 1.0 - (actual / maximum)
        # No arbitrary epsilon relaxation of real cap abuse.
        if not 0.0 <= saving <= 1.0:
            raise ValueError("normalized resource saving outside unit interval")
        gains.append(saving)
    return tuple(gains)


def _union_origin_boxes(boxes: tuple[tuple[float, ...], ...]) -> float:
    """Exact recursive sweep for origin-to-point axis-aligned hyperrectangles.

    The mathematical definition uses the union volume of [0,x] boxes, not
    the SUM of per-policy volumes (which double-counts overlaps). No Monte
    Carlo approximation, prediction, probability or scalarized budget.
    Float64 yields numerical rounding only; avoid claiming formal exact
    rational arithmetic for input floats.
    """
    if not boxes:
        return 0.0
    dimensions = len(boxes[0])
    if any(len(box) != dimensions for box in boxes):
        raise ValueError("all benefit vectors must have equal dimensions")
    if dimensions == 1:
        return max(box[0] for box in boxes)
    cuts = sorted({0.0} | {box[-1] for box in boxes})
    volume = 0.0
    for low, high in zip(cuts, cuts[1:]):
        if high == low:
            continue
        active = tuple(box[:-1] for box in boxes if box[-1] >= high)
        if active:
            volume += (high - low) * _union_origin_boxes(active)
    return volume


def audit_resource_quality_frontier(
    arms: Sequence[ParetoArm],
    per_assignment_cap: ResourceVector,
    matched_assignments: int,
    *,
    model_id: str = "SYNTHETIC_UNAUTHENTICATED_MODEL",
    budget_id: str = "SYNTHETIC_UNAUTHENTICATED_CAP",
) -> ParetoBudgetAudit:
    """Exact small fixed-cap six-objective union HV, not a significance test.

    Resource totals are taken ACROSS the same number of assigned trials
    for every policy, so fractional mean token/test counts are never
    misrepresented as integral hardware readings. Success denominators
    are the original matched assignments, NOT released-patch counts.
    """
    if type(arms) not in (tuple, list):
        raise TypeError("bounded sequence of typed Pareto arms required")
    if not 1 <= len(arms) <= MAX_PARETO_POLICIES:
        raise ValueError("one to eight policies required for bounded exact hypervolume")
    if any(type(a) is not ParetoArm for a in arms):
        raise TypeError("only typed Pareto arm records accepted")
    if type(matched_assignments) is not int or matched_assignments <= 0:
        raise ValueError("positive integer matched assignment count required")
    if (type(model_id) is not str or not model_id.strip()
            or type(budget_id) is not str or not budget_id.strip()):
        raise ValueError("model/budget identity is required")
    _strict_positive_caps(per_assignment_cap)
    names = tuple(a.policy for a in arms)
    if len(set(names)) != len(names):
        raise ValueError("duplicate policy identity is not an additional Pareto arm")
    # ResourceVector validates the complete typed vector, including
    # integer token/test counts; multiplying N before normalization
    # preserves the five frozen per-assignment caps.
    aggregate_cap = ResourceVector(**{
        dim: getattr(per_assignment_cap, dim) * matched_assignments
        for dim in RESOURCE_FIELDS
    })
    ordered = tuple(sorted(arms, key=lambda a: a.policy))
    gains = {
        arm.policy: _benefit_vector(arm, aggregate_cap) for arm in ordered
    }
    dominators = {
        arm.policy: tuple(x.policy for x in ordered if dominates(x, arm))
        for arm in ordered
    }
    frontier = tuple(
        arm.policy for arm in ordered if not dominators[arm.policy]
    )
    ties = tuple(
        (a.policy, b.policy)
        for i, a in enumerate(ordered)
        for b in ordered[i + 1:]
        if (a.evaluator_claimed_success_rate
            == b.evaluator_claimed_success_rate
            and a.total_reported_cost == b.total_reported_cost)
    )
    all_boxes = tuple(gains[arm.policy] for arm in ordered)
    hypervolume = _union_origin_boxes(all_boxes)
    if not isfinite(hypervolume) or not -1e-12 <= hypervolume <= 1 + 1e-12:
        raise AssertionError("bounded normalized hypervolume arithmetic drift")
    # Contributions can be zero even for nondominated tied policies, because
    # removing ONE of two identical points leaves the union unchanged.
    contribution = []
    for i, arm in enumerate(ordered):
        without = _union_origin_boxes(all_boxes[:i] + all_boxes[i+1:])
        value = hypervolume - without
        if value < -1e-12:
            raise AssertionError("negative hypervolume contribution")
        contribution.append((arm.policy, max(0.0, value)))
    return ParetoBudgetAudit(
        model_id=model_id,
        budget_id=budget_id,
        matched_assignments_per_policy=matched_assignments,
        six_objectives=("claimed_full_task_success_maximize",) + tuple(
            "reported_" + dim + "_minimize" for dim in RESOURCE_FIELDS
        ),
        declared_budget_per_assignment=per_assignment_cap,
        arms=ordered,
        nondominated_policies=frontier,
        identical_tradeoff_ties=ties,
        dominated_by=tuple(
            (arm.policy, dominators[arm.policy]) for arm in ordered
        ),
        exact_normalized_hypervolume=hypervolume,
        marginal_hypervolume_by_policy=tuple(contribution),
    )


def audit_matched_postterminal_pareto(
    study: FrozenStudy,
    receipts: tuple[PolicyRunReceipt, ...],
    verdicts: tuple[EvaluatorVerdict, ...],
    *,
    model_id: str,
    budget_id: str,
    frozen_oracles: FrozenOracleManifest | None = None,
) -> ParetoBudgetAudit:
    """Build comparable policy arms only after complete terminal run audit.

    This checks structural equality of all task/model/seed/budget assignment
    cells and declared checkpoint/tool/oracle digests. A caller can forge
    receipts; successful structural validation does NOT authenticate them.
    Suppresses all policy-quality Pareto output on any timeout, safety stop,
    or infrastructure failure in the frozen matrix, consistent with the
    conservative confirmatory comparison gate.
    """
    audit = audit_confirmatory_run_matrix(
        study, receipts, verdicts, require_complete=True,
        frozen_oracles=frozen_oracles,
    )
    if model_id not in study.model_ids or budget_id not in dict(study.budgets):
        raise ValueError("model and budget must match frozen experimental factors")
    expected_per_policy = len(study.task_lineages) * len(study.seeds)
    outcome_groups = {}
    cost_groups = {}
    for o in audit.outcomes:
        if o.model_id == model_id and o.budget_id == budget_id:
            outcome_groups.setdefault(o.policy, []).append(o)
    for r in receipts:
        if r.model_id == model_id and r.budget_id == budget_id:
            cost_groups.setdefault(r.policy, []).append(r)
    arms = []
    for policy in study.policies:
        outcomes = outcome_groups.get(policy, [])
        records = cost_groups.get(policy, [])
        if len(outcomes) != expected_per_policy or len(records) != expected_per_policy:
            raise AssertionError("strict matched policy denominator drift")
        total = ResourceVector(**{
            dim: sum(getattr(r.consumed, dim) for r in records)
            for dim in RESOURCE_FIELDS
        })
        successes = sum(o.verified_success for o in outcomes)
        arms.append(ParetoArm(
            policy=policy,
            evaluator_claimed_success_rate=successes / expected_per_policy,
            total_reported_cost=total,
        ))
    return audit_resource_quality_frontier(
        tuple(arms), dict(study.budgets)[budget_id], expected_per_policy,
        model_id=model_id, budget_id=budget_id,
    )
