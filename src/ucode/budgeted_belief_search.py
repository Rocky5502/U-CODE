"""BES: bounded evidence-and-generation look-ahead with vector budgets.

An EXACT finite-tree dynamic program *under its input-model assumptions*.
NOT an optimal general coding-agent POMDP, a trained policy, a novel theorem,
a formal risk guarantee, or an empirical U-CODE result.

One candidate is tracked at a time. Each candidate-producing action may
replace that candidate, while each diagnostic updates its probability of
acceptability without creating a candidate. All forecast probabilities must
be estimated pre-outcome, before evaluation-only hidden tests are revealed.

Dependencies between distinct diagnostics on the SAME candidate must be
modeled explicitly in a later conditional-kernel implementation. This
reference uses conditional independence and refuses multi-probe planning
unless that modeling assumption is affirmatively declared.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Sequence

from .vector_policy import (
    DIAGNOSTICS, GENERATORS, ResourcePrices, ResourceVector,
)
from .voi import ReleaseRule, terminal_value


def _probability(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a numeric probability")
    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite in [0,1]")
    return float(value)


@dataclass(frozen=True)
class EvidenceAction:
    action_id: str
    kind: str
    sensitivity: float
    specificity: float
    cost: ResourceVector

    def __post_init__(self):
        if not self.action_id or not self.action_id.strip():
            raise ValueError("evidence action needs a stable ID")
        if self.kind not in DIAGNOSTICS:
            raise ValueError("evidence kind must be test/retrieve/static_analysis")
        _probability(self.sensitivity, "sensitivity")
        _probability(self.specificity, "specificity")
        if self.cost.is_free():
            raise ValueError("nonterminal evidence must consume resources")


@dataclass(frozen=True)
class CandidateScenario:
    probability: float
    new_prior: float | None

    def __post_init__(self):
        _probability(self.probability, "scenario probability")
        if self.new_prior is not None:
            _probability(self.new_prior, "new patch predicted acceptability")


@dataclass(frozen=True)
class CandidateAction:
    action_id: str
    kind: str
    scenarios: tuple[CandidateScenario, ...]
    cost: ResourceVector

    def __post_init__(self):
        if not self.action_id or not self.action_id.strip():
            raise ValueError("candidate action needs a stable ID")
        if self.kind not in GENERATORS:
            raise ValueError("candidate action must generate or repair")
        if self.cost.is_free():
            raise ValueError("nonterminal generation must consume resources")
        if not self.scenarios or not isinstance(self.scenarios, tuple):
            raise ValueError("candidate scenarios must be a nonempty tuple")
        mass = sum(s.probability for s in self.scenarios)
        if abs(mass - 1.0) > 1e-9:
            raise ValueError("candidate scenario probabilities must sum to one")


@dataclass(frozen=True)
class BeliefPlan:
    first_action: str
    kind: str
    expected_net_utility: float
    immediate_stop_utility: float
    predicted_improvement: float
    budget_after_first: ResourceVector
    states_expanded: int
    horizon: int

    @property
    def should_intervene(self) -> bool:
        return self.kind not in ("release", "abstain")


def plan_bounded_evidence_search(
    prior: float | None,
    actions: Sequence[EvidenceAction | CandidateAction],
    remaining_budget: ResourceVector,
    prices: ResourcePrices,
    release_rule: ReleaseRule,
    horizon: int = 2,
    *,
    assume_independent_diagnostics: bool = False,
    max_states: int = 30000,
) -> BeliefPlan:
    """Finite-depth Bellman recursion with probabilistic observable branches.

    Every action is purchasable at most once within one planning call.
    CandidateAction.new_prior=None means an unusable new candidate and the
    prior candidate (if any) is retained. Successful generate/repair REPLACES
    the current candidate. No Pareto archive is claimed in this version.

    If planning multiple distinct diagnostic probes, their outcome channels
    are assumed conditionally independent given the unchanged candidate's
    latent acceptability. Caller must explicitly accept this assumption.
    For correlated verifier errors, a learned joint/conditional kernel is
    mandatory before real evaluation. Replan after actual visible evidence.

    Prices are scalar *planning* weights, but all five resource dimensions
    impose independent hard feasibility constraints. Terminal release uses
    only the frozen predicted risk rule, NOT a certified risk guarantee.

    Exactness refers solely to this finite discretized, one-candidate,
    exogenously supplied probabilistic branching model.
    """
    if prior is not None:
        prior = _probability(prior, "candidate prior")
    if type(horizon) is not int or not 1 <= horizon <= 4:
        raise ValueError("horizon must be an integer from 1 to 4")
    if type(max_states) is not int or max_states < 1:
        raise ValueError("max_states must be positive integer")
    if release_rule.unit_cost_penalty != 0:
        raise ValueError("cost penalties must use ResourcePrices only")
    actions = tuple(actions)
    if len(actions) > 10:
        raise ValueError("at most ten actions in bounded reference planner")
    if any(not isinstance(a, (EvidenceAction, CandidateAction)) for a in actions):
        raise TypeError("all forecast actions must be typed")
    ids = [a.action_id for a in actions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate action_id would merge distinct evidence")
    n_probes = sum(isinstance(a, EvidenceAction) for a in actions)
    if horizon > 1 and n_probes > 1 and not assume_independent_diagnostics:
        raise ValueError("multi-probe planning requires declared conditional independence")

    expanded = [0]

    @lru_cache(maxsize=None)
    def solve(
        belief: float | None,
        budget: ResourceVector,
        available_mask: int,
        depth: int,
    ) -> tuple[float, int | None]:
        expanded[0] += 1
        if expanded[0] > max_states:
            raise ValueError("planning state cap exceeded; reduce horizon/actions")
        stop = terminal_value(belief, release_rule) if belief is not None else 0.0
        best_value, best_index = stop, None
        if depth == 0:
            return best_value, best_index
        for index, action in enumerate(actions):
            if not available_mask & (1 << index):
                continue
            if not budget.affordable(action.cost):
                continue
            if belief is None and (
                isinstance(action, EvidenceAction) or action.kind == "repair"
            ):
                continue

            next_budget = budget.subtract(action.cost)
            next_mask = available_mask & ~(1 << index)
            charge = action.cost.total_price(prices)
            expected_future = 0.0
            if isinstance(action, EvidenceAction):
                # A test only updates the existing candidate belief.
                p_pos = belief * action.sensitivity + (1 - belief) * (1 - action.specificity)
                p_neg = (1 - p_pos)
                if p_pos > 0:
                    q_pos = belief * action.sensitivity / p_pos
                    expected_future += p_pos * solve(
                        _probability(q_pos, "positive posterior"),
                        next_budget, next_mask, depth - 1,
                    )[0]
                if p_neg > 0:
                    q_neg = belief * (1 - action.sensitivity) / p_neg
                    expected_future += p_neg * solve(
                        _probability(q_neg, "negative posterior"),
                        next_budget, next_mask, depth - 1,
                    )[0]
            else:
                for scenario in action.scenarios:
                    if scenario.probability == 0:
                        continue
                    replacement = (scenario.new_prior if scenario.new_prior is not None
                                   else belief)
                    expected_future += scenario.probability * solve(
                        replacement, next_budget, next_mask, depth - 1,
                    )[0]
            candidate_value = expected_future - charge
            if candidate_value > best_value + 1e-12:
                best_value, best_index = candidate_value, index
        return best_value, best_index

    terminal = terminal_value(prior, release_rule) if prior is not None else 0.0
    value, best = solve(prior, remaining_budget, (1 << len(actions)) - 1, horizon)
    if best is None:
        terminal_action = "release" if terminal > 0 else "abstain"
        return BeliefPlan(
            first_action=terminal_action, kind=terminal_action,
            expected_net_utility=value, immediate_stop_utility=terminal,
            predicted_improvement=0.0, budget_after_first=remaining_budget,
            states_expanded=expanded[0], horizon=horizon,
        )
    selected = actions[best]
    return BeliefPlan(
        first_action=selected.action_id, kind=selected.kind,
        expected_net_utility=value, immediate_stop_utility=terminal,
        predicted_improvement=value - terminal,
        budget_after_first=remaining_budget.subtract(selected.cost),
        states_expanded=expanded[0], horizon=horizon,
    )
