"""Finite-scenario ONE-STEP planning for both diagnostics and generation/repair.

Unlike robust_mixed_intervention (which treats generative forecasts as
point estimates), this alternative evaluates BOTH types of actions under
the SAME finite, named hypothesis set. This is a complete uncertainty
sensitivity analysis for a RESTRICTED one-step action catalogue only.

Each scenario pairs a frozen history-conditioned diagnostic kernel
with expected terminal utility of generating/repairing a candidate.
Scenario forecasts must be trained/frozen without held-out oracles.
This is NOT statistical distribution-shift coverage, end-to-end planning,
measured code correctness, or independent risk certification.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .conditional_bes import ConditionalKernel, ConditionalProbe, ConditionalState
from .scenario_robust_evidence import conditional_one_step_net_gain
from .vector_policy import (
    GENERATORS, ResourcePrices, ResourceVector,
)
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class ScenarioGenerationAction:
    action: str
    cost: ResourceVector

    def __post_init__(self):
        if self.action not in GENERATORS:
            raise ValueError("scenario generator action must be generate or repair")
        if not isinstance(self.cost, ResourceVector) or self.cost.is_free():
            raise ValueError("generation/repair action must spend resources")


@dataclass(frozen=True)
class ScenarioGenerationValue:
    action: str
    expected_terminal_utility: float

    def __post_init__(self):
        if self.action not in GENERATORS:
            raise ValueError("generator utility needs a supported action")
        p = self.expected_terminal_utility
        if type(p) not in (float, int) or not isfinite(p) or p < 0:
            raise ValueError("generator utility must be finite nonnegative")


@dataclass(frozen=True)
class FrozenJointScenario:
    scenario_id: str
    diagnostic_kernel: ConditionalKernel | None
    generation_values: tuple[ScenarioGenerationValue, ...]

    def __post_init__(self):
        if (type(self.scenario_id) is not str
                or not self.scenario_id.strip()
                or len(self.scenario_id) > 128):
            raise ValueError("immutable scenario ID required")
        if self.diagnostic_kernel is not None and not isinstance(
                self.diagnostic_kernel, ConditionalKernel):
            raise TypeError("diagnostic kernel must be typed")
        if type(self.generation_values) is not tuple or any(
                not isinstance(v, ScenarioGenerationValue)
                for v in self.generation_values):
            raise TypeError("immutable typed generation values required")
        actions = [v.action for v in self.generation_values]
        if len(actions) != len(set(actions)):
            raise ValueError("duplicate generator forecast in same scenario")


@dataclass(frozen=True)
class JointActionAssessment:
    action: str
    category: str
    per_scenario_net_gain: tuple[float, ...]
    lower_net_gain: float
    upper_net_gain: float
    sensitivity: str


@dataclass(frozen=True)
class JointScenarioDecision:
    action: str
    category: str
    worst_case_net_gain: float
    remaining_budget: ResourceVector
    considered: tuple[JointActionAssessment, ...]
    scenario_ids: tuple[str, ...]
    scope: str = "ONE_STEP_FINITE_FROZEN_SCENARIOS_FOR_BOTH_ACTION_TYPES"
    executable_task_results: int = 0


def choose_joint_scenario_action(
    state: ConditionalState,
    actions: Sequence[ConditionalProbe | ScenarioGenerationAction],
    scenarios: Sequence[FrozenJointScenario],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    max_scenarios: int = 32,
) -> JointScenarioDecision:
    if not isinstance(state, ConditionalState):
        raise TypeError("typed conditional state required")
    if not isinstance(prices, ResourcePrices) or not isinstance(rule, ReleaseRule):
        raise TypeError("typed costs and terminal rule required")
    if rule.unit_cost_penalty != 0:
        raise ValueError("vector price charge must not be duplicated")
    if type(max_scenarios) is not int or max_scenarios < 1:
        raise ValueError("positive max_scenarios required")
    hypotheses = tuple(scenarios)
    if not 1 <= len(hypotheses) <= max_scenarios:
        raise ValueError("nonempty bounded frozen scenario set required")
    if any(not isinstance(s, FrozenJointScenario) for s in hypotheses):
        raise TypeError("typed scenario hypotheses required")
    ids = tuple(s.scenario_id for s in hypotheses)
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scenario identities")

    proposals = tuple(actions)
    if len(proposals) > 10 or any(not isinstance(a, (
            ConditionalProbe, ScenarioGenerationAction)) for a in proposals):
        raise TypeError("up to ten typed interventions are supported")
    labels = [a.action_id if isinstance(a, ConditionalProbe) else a.action
              for a in proposals]
    if len(labels) != len(set(labels)):
        raise ValueError("duplicate action ID across diagnostic and generation")

    consumed = {h.action_id for h in state.history}
    baseline = terminal_value(state.prior, rule)
    candidates = []
    best = None
    for action in proposals:
        if not state.budget.affordable(action.cost):
            continue
        if isinstance(action, ConditionalProbe) and action.action_id in consumed:
            continue
        gains = []
        for scenario in hypotheses:
            if isinstance(action, ConditionalProbe):
                if scenario.diagnostic_kernel is None:
                    raise ValueError("missing frozen diagnostic kernel for feasible action")
                gain = conditional_one_step_net_gain(
                    state, action, scenario.diagnostic_kernel, prices, rule)
                category, name = "diagnostic", action.action_id
            else:
                matching = [v.expected_terminal_utility
                            for v in scenario.generation_values
                            if v.action == action.action]
                if len(matching) != 1:
                    raise ValueError("missing frozen generation/repair scenario forecast")
                predicted = matching[0]
                if predicted > rule.correct_reward:
                    raise ValueError("scenario generator forecast exceeds reward ceiling")
                gain = predicted - baseline - action.cost.total_price(prices)
                category, name = "generation_or_repair", action.action
            if not isfinite(gain):
                raise ValueError("non-finite net value in scenario")
            gains.append(float(gain))
        lower, upper = min(gains), max(gains)
        sensitivity = ("NONPOSITIVE_ALL" if upper <= 0 else
                       "POSITIVE_ALL" if lower > 0 else "MODEL_SENSITIVE")
        candidates.append(JointActionAssessment(
            name, category, tuple(gains), lower, upper, sensitivity))
        if lower > 0 and (best is None or lower > best[0]):
            best = (lower, name, category, action.cost)
    if best is not None:
        gain, name, cat, cost = best
        return JointScenarioDecision(
            name, cat, gain, state.budget.subtract(cost),
            tuple(candidates), ids)
    return JointScenarioDecision(
        "release" if baseline > 0 else "abstain",
        "terminal", 0.0, state.budget, tuple(candidates), ids)
