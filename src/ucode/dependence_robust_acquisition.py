"""Dependence-robust two-point Pareto acquisition: SYNTHETIC reference ONLY.

Given TWO supported outcomes for each objective and their separately supplied
marginal probabilities, enumerate the exact Frechet interval for their unknown
joint dependence. This is NOT general distributionally robust optimization and
does NOT replace a calibrated multivariate distribution or an executable agent.

Only generate/repair create Pareto points; evidence actions must use the VOI
controllers. Real model, benchmark, uncertainty-fit and sealed oracle results: 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .acquisition import ParetoPoint, hypervolume_2d
from .vector_policy import ResourcePrices, ResourceVector

_ACTIONS = frozenset(("generate", "repair"))
_EPS = 1e-12


def _probability(x: float, label: str) -> float:
    if type(x) not in (int, float) or not isfinite(x) or not 0 <= x <= 1:
        raise ValueError(label + " must be finite in [0,1]")
    return float(x)


@dataclass(frozen=True)
class TwoPointOutcome:
    """Provisional low/high utility states; these are NOT observed labels."""
    low: float
    high: float
    probability_high: float

    def __post_init__(self) -> None:
        l = _probability(self.low, "low")
        h = _probability(self.high, "high")
        _probability(self.probability_high, "probability_high")
        if l > h:
            raise ValueError("two-point utility outcomes must be ordered")


@dataclass(frozen=True)
class RobustParetoProposal:
    """One candidate-producing action with a separate hard five-resource cost."""
    action_id: str
    action: str
    reliability: TwoPointOutcome
    safety: TwoPointOutcome
    probability_valid: float
    cost: ResourceVector

    def __post_init__(self) -> None:
        if type(self.action_id) is not str or not self.action_id.strip() or len(self.action_id) > 128:
            raise ValueError("bounded unique candidate action ID required")
        if self.action not in _ACTIONS:
            raise ValueError("only generate or repair may add new Pareto points")
        if (not isinstance(self.reliability, TwoPointOutcome)
                or not isinstance(self.safety, TwoPointOutcome)):
            raise TypeError("typed two-outcome objective marginals required")
        _probability(self.probability_valid, "probability_valid")
        if not isinstance(self.cost, ResourceVector) or self.cost.is_free():
            raise ValueError("nonterminal candidate creation must consume resources")


@dataclass(frozen=True)
class DependenceHVI:
    action_id: str
    joint_high_high_range: tuple[float, float]
    gross_hvi_range: tuple[float, float]
    independent_gross_hvi: float
    scalar_cost: float
    robust_net_range: tuple[float, float]
    independent_net: float
    dependence_width: float
    interpretation: str = "TWO_POINT_FRECHET_BOUND_SYNTHETIC_NO_CALIBRATION"


@dataclass(frozen=True)
class DependenceRobustChoice:
    action_id: str | None
    action: str
    selected: DependenceHVI | None
    remaining_after: ResourceVector
    # Conditional on all supplied two-point marginals and cost assumptions.
    ranking_stable_over_independent_ambiguity_sets: bool
    interpretation: str = "RESTRICTED_SYNTHETIC_MAXIMIN_NOT_EMPIRICAL"


def bound_candidate_hvi(
    archive: Sequence[ParetoPoint],
    proposal: RobustParetoProposal,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0, 0),
) -> DependenceHVI:
    """Exact coupling bounds for a 2x2 *finite-support* outcome pair.

    p=P(reliability high), q=P(safety high); unknown t=P(both high)
    is in [max(0,p+q-1), min(p,q)]. The expected HVI is affine in t,
    so its extrema occur exactly at the two Frechet endpoints.
    Valid-result probability is stipulated INDEPENDENT of both objective
    outcomes here: that is an explicit restrictive assumption. If joint
    validity dependence is unknown, these bounds are not valid.
    """
    if not isinstance(proposal, RobustParetoProposal):
        raise TypeError("typed candidate proposal required")
    if not isinstance(unit_prices, ResourcePrices):
        raise TypeError("typed resource prices required")
    if not isinstance(reference, ParetoPoint):
        raise TypeError("typed fixed reference point required")
    archive = tuple(archive)
    if any(not isinstance(x, ParetoPoint) for x in archive):
        raise TypeError("typed public Pareto archive required")
    base = hypervolume_2d(archive, reference)
    r, s = proposal.reliability, proposal.safety
    p, q = float(r.probability_high), float(s.probability_high)
    tlo, thi = max(0., p + q - 1.), min(p, q)
    def improvement(x: float, y: float) -> float:
        current = hypervolume_2d((*archive, ParetoPoint(x, y)), reference)
        return max(0., current - base)
    g00 = improvement(r.low, s.low)
    g01 = improvement(r.low, s.high)
    g10 = improvement(r.high, s.low)
    g11 = improvement(r.high, s.high)

    def expected(t: float) -> float:
        # Explicit Frechet 2x2 atom probabilities, all nonnegative.
        return ((1. - p - q + t) * g00 + (q - t) * g01
                + (p - t) * g10 + t * g11)

    v0, v1 = expected(tlo), expected(thi)
    vi = expected(p * q)
    valid = float(proposal.probability_valid)
    lower, upper = sorted((max(0., v0 * valid), max(0., v1 * valid)))
    independent = max(0., vi * valid)
    cost = proposal.cost.total_price(unit_prices)
    if not all(isfinite(x) for x in (lower, upper, independent, cost)):
        raise ValueError("nonfinite candidate acquisition value")
    if not lower - _EPS <= independent <= upper + _EPS:
        raise AssertionError("independent coupling must lie inside Frechet interval")
    return DependenceHVI(
        action_id=proposal.action_id,
        joint_high_high_range=(tlo, thi),
        gross_hvi_range=(lower, upper),
        independent_gross_hvi=independent,
        scalar_cost=cost,
        robust_net_range=(lower - cost, upper - cost),
        independent_net=independent - cost,
        dependence_width=upper - lower,
    )


def choose_dependence_robust_action(
    archive: Sequence[ParetoPoint],
    proposals: Sequence[RobustParetoProposal],
    remaining_budget: ResourceVector,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0, 0),
) -> DependenceRobustChoice:
    """Maximin *net* HVI subject to five hard budgets, or stop.

    A robust winner is 'ranking stable' ONLY if its lower net payoff is
    strictly greater than the STOP value (0) and every feasible rival's
    upper net payoff. This is deterministic model-conditional separation,
    NOT a statistical certificate and NOT a claim of general optimality.
    """
    if not isinstance(remaining_budget, ResourceVector):
        raise TypeError("typed five-component remaining budget required")
    options = tuple(proposals)
    if any(not isinstance(x, RobustParetoProposal) for x in options):
        raise TypeError("typed immutable candidate proposals required")
    if len(options) > 64:
        raise ValueError("bounded exploratory candidate menu required")
    ids = [x.action_id for x in options]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate candidate action IDs")
    scored = [
        (p, bound_candidate_hvi(archive, p, unit_prices, reference))
        for p in options if remaining_budget.affordable(p.cost)
    ]
    # Deterministic lexical ties are independent of caller ordering.
    scored.sort(key=lambda row: row[0].action_id)
    eligible = [(p, s) for p, s in scored if s.robust_net_range[0] > _EPS]
    if not eligible:
        return DependenceRobustChoice(None, "stop", None, remaining_budget, False)
    winner, score = max(eligible, key=lambda row: row[1].robust_net_range[0])
    stable = all(
        score.robust_net_range[0] > other.robust_net_range[1] + _EPS
        for p, other in scored if p.action_id != winner.action_id
    )
    return DependenceRobustChoice(
        winner.action_id, winner.action, score,
        remaining_budget.subtract(winner.cost), stable,
    )


def choose_independence_baseline(
    archive: Sequence[ParetoPoint],
    proposals: Sequence[RobustParetoProposal],
    remaining_budget: ResourceVector,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0, 0),
) -> str | None:
    """Matched-choice negative control, restricted to the independence joint."""
    if not isinstance(remaining_budget, ResourceVector):
        raise TypeError("typed remaining budget required")
    options = tuple(proposals)
    if len({p.action_id for p in options}) != len(options):
        raise ValueError("duplicate candidate action IDs")
    if any(not isinstance(p, RobustParetoProposal) for p in options):
        raise TypeError("typed candidate menu required")
    scored = sorted(
        ((p.action_id, bound_candidate_hvi(
            archive, p, unit_prices, reference).independent_net)
         for p in options if remaining_budget.affordable(p.cost)),
        key=lambda row: row[0],
    )
    best = max(scored, key=lambda x: x[1], default=None)
    if best is None or best[1] <= _EPS:
        return None
    return best[0]
