"""Finite-scenario robustness audit for conditional diagnostic evidence value.

An ONE-STEP decision check for a fixed patch and visible history; it is not
POMDP robust optimality, a statistical confidence bound, or a real task runner.

For each feasible probe a and pre-frozen possible conditional kernel k,
    gain(a,k) = E_k[U_0(P(Z=1|h,O_a))] - U_0(p)
                - lambda^T cost(a).
Bounds are min/max ONLY over the finite supplied scenario set.
Action choice maximizes min gain, otherwise release or abstain.
A missing reachable conditional row fails closed. Exact hard five-vector
limits apply independent of weighted price. No gold labels may appear.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalState, record_conditional,
)
from .vector_policy import ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


@dataclass(frozen=True)
class ScenarioEvidenceAssessment:
    action_id: str
    net_gains_by_scenario: tuple[float, ...]
    worst_case_gain: float
    best_case_gain: float
    label: str  # NEGATIVE_ALL, POSITIVE_ALL or SCENARIO_SENSITIVE


@dataclass(frozen=True)
class ScenarioRobustDecision:
    action: str  # diagnostic ID, release or abstain
    worst_case_improvement: float
    budget_after: ResourceVector
    baseline_terminal_utility: float
    assessments: tuple[ScenarioEvidenceAssessment, ...]
    uncertainty_scope: str
    experimental_task_count: int = 0


def conditional_one_step_net_gain(
    state: ConditionalState,
    probe: ConditionalProbe,
    kernel: ConditionalKernel,
    prices: ResourcePrices,
    rule: ReleaseRule,
) -> float:
    """Expected one-step diagnostic gain under ONE given scenario kernel."""
    if not isinstance(state, ConditionalState) or not isinstance(probe, ConditionalProbe):
        raise TypeError("typed state and probe required")
    if not isinstance(kernel, ConditionalKernel):
        raise TypeError("typed frozen kernel required")
    if not isinstance(prices, ResourcePrices) or not isinstance(rule, ReleaseRule):
        raise TypeError("typed prices and release rule required")
    if rule.unit_cost_penalty != 0:
        raise ValueError("cost is charged once through five-vector prices only")
    if probe.action_id in {o.action_id for o in state.history}:
        raise ValueError("cannot repurchase diagnostic in observed history")
    if not state.budget.affordable(probe.cost):
        raise ValueError("probe is not feasible under five hard budgets")

    row = kernel.get(probe.action_id, state.history)
    p = state.prior
    q_pos = p * row.positive_if_acceptable + (1.0 - p) * row.positive_if_unacceptable
    after = 0.0
    for observed, probability in ((True, q_pos), (False, 1.0 - q_pos)):
        if probability == 0:
            continue
        successor = record_conditional(state, probe, kernel, observed)
        after += probability * terminal_value(successor.prior, rule)
    gain = after - terminal_value(p, rule) - probe.cost.total_price(prices)
    if not isfinite(gain):
        raise ValueError("computed net gain must be finite")
    return gain


def choose_scenario_robust_probe(
    state: ConditionalState,
    probes: Sequence[ConditionalProbe],
    kernels: Sequence[ConditionalKernel],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    maximum_scenarios: int = 32,
) -> ScenarioRobustDecision:
    """Finite-scenario maximin ONE-step action or optional terminal stop.

    Every scenario must contain a valid matching row for EVERY currently
    feasible probe. Never silently shrink the scenario set per action:
    such selective omission would bias robust comparisons.
    """
    if type(maximum_scenarios) is not int or maximum_scenarios < 1:
        raise ValueError("positive finite-scenario limit required")
    models = tuple(kernels)
    proposals = tuple(probes)
    if not 1 <= len(models) <= maximum_scenarios:
        raise ValueError("at least one and at most maximum_scenarios kernels required")
    if any(not isinstance(k, ConditionalKernel) for k in models):
        raise TypeError("all scenarios must be frozen conditional kernels")
    if len(proposals) > 10 or any(not isinstance(p, ConditionalProbe) for p in proposals):
        raise ValueError("at most ten typed diagnostic probes required")
    ids = [p.action_id for p in proposals]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate diagnostic IDs")
    baseline = terminal_value(state.prior, rule)
    assessments = []
    best = None
    for probe in proposals:
        if probe.action_id in {o.action_id for o in state.history}:
            continue
        if not state.budget.affordable(probe.cost):
            continue
        values = tuple(
            conditional_one_step_net_gain(state, probe, k, prices, rule)
            for k in models
        )
        low, high = min(values), max(values)
        kind = ("NEGATIVE_ALL" if high <= 0 else
                "POSITIVE_ALL" if low > 0 else "SCENARIO_SENSITIVE")
        assessments.append(ScenarioEvidenceAssessment(
            probe.action_id, values, low, high, kind))
        if low > 0 and (best is None or low > best[0]):
            best = (low, probe)
    if best is not None:
        worst_gain, selected = best
        return ScenarioRobustDecision(
            selected.action_id, worst_gain,
            state.budget.subtract(selected.cost), baseline,
            tuple(assessments), "FINITE_FROZEN_SCENARIOS_ONLY_NOT_STATISTICAL_CERTIFICATE")
    stop = "release" if baseline > 0 else "abstain"
    return ScenarioRobustDecision(
        stop, 0.0, state.budget, baseline, tuple(assessments),
        "FINITE_FROZEN_SCENARIOS_ONLY_NOT_STATISTICAL_CERTIFICATE")
