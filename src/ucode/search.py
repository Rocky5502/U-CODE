"""Explicit budget-constrained, Pareto-aware action selection.

Action benefit estimates are *inputs*, not measured scientific effects. This is
a testable decision-policy scaffold; fit/calibrate estimators on training data.
"""
from dataclasses import dataclass
from math import isfinite
from random import Random
from typing import Sequence

ACTIONS = ("generate", "retrieve", "test", "static_analysis", "repair", "abstain")


@dataclass(frozen=True)
class ActionEstimate:
    action: str
    expected_quality_gain: float
    expected_information_gain: float
    expected_security_gain: float
    cost: float

    def __post_init__(self) -> None:
        if self.action not in ACTIONS:
            raise ValueError("unknown action")
        for value in (self.expected_quality_gain, self.expected_information_gain,
                      self.expected_security_gain, self.cost):
            if not isfinite(value) or value < 0:
                raise ValueError("action estimates must be finite and nonnegative")


@dataclass(frozen=True)
class SearchState:
    remaining_budget: float
    predicted_failure_risk: float
    has_candidate: bool = True
    evidence_count: int = 0

    def __post_init__(self) -> None:
        if not isfinite(self.remaining_budget) or self.remaining_budget < 0:
            raise ValueError("remaining_budget must be nonnegative")
        if not 0 <= self.predicted_failure_risk <= 1:
            raise ValueError("predicted_failure_risk outside [0,1]")
        if self.evidence_count < 0:
            raise ValueError("negative evidence_count")


def dominates(a: ActionEstimate, b: ActionEstimate) -> bool:
    """a Pareto-dominates b (three benefits maximized, cost minimized)."""
    va = (a.expected_quality_gain, a.expected_information_gain,
          a.expected_security_gain, -a.cost)
    vb = (b.expected_quality_gain, b.expected_information_gain,
          b.expected_security_gain, -b.cost)
    return all(x >= y for x, y in zip(va, vb)) and any(x > y for x, y in zip(va, vb))


def pareto_frontier(actions: Sequence[ActionEstimate]) -> list[ActionEstimate]:
    """Non-dominated feasible actions in stable input order."""
    return [a for a in actions if not any(dominates(b, a) for b in actions if b is not a)]


def choose_action(
    state: SearchState,
    estimates: Sequence[ActionEstimate],
    policy: str = "uncertainty_pareto",
    seed: int = 0,
) -> ActionEstimate:
    """Select a search action using ONLY pre-outcome estimates and budget.

    Baselines: random, cost_first, fixed_test, quality_only. The Pareto variant
    incorporates predicted failure risk into information/security acquisition.
    The abstain action is safe when no feasible or admissible action exists.
    """
    if policy not in {"uncertainty_pareto", "random", "cost_first",
                      "fixed_test", "quality_only"}:
        raise ValueError("unknown policy")
    feasible = [
        a for a in estimates
        if a.cost <= state.remaining_budget and
        (state.has_candidate or a.action not in {"repair", "test", "static_analysis"})
        and a.action != "abstain"
    ]
    abstain = ActionEstimate("abstain", 0, 0, 0, 0)
    if not feasible:
        return abstain
    if policy == "random":
        return Random(seed).choice(feasible)
    if policy == "cost_first":
        return min(feasible, key=lambda a: (a.cost, a.action))
    if policy == "fixed_test":
        return next((a for a in feasible if a.action == "test"), min(feasible, key=lambda a: a.cost))
    if policy == "quality_only":
        return max(feasible, key=lambda a: (a.expected_quality_gain / max(a.cost, 1e-9),
                                             -a.cost, a.action))
    frontier = pareto_frontier(feasible)
    r = state.predicted_failure_risk
    def score(a: ActionEstimate) -> float:
        # Risk-dependent predicted utility per unit of execution cost;
        # coefficients are pre-registered heuristics, NOT learned/calibrated.
        return ((2 * a.expected_quality_gain +
                 (0.25 + 1.5 * r) * a.expected_information_gain +
                 (0.5 + r) * a.expected_security_gain)
                / max(a.cost, 1e-9))
    return max(frontier, key=lambda a: (score(a), -a.cost, a.action))
