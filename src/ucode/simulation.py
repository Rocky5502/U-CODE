"""Synthetic smoke-test simulator. NEVER report demo values as real-code results."""
from dataclasses import dataclass
from random import Random

from .search import ActionEstimate, SearchState, choose_action


@dataclass(frozen=True)
class DemoResult:
    policy: str
    seed: int
    actions: tuple[str, ...]
    budget_spent: float
    final_synthetic_quality: float
    synthetic_only: bool = True


def run_synthetic_episode(policy: str = "uncertainty_pareto", seed: int = 7,
                          total_budget: float = 9.0) -> DemoResult:
    """Deterministic fake outcome function for wiring/CI, not a study."""
    if total_budget < 0:
        raise ValueError("budget must be >=0")
    rng = Random(seed)
    budget = float(total_budget)
    quality = 0.25
    risk = 0.65
    sequence = []
    for step in range(12):
        estimates = [
            ActionEstimate("generate", .20, .05, .05, 3),
            ActionEstimate("retrieve", .06, .25, .02, 2),
            ActionEstimate("test", .02, .35, .05, 1),
            ActionEstimate("static_analysis", .02, .15, .30, 1),
            ActionEstimate("repair", .25, .05, .12, 3),
        ]
        state = SearchState(remaining_budget=budget,
                            predicted_failure_risk=risk,
                            has_candidate=True, evidence_count=step)
        a = choose_action(state, estimates, policy, seed + step)
        if a.action == "abstain":
            break
        sequence.append(a.action)
        budget -= a.cost
        # Deliberately arbitrary synthetic response; never an empirical outcome.
        quality = min(1., quality + a.expected_quality_gain * rng.uniform(.3, 1.))
        risk = max(0., risk - .03 * a.expected_information_gain)
    return DemoResult(policy, seed, tuple(sequence), total_budget-budget,
                      round(quality, 6))
