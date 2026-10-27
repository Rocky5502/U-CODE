"""One-step evidence-versus-generation decision with FINITE evidence-model ambiguity.

This is a pure mathematical reference for an EXISTING code candidate.
Diagnostic actions use worst-case net value across a frozen finite family of
history-conditional kernels. Candidate-generating actions use separately
frozen point forecasts; they are NOT robust to generator-model errors.

This narrows the gap between the paper's central allocation formulation and
previously separate analytical prototypes. No LLM generates code, no patch
is executed, no hidden oracle is queried and no actual outcome is measured.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .conditional_bes import ConditionalKernel, ConditionalProbe, ConditionalState
from .scenario_robust_evidence import (
    ScenarioEvidenceAssessment, conditional_one_step_net_gain,
)
from .vector_policy import GenerativeForecast, ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class MixedRobustDecision:
    action: str
    action_kind: str
    conservative_net_improvement: float
    budget_after: ResourceVector
    evidence_assessments: tuple[ScenarioEvidenceAssessment, ...]
    applicability: str = "ONE_STEP_FROZEN_DIAGNOSTIC_SCENARIOS_GENERATION_POINT_FORECAST"
    observed_full_task_successes: int = 0


def choose_evidence_vs_generation(
    state: ConditionalState,
    interventions: Sequence[ConditionalProbe | GenerativeForecast],
    kernels: Sequence[ConditionalKernel],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    maximum_scenarios: int = 32,
) -> MixedRobustDecision:
    """Select highest positive worst-scenario net improvement, or stop.

    This is a ONE-STEP reference; the generator point forecast MUST be
    separately estimated without held-out task oracle information.
    Diagnostic outcomes are history-dependent and require every conditional
    row across ALL frozen kernels, not only the model favoring the action.
    """
    if (not isinstance(state, ConditionalState)
            or not isinstance(prices, ResourcePrices)
            or not isinstance(rule, ReleaseRule)):
        raise TypeError("typed conditional state, prices and release rule required")
    if rule.unit_cost_penalty:
        raise ValueError("scalar rule penalty would double-charge vector prices")
    actions = tuple(interventions)
    if len(actions) > 10:
        raise ValueError("at most ten action forecasts in reference controller")
    if any(not isinstance(a, (ConditionalProbe, GenerativeForecast))
           for a in actions):
        raise TypeError("unsupported mixed intervention forecast type")
    if len({a.action_id if isinstance(a, ConditionalProbe) else a.action
            for a in actions}) != len(actions):
        raise ValueError("duplicate cross-type action identifier")

    active_probes = [
        x for x in actions if isinstance(x, ConditionalProbe)
        and state.budget.affordable(x.cost)
        and x.action_id not in {h.action_id for h in state.history}
    ]
    frozen = tuple(kernels)
    if active_probes and (not 1 <= len(frozen) <= maximum_scenarios
                          or any(not isinstance(k, ConditionalKernel) for k in frozen)):
        raise ValueError("missing or unsupported frozen diagnostic kernel ensemble")
    baseline = terminal_value(state.prior, rule)
    best = None
    assessments = []
    for idx, action in enumerate(actions):
        if not state.budget.affordable(action.cost):
            continue
        if isinstance(action, ConditionalProbe):
            if action.action_id in {h.action_id for h in state.history}:
                continue
            gains = tuple(
                conditional_one_step_net_gain(state, action, k, prices, rule)
                for k in frozen)
            lo, hi = min(gains), max(gains)
            label = ("NEGATIVE_ALL" if hi <= 0 else
                     "POSITIVE_ALL" if lo > 0 else "SCENARIO_SENSITIVE")
            assessments.append(ScenarioEvidenceAssessment(
                action.action_id, gains, lo, hi, label))
            minimum_gain = lo
            name, kind = action.action_id, "diagnostic"
        else:
            if action.expected_terminal_value_after > rule.correct_reward:
                raise ValueError("generative terminal forecast exceeds theoretical reward")
            minimum_gain = (
                action.expected_terminal_value_after - baseline
                - action.cost.total_price(prices)
            )
            if not isfinite(minimum_gain):
                raise ValueError("generative gain is nonfinite")
            name, kind = action.action, "generation_or_repair"
        if minimum_gain > 0 and (best is None or minimum_gain > best[0]):
            best = (minimum_gain, idx, name, kind, action.cost)
    if best is not None:
        gain, _, name, kind, cost = best
        return MixedRobustDecision(
            name, kind, gain, state.budget.subtract(cost),
            tuple(assessments))
    return MixedRobustDecision(
        "release" if baseline > 0 else "abstain",
        "terminal", 0.0, state.budget, tuple(assessments))
