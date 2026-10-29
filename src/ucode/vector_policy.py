"""Pre-experimental one-step intervention selector with hard vector budgets.

This is a pure offline *planning reference*; not a fitted or deployed coding
agent. It compares diagnostic information gains against candidate-producing
forecasts on the SAME terminal-utility scale. Do not insert evaluator-only
oracle labels or hidden tests into forecasts.

Unlike scalar-cost prototypes, token/test/GPU/CPU/wall limits are hard and
independent. Forecasts and unit prices must be frozen before evaluation.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .voi import DiagnosticAction, ReleaseRule, terminal_value, value_of_diagnostic

RESOURCE_FIELDS = ("tokens", "test_calls", "gpu_seconds", "cpu_seconds", "wall_seconds")
DIAGNOSTICS = frozenset(("test", "static_analysis", "retrieve"))
GENERATORS = frozenset(("generate", "repair"))


@dataclass(frozen=True)
class ResourceVector:
    tokens: float = 0.0
    test_calls: float = 0.0
    gpu_seconds: float = 0.0
    cpu_seconds: float = 0.0
    wall_seconds: float = 0.0

    def __post_init__(self) -> None:
        for field in RESOURCE_FIELDS:
            value = getattr(self, field)
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError(f"{field} must be finite nonnegative")
        for field in ("tokens", "test_calls"):
            value = getattr(self, field)
            if float(value) != int(value):
                raise ValueError(f"{field} must be a whole number")

    def affordable(self, cost: "ResourceVector") -> bool:
        return all(getattr(cost, field) <= getattr(self, field)
                   for field in RESOURCE_FIELDS)

    def subtract(self, cost: "ResourceVector") -> "ResourceVector":
        if not self.affordable(cost):
            raise ValueError("action exceeds at least one hard resource budget")
        return ResourceVector(**{field: getattr(self, field) - getattr(cost, field)
                                 for field in RESOURCE_FIELDS})

    def total_price(self, unit_prices: "ResourcePrices") -> float:
        """Scalar planning cost; reject IEEE-754 overflow rather than using inf.

        Individual resource quantities and prices can each be finite while
        their product or sum is infinite. Such a value invalidates the
        stated finite-utility planning assumptions and must fail closed.
        """
        if not isinstance(unit_prices, ResourcePrices):
            raise TypeError("typed five-component resource prices required")
        value = sum(getattr(self, field) * getattr(unit_prices, field)
                    for field in RESOURCE_FIELDS)
        if not isfinite(value):
            raise ValueError("resource scalar cost overflowed to nonfinite value")
        return value

    def is_free(self) -> bool:
        return all(getattr(self, field) == 0 for field in RESOURCE_FIELDS)


@dataclass(frozen=True)
class ResourcePrices:
    """Predeclared scalarization weights; fractional per-unit prices allowed."""
    tokens: float = 0.0
    test_calls: float = 0.0
    gpu_seconds: float = 0.0
    cpu_seconds: float = 0.0
    wall_seconds: float = 0.0

    def __post_init__(self) -> None:
        for field in RESOURCE_FIELDS:
            value = getattr(self, field)
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError(f"{field} price must be finite nonnegative")


@dataclass(frozen=True)
class DiagnosticForecast:
    action: str
    sensitivity: float
    specificity: float
    cost: ResourceVector

    def __post_init__(self) -> None:
        if self.action not in DIAGNOSTICS:
            raise ValueError("diagnostic type must be test, retrieve or static_analysis")
        if self.cost.is_free():
            raise ValueError("nonterminal diagnostic must consume a resource")
        # Reuse strict binary likelihood validation from independent VOI reference.
        DiagnosticAction(self.action, self.sensitivity, self.specificity, 1.0)


@dataclass(frozen=True)
class GenerativeForecast:
    action: str
    expected_terminal_value_after: float
    cost: ResourceVector

    def __post_init__(self) -> None:
        if self.action not in GENERATORS:
            raise ValueError("generative type must be generate or repair")
        if self.cost.is_free():
            raise ValueError("nonterminal generation must consume a resource")
        if (type(self.expected_terminal_value_after) not in (int, float)
                or not isfinite(self.expected_terminal_value_after)
                or self.expected_terminal_value_after < 0):
            raise ValueError("predicted terminal utility must be finite nonnegative")


@dataclass(frozen=True)
class PlanDecision:
    """A one-step action recommendation, not an oracle-verified outcome."""
    action: str  # diagnostics, generation, repair, release, abstain
    predicted_net_improvement: float
    budget_after: ResourceVector
    reason: str


def choose_next_intervention(
    prior_acceptable: float | None,
    proposals: Sequence[DiagnosticForecast | GenerativeForecast],
    remaining_budget: ResourceVector,
    unit_prices: ResourcePrices,
    release_rule: ReleaseRule,
) -> PlanDecision:
    """Pick the best *strictly positive* marginal utility action, or stop.

    If prior is None, no patch exists: diagnostics/repair have no referent;
    only generate is admissible. For a candidate, predictions are pre-outcome.
    All candidates are scored against the same terminal baseline (best release
    or abstention). Costs are charged once through the preregistered vector
    prices, not twice through the standalone VOI example's scalar penalty.

    Does not claim a selective-risk certificate; this policy is a one-step
    reference, not an optimal solution of the Bellman equation.
    """
    has_candidate = prior_acceptable is not None
    if has_candidate:
        baseline = terminal_value(prior_acceptable, release_rule)
    else:
        baseline = 0.0
    best: tuple[float, int, DiagnosticForecast | GenerativeForecast] | None = None
    for i, proposal in enumerate(proposals):
        if not remaining_budget.affordable(proposal.cost):
            continue
        if not has_candidate and proposal.action != "generate":
            continue
        if isinstance(proposal, DiagnosticForecast):
            # The scalar cost required by the standalone VOI helper is
            # a nominal +1; we use ONLY its gross evidence gain here and
            # charge measured vector cost below. No double accounting.
            model = DiagnosticAction(proposal.action, proposal.sensitivity,
                                     proposal.specificity, 1.0)
            improvement = value_of_diagnostic(prior_acceptable, model,
                                              release_rule).gross_value_of_information
        elif isinstance(proposal, GenerativeForecast):
            if proposal.expected_terminal_value_after > release_rule.correct_reward:
                raise ValueError("forecast utility exceeds max release reward")
            improvement = proposal.expected_terminal_value_after - baseline
        else:
            raise TypeError("unexpected intervention forecast type")
        net = improvement - proposal.cost.total_price(unit_prices)
        if net > 0 and (best is None or net > best[0]):
            best = (net, i, proposal)
    if best is not None:
        gain, _, proposal = best
        return PlanDecision(proposal.action, gain,
                            remaining_budget.subtract(proposal.cost),
                            "pre-outcome positive expected utility; not a result")
    if has_candidate and baseline > 0:
        return PlanDecision("release", 0.0, remaining_budget,
                            "predicted risk and utility meet release policy only")
    return PlanDecision("abstain", 0.0, remaining_budget,
                        "no feasible positive predicted improvement or release")
