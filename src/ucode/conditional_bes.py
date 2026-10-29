"""History-conditioned Bounded Evidence Search for correlated diagnostics.

A finite, pre-specified conditional likelihood table replaces the
conditional-independence shortcut of budgeted_belief_search.py.

This restricted controller studies ONE existing candidate and diagnostic
actions ONLY. No generated code, hidden oracle results, model training or
third-party execution occur here. Likelihood tables must be fitted on
independent training data and frozen before held-out assessment.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Sequence

from .vector_policy import DIAGNOSTICS, ResourcePrices, ResourceVector
from .voi import ReleaseRule, terminal_value


def _probability(p: float, label: str) -> float:
    if type(p) not in (int, float) or not isfinite(p) or not 0 <= p <= 1:
        raise ValueError(f"{label} must be a finite probability")
    return float(p)


@dataclass(frozen=True)
class Observation:
    action_id: str
    positive: bool

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("observation requires an action ID")
        if type(self.positive) is not bool:
            raise ValueError("positive must be a boolean observation")


@dataclass(frozen=True)
class ConditionalRow:
    """P(positive | Y=1,h) and P(positive | Y=0,h) for the NEXT action.

    The sequence h contains strictly past VISIBLE diagnostic outcomes only.
    No gold outcome may be included in h; conditional likelihoods must be
    learned on sealed TRAINING labels, then frozen for evaluation.
    """
    action_id: str
    history: tuple[Observation, ...]
    positive_if_acceptable: float
    positive_if_unacceptable: float

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("row needs an action ID")
        if not isinstance(self.history, tuple):
            raise ValueError("history must be immutable tuple")
        seen = set()
        for item in self.history:
            if not isinstance(item, Observation):
                raise ValueError("history must contain typed observations")
            if item.action_id == self.action_id or item.action_id in seen:
                raise ValueError("conditional row history repeats an action")
            seen.add(item.action_id)
        _probability(self.positive_if_acceptable, "P(positive|acceptable,h)")
        _probability(self.positive_if_unacceptable, "P(positive|unacceptable,h)")


@dataclass(frozen=True)
class ConditionalKernel:
    rows: tuple[ConditionalRow, ...]

    def __post_init__(self):
        if not isinstance(self.rows, tuple) or not self.rows:
            raise ValueError("frozen history kernel requires rows")
        seen = set()
        for r in self.rows:
            if not isinstance(r, ConditionalRow):
                raise ValueError("all rows must be typed")
            key = (r.action_id, r.history)
            if key in seen:
                raise ValueError("duplicate conditional likelihood context")
            seen.add(key)

    def get(self, action_id: str, history: tuple[Observation, ...]) -> ConditionalRow:
        for r in self.rows:
            if r.action_id == action_id and r.history == history:
                return r
        raise ValueError(
            f"missing frozen conditional likelihood for {action_id} "
            f"after {len(history)} visible observations"
        )


@dataclass(frozen=True)
class ConditionalProbe:
    action_id: str
    kind: str
    cost: ResourceVector

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("probe needs a nonempty action ID")
        if self.kind not in DIAGNOSTICS:
            raise ValueError("only diagnostics are permitted in conditional model")
        if self.cost.is_free():
            raise ValueError("nonterminal probe must consume resources")


@dataclass(frozen=True)
class ConditionalState:
    """Only policy-visible information; no independent functional oracle."""
    prior: float
    budget: ResourceVector
    history: tuple[Observation, ...] = ()

    def __post_init__(self):
        _probability(self.prior, "prior")
        if not isinstance(self.history, tuple):
            raise ValueError("history must be immutable")
        ids = []
        for o in self.history:
            if not isinstance(o, Observation):
                raise ValueError("history entries must be typed")
            ids.append(o.action_id)
        if len(ids) != len(set(ids)):
            raise ValueError("same diagnostic cannot be purchased twice")


@dataclass(frozen=True)
class ConditionalPlan:
    action: str  # probe ID, release, abstain
    expected_net_utility: float
    stop_utility: float
    expected_gain: float
    budget_after_first: ResourceVector
    states_expanded: int


def record_conditional(
    state: ConditionalState,
    probe: ConditionalProbe,
    kernel: ConditionalKernel,
    observed_positive: bool,
) -> ConditionalState:
    """Consume a single *visible* observation via the fitted conditional row.

    A branch assigned probability zero cannot be observed under the
    frozen model without exposing model misspecification; fail closed.
    """
    if not isinstance(probe, ConditionalProbe):
        raise TypeError("probe must be a ConditionalProbe")
    if type(observed_positive) is not bool:
        raise ValueError("observed outcome must be boolean")
    if probe.action_id in (x.action_id for x in state.history):
        raise ValueError("diagnostic action already consumed")
    if not state.budget.affordable(probe.cost):
        raise ValueError("insufficient hard resource budget")
    row = kernel.get(probe.action_id, state.history)
    p = state.prior
    positive_mass = p * row.positive_if_acceptable + (1-p) * row.positive_if_unacceptable
    if observed_positive:
        if positive_mass == 0:
            raise ValueError("zero-probability positive diagnostic observation")
        updated = p * row.positive_if_acceptable / positive_mass
    else:
        neg_mass = 1 - positive_mass
        if neg_mass == 0:
            raise ValueError("zero-probability negative diagnostic observation")
        updated = p * (1-row.positive_if_acceptable) / neg_mass
    return ConditionalState(
        min(1.0, max(0.0, updated)),
        state.budget.subtract(probe.cost),
        state.history + (Observation(probe.action_id, observed_positive),),
    )


def plan_conditional(
    state: ConditionalState,
    probes: Sequence[ConditionalProbe],
    kernel: ConditionalKernel,
    prices: ResourcePrices,
    rule: ReleaseRule,
    horizon: int = 2,
    max_states: int = 30000,
    *,
    outside_option: float = 0.0,
) -> ConditionalPlan:
    """DP over history-conditional evidence without independence assertions.

    All reachable branch contexts must be provided; missing contexts throw
    instead of substituting a naive independent Bayes factor.

    outside_option is the fixed, nonnegative terminal utility obtainable by
    releasing another, UNCHANGED candidate from the archive. Every terminal
    branch chooses max(local release, outside_option, abstention). The
    expected value is therefore E[max(V_local(Y), V_other)] -- NOT
    max(E[V_local(Y)], V_other). This is exact for the specified finite
    per-candidate conditional kernel while other candidates are fixed;
    it is NOT joint cross-candidate belief updating or oracle correctness.
    """
    if type(horizon) is not int or not 1 <= horizon <= 4:
        raise ValueError("horizon must be integer 1 to 4")
    if type(max_states) is not int or max_states < 1:
        raise ValueError("max_states must be positive")
    if (type(outside_option) not in (int, float)
            or not isfinite(outside_option) or outside_option < 0):
        raise ValueError("outside option must be finite nonnegative terminal utility")
    outside_option = float(outside_option)
    if rule.unit_cost_penalty != 0:
        raise ValueError("charge costs with ResourcePrices only")
    probes = tuple(probes)
    if len(probes) > 10:
        raise ValueError("maximum ten forecast probes")
    if any(not isinstance(p, ConditionalProbe) for p in probes):
        raise TypeError("typed probes required")
    ids = [p.action_id for p in probes]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate probe IDs")
    if any(h.action_id not in ids for h in state.history):
        raise ValueError("history contains action outside frozen probe set")
    expanded = [0]

    @lru_cache(maxsize=None)
    def solve(s: ConditionalState, steps: int) -> tuple[float, str | None]:
        expanded[0] += 1
        if expanded[0] > max_states:
            raise ValueError("conditional search state cap exceeded")
        # Keep the other archived candidate as a terminal alternative
        # on EACH posterior branch, not only outside the expectation.
        stop = max(terminal_value(s.prior, rule), outside_option)
        val, choice = stop, None
        if steps == 0:
            return val, choice
        spent = {o.action_id for o in s.history}
        for probe in probes:
            if probe.action_id in spent or not s.budget.affordable(probe.cost):
                continue
            row = kernel.get(probe.action_id, s.history)
            p_pos = (s.prior * row.positive_if_acceptable
                     + (1-s.prior) * row.positive_if_unacceptable)
            expected = 0.0
            for positive, mass in ((True, p_pos), (False, 1 - p_pos)):
                if mass == 0:
                    continue
                updated = record_conditional(s, probe, kernel, positive)
                expected += mass * solve(updated, steps-1)[0]
            net = expected - probe.cost.total_price(prices)
            if net > val + 1e-12:
                val, choice = net, probe.action_id
        return val, choice

    stop = max(terminal_value(state.prior, rule), outside_option)
    value, chosen = solve(state, horizon)
    if chosen is None:
        # A higher outside option belongs to another archived patch.
        # In that case the local planner reports no local action; the
        # archive adapter remains responsible for the actual release SHA.
        local_stop = terminal_value(state.prior, rule)
        action = "release" if local_stop > 0 and local_stop >= outside_option else "abstain"
        return ConditionalPlan(action, value, stop, 0, state.budget, expanded[0])
    probe = next(p for p in probes if p.action_id == chosen)
    return ConditionalPlan(chosen, value, stop, value-stop,
                           state.budget.subtract(probe.cost), expanded[0])
