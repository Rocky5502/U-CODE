"""Exact finite-support THREE-WAY dependence stress test for DRPA.

Models binary high/low RELIABILITY, SAFETY and VALIDITY with separately
supplied one-dimensional marginals. The joint distribution is unknown.
We optimize expected VALID new-patch hypervolume improvement over all
2x2x2 couplings consistent with the three marginal probabilities.

The LP has 8 nonnegative atoms and four independent equality constraints:
normalization plus each high-state marginal. Its vertices have at most four
positive atoms, so enumerate <=C(8,4)=70 candidate bases with exact
fractions.Fraction elimination (no scipy, Monte Carlo or rounding in LP).
Finite Pareto geometry is computed on exact decimal-rational input values.

This fixes the earlier 2x2 reference's UNVERIFIED assumption that a
candidate's validity is independent of predicted reliability and safety.
It is a bounded MATHEMATICAL reference only, NOT a measured model, a
risk certificate, or a general-purpose multidimensional optimal transport
solver. No third-party code, LLM inference or hidden evaluators are run.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from math import isfinite
from typing import Sequence

from .acquisition import ParetoPoint
from .dependence_robust_acquisition import (
    RobustParetoProposal, bound_candidate_hvi,
)
from .vector_policy import ResourcePrices, ResourceVector

_ATOMS = tuple(product((0, 1), repeat=3))  # lexicographic (R_high,S_high,V_valid)
_EPS = 1e-12
_MAX_MENU = 64
_MAX_ARCHIVE = 256


def _frac(x: float) -> F:
    # Exact with respect to the *printed decimal input*, not the latent
    # population probability or an inexact numerical model's true output.
    if type(x) not in (float, int) or not isfinite(x):
        raise ValueError("finite numeric marginal or objective required")
    return F(str(x))


def _exact_hv(
    points: Sequence[ParetoPoint], reference: ParetoPoint,
) -> F:
    """Independent exact-rational two-dimensional dominated-area sweep."""
    rx, sy = _frac(reference.reliability), _frac(reference.safety)
    pairs = sorted(
        (_frac(p.reliability), _frac(p.safety))
        for p in points
        if _frac(p.reliability) > rx and _frac(p.safety) > sy
    )
    if not pairs:
        return F(0)
    suffix = [sy] * len(pairs)
    maximum = sy
    for i in range(len(pairs) - 1, -1, -1):
        maximum = max(maximum, pairs[i][1])
        suffix[i] = maximum
    area = F(0)
    prev = rx
    for i, (x, _) in enumerate(pairs):
        area += (x - prev) * (suffix[i] - sy)
        prev = x
    return area


def _solve_four(basis: tuple[int, ...], marginals: tuple[F, F, F]):
    """Unique basic coupling or None if singular/infeasible; exact arithmetic."""
    p, q, v = marginals
    b = (F(1), p, q, v)
    # A[:, atom] = (1,R,S,V) for eight binary atoms.
    aug = [
        [F(1) if row == 0 else F(_ATOMS[k][row-1])
         for k in basis] + [b[row]]
        for row in range(4)
    ]
    for col in range(4):
        pivot = next((i for i in range(col, 4) if aug[i][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [x / div for x in aug[col]]
        for row in range(4):
            if row == col:
                continue
            f = aug[row][col]
            if f:
                aug[row] = [
                    x - f * y for x, y in zip(aug[row], aug[col])
                ]
    solution = tuple(aug[i][4] for i in range(4))
    if any(x < 0 for x in solution):
        return None
    masses = [F(0)] * 8
    for idx, mass in zip(basis, solution):
        masses[idx] = mass
    return tuple(masses)


@lru_cache(maxsize=1024)
def _coupling_vertices(p: F, q: F, v: F) -> tuple[tuple[F, ...], ...]:
    """All distinct 2x2x2 coupling vertices under fixed Bernoulli marginals."""
    if any(not 0 <= x <= 1 for x in (p, q, v)):
        raise ValueError("marginals must belong to [0,1]")
    vertices = []
    seen = set()
    for basis in combinations(range(8), 4):
        masses = _solve_four(basis, (p, q, v))
        if masses is not None and masses not in seen:
            seen.add(masses)
            vertices.append(masses)
    if not vertices:
        raise AssertionError("independent Bernoulli marginals must admit a coupling")
    return tuple(vertices)


def _witness_text(weights: tuple[F, ...]) -> tuple[str, ...]:
    """Unambiguous, lossless rational weights in canonical eight-atom order."""
    return tuple(str(x) for x in weights)


@dataclass(frozen=True)
class JointValidityBounds:
    action_id: str
    gross_hvi_range: tuple[float, float]
    legacy_independent_validity_range: tuple[float, float]
    fully_independent_gross_hvi: float
    net_hvi_range: tuple[float, float]
    scalar_cost: float
    min_coupling_weights: tuple[str, ...]
    max_coupling_weights: tuple[str, ...]
    feasible_vertices: int
    atom_order: str = "000,001,010,011,100,101,110,111_(R,S,VALID)"
    interpretation: str = "EXACT_2x2x2_RATIONAL_COUPLING_SYNTHETIC_NO_CALIBRATION"


@dataclass(frozen=True)
class JointValidityChoice:
    action_id: str | None
    action: str
    selected: JointValidityBounds | None
    remaining_after: ResourceVector
    model_conditional_winner_separated: bool
    interpretation: str = "THREE_WAY_MARGINAL_MAXIMIN_NOT_REAL_TASK_RESULT"


def bound_joint_validity_hvi(
    archive: Sequence[ParetoPoint],
    proposal: RobustParetoProposal,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0, 0),
) -> JointValidityBounds:
    """Tight three-way coupling HVI bounds, including possible invalidity.

    P(R_high)=p, P(S_high)=q and P(VALID)=v are supplied separately.
    No assumption about pairwise or triple dependence is introduced.
    Invalid outcomes contribute zero new-patch HVI, never a fake point.
    The bounds are sharp ONLY over the specified finite-support marginal
    class; the marginals themselves may be uncalibrated or misspecified.
    """
    if not isinstance(proposal, RobustParetoProposal):
        raise TypeError("typed candidate-producing proposal required")
    if not isinstance(unit_prices, ResourcePrices):
        raise TypeError("typed five resource prices required")
    if not isinstance(reference, ParetoPoint):
        raise TypeError("typed Pareto reference point required")
    points = tuple(archive)
    if len(points) > _MAX_ARCHIVE:
        raise ValueError("bounded public Pareto archive limit exceeded")
    if any(not isinstance(x, ParetoPoint) for x in points):
        raise TypeError("typed public patch archive required")
    p = _frac(proposal.reliability.probability_high)
    q = _frac(proposal.safety.probability_high)
    v = _frac(proposal.probability_valid)
    baseline = _exact_hv(points, reference)
    r = proposal.reliability
    s = proposal.safety
    gains = {
        (ri, si): _exact_hv(
            (*points, ParetoPoint(
                r.high if ri else r.low,
                s.high if si else s.low,
            )), reference,
        ) - baseline
        for ri, si in product((0, 1), repeat=2)
    }
    if any(x < 0 for x in gains.values()):
        raise AssertionError("adding a Pareto point must not decrease HV")
    payoffs = tuple(
        gains[(ri, si)] if valid else F(0)
        for ri, si, valid in _ATOMS
    )
    vertices = _coupling_vertices(p, q, v)
    values = tuple(
        sum((a * b for a, b in zip(masses, payoffs)), F(0))
        for masses in vertices
    )
    min_idx = min(range(len(vertices)), key=lambda i: (values[i], i))
    max_idx = max(range(len(vertices)), key=lambda i: (values[i], -i))
    lo, hi = values[min_idx], values[max_idx]
    independence = tuple(
        (p if ri else 1-p) * (q if si else 1-q)
        * (v if valid else 1-v)
        for ri, si, valid in _ATOMS
    )
    nominal = sum((a*b for a, b in zip(independence, payoffs)), F(0))
    if not lo <= nominal <= hi:
        raise AssertionError("fully independent coupling outside sharp range")

    # Explicit comparison against the existing two-way algorithm which
    # assumes validity independently of (R,S). Never call it "truth".
    old = bound_candidate_hvi(points, proposal, unit_prices, reference)
    cost = proposal.cost.total_price(unit_prices)
    a, b = float(lo), float(hi)
    if not all(isfinite(x) for x in (a, b, float(nominal), cost)):
        raise ValueError("nonfinite coupled HVI or priced resource cost")
    if (a > old.gross_hvi_range[0] + 1e-10
            or b + 1e-10 < old.gross_hvi_range[1]):
        raise AssertionError("three-way ambiguity must contain legacy ambiguity")
    return JointValidityBounds(
        proposal.action_id, (a, b), old.gross_hvi_range,
        float(nominal), (a-cost, b-cost), cost,
        _witness_text(vertices[min_idx]),
        _witness_text(vertices[max_idx]),
        len(vertices),
    )


def choose_joint_validity_action(
    archive: Sequence[ParetoPoint],
    proposals: Sequence[RobustParetoProposal],
    remaining_budget: ResourceVector,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0, 0),
) -> JointValidityChoice:
    """Choose worst-case valid-HVI/cost action across all THREE-WAY couplings.

    Always enforce all five caps independently; no diagnostic evidence
    action can enter the patch frontier. A mathematically separated choice
    requires its LOWER score to exceed every feasible rival's UPPER score.
    These are model-conditional sensitivity values, NOT risk guarantees.
    """
    if not isinstance(remaining_budget, ResourceVector):
        raise TypeError("typed remaining five-resource budget required")
    if not isinstance(unit_prices, ResourcePrices):
        raise TypeError("typed resource prices required")
    rows = tuple(proposals)
    if len(rows) > _MAX_MENU:
        raise ValueError("at most 64 bounded exploratory proposals")
    if any(not isinstance(row, RobustParetoProposal) for row in rows):
        raise TypeError("typed candidate-producing proposals required")
    if len({row.action_id for row in rows}) != len(rows):
        raise ValueError("duplicate candidate action IDs")
    scored = [
        (row, bound_joint_validity_hvi(archive, row, unit_prices, reference))
        for row in rows if remaining_budget.affordable(row.cost)
    ]
    scored.sort(key=lambda t:t[0].action_id)
    positive = [(row, s) for row, s in scored if s.net_hvi_range[0] > _EPS]
    if not positive:
        return JointValidityChoice(None, "stop", None, remaining_budget, False)
    winner, score = max(positive, key=lambda t:t[1].net_hvi_range[0])
    separated = all(
        score.net_hvi_range[0] > rival.net_hvi_range[1] + _EPS
        for row, rival in scored if row.action_id != winner.action_id
    )
    return JointValidityChoice(
        winner.action_id, winner.action, score,
        remaining_budget.subtract(winner.cost), separated,
    )
