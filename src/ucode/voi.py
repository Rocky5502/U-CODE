"""Exact one-step Bayesian value of *diagnostic evidence*, not model results.

For an existing candidate, actions such as testing and static analysis modify
beliefs; they do not create a new point on the patch Pareto frontier.

This module is a pure mathematical reference. Its input prior, sensitivity and
specificity MUST be estimated outside held-out evaluation. The acceptance
threshold is a policy preference, NOT a statistical risk guarantee.

No external code execution, model inference, third-party downloads or APIs.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence


def _probability(value: float, name: str) -> float:
    if not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite in [0,1]")
    return float(value)


@dataclass(frozen=True)
class DiagnosticAction:
    """Predicted binary evidence model for a candidate's *joint* acceptability.

    sensitivity = P(positive evidence | candidate truly acceptable)
    specificity = P(negative evidence | candidate truly unacceptable)
    cost = scalarized *preregistered* cost (not a free tool call)
    """

    name: str
    sensitivity: float
    specificity: float
    cost: float

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("diagnostic action needs a name")
        _probability(self.sensitivity, "sensitivity")
        _probability(self.specificity, "specificity")
        if not isfinite(self.cost) or self.cost <= 0:
            raise ValueError("diagnostic cost must be positive finite")


@dataclass(frozen=True)
class ReleaseRule:
    """Terminal release/abstain decision under a *predicted* risk gate.

    WARNING: max_predicted_failure is not a statistical risk certificate.
    """

    max_predicted_failure: float
    correct_reward: float = 1.0
    failure_penalty: float = 1.0
    unit_cost_penalty: float = 0.0

    def __post_init__(self) -> None:
        _probability(self.max_predicted_failure, "max_predicted_failure")
        for name in ("correct_reward", "failure_penalty", "unit_cost_penalty"):
            v = getattr(self, name)
            if not isfinite(v) or v < 0:
                raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class DiagnosticValue:
    """Inspectability of the *hypothetical* one-step evidence calculation."""

    action: str
    positive_probability: float
    negative_probability: float
    posterior_positive: float
    posterior_negative: float
    terminal_value_before: float
    expected_terminal_value_after: float
    gross_value_of_information: float
    net_gain: float


def terminal_value(prior_acceptable: float, rule: ReleaseRule) -> float:
    """Zero for abstain, otherwise expected utility of releasing one candidate."""
    p = _probability(prior_acceptable, "prior_acceptable")
    expected = p * rule.correct_reward - (1 - p) * rule.failure_penalty
    if 1 - p > rule.max_predicted_failure or expected <= 0:
        return 0.0
    return expected


def value_of_diagnostic(
    prior_acceptable: float, action: DiagnosticAction, rule: ReleaseRule,
) -> DiagnosticValue:
    """Enumerate exact predictive evidence outcomes for one binary diagnostic.

    p must be a *pre-outcome* probability of the JOINT correctness/safety
    predicate, not a hidden result. Missing-probability branches contribute
    exactly zero. This is a one-step Bayes reference, not a full planner.
    """
    p = _probability(prior_acceptable, "prior_acceptable")
    prob_pos = p * action.sensitivity + (1 - p) * (1 - action.specificity)
    prob_neg = p * (1 - action.sensitivity) + (1 - p) * action.specificity
    post_pos = p * action.sensitivity / prob_pos if prob_pos else p
    post_neg = p * (1 - action.sensitivity) / prob_neg if prob_neg else p
    before = terminal_value(p, rule)
    after = (prob_pos * terminal_value(post_pos, rule)
             + prob_neg * terminal_value(post_neg, rule))
    gain = after - before
    # Optimal contingent decision makes information nonnegative in exact
    # arithmetic; tolerate small floating point cancellation only.
    if gain < -1e-10:
        raise ArithmeticError("inconsistent Bayesian diagnostic model")
    gain = max(0.0, gain)
    return DiagnosticValue(
        action=action.name, positive_probability=prob_pos,
        negative_probability=prob_neg, posterior_positive=post_pos,
        posterior_negative=post_neg, terminal_value_before=before,
        expected_terminal_value_after=after,
        gross_value_of_information=gain,
        net_gain=gain - rule.unit_cost_penalty * action.cost,
    )


def choose_diagnostic(
    prior_acceptable: float, actions: Sequence[DiagnosticAction],
    rule: ReleaseRule, remaining_scalar_budget: float,
) -> DiagnosticValue | None:
    """Choose positive-net-VOI feasible diagnostic, or purchase no evidence.

    If diagnostics cannot help, returning None means the caller should
    either release or abstain according to terminal_value, not pay for tools.
    Separate full-policy budgets must still enforce tokens/tests/GPU/wall.
    """
    _probability(prior_acceptable, "prior_acceptable")
    if not isfinite(remaining_scalar_budget) or remaining_scalar_budget < 0:
        raise ValueError("remaining_scalar_budget must be nonnegative finite")
    best = None
    for action in actions:
        if action.cost <= remaining_scalar_budget:
            value = value_of_diagnostic(prior_acceptable, action, rule)
            if value.net_gain > 0 and (
                best is None or value.net_gain > best.net_gain
            ):
                best = value
    return best
