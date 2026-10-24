"""Prototype budget-constrained Expected Hypervolume Improvement (EHVI).

This is a reproducible search acquisition *algorithm* built on predictive
distributions supplied by an external, separately calibrated estimator.
The 2D hypervolume uses reliability and safety utility on newly generated
candidate patches ONLY. Verification-only actions must use evidence value
(see voi.py) and never hallucinate a new Pareto point. Execution cost is
a hard constraint and denominator. No real-model results are asserted.
"""
from dataclasses import dataclass
from math import isfinite
from random import Random
from typing import Sequence

# EHVI expands a *candidate patch* frontier; tests and retrieval do not.
CANDIDATE_PRODUCING_ACTIONS = frozenset({"generate", "repair"})


@dataclass(frozen=True)
class ParetoPoint:
    reliability: float  # predicted/verified success scale 0..1 (document source)
    safety: float       # predicted/verified safety utility scale 0..1

    def __post_init__(self):
        for value in (self.reliability, self.safety):
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError("normalized objectives must be in [0,1]")


@dataclass(frozen=True)
class AcquisitionProposal:
    action: str
    mean_reliability: float
    sd_reliability: float
    mean_safety: float
    sd_safety: float
    probability_valid: float
    cost: float

    def __post_init__(self):
        if self.action not in CANDIDATE_PRODUCING_ACTIONS:
            raise ValueError("EHVI requires a candidate-producing action: generate or repair")
        for x in (self.mean_reliability, self.mean_safety, self.probability_valid):
            if not isfinite(x) or not 0 <= x <= 1:
                raise ValueError("prediction or probability must be in [0,1]")
        for x in (self.sd_reliability, self.sd_safety):
            if not isfinite(x) or x < 0:
                raise ValueError("standard deviations must be nonnegative")
        if not isfinite(self.cost) or self.cost <= 0:
            raise ValueError("cost must be positive")


def hypervolume_2d(
    points: Sequence[ParetoPoint], reference: ParetoPoint = ParetoPoint(0, 0)
) -> float:
    """Exact 2D dominated area above a lower reference point, maximizing both.

    Duplicated/dominated points do not change the hypervolume. Reference must
    be held fixed across competing policies.
    """
    ps = sorted(
        [(p.reliability, p.safety) for p in points
         if p.reliability > reference.reliability and p.safety > reference.safety]
    )
    if not ps:
        return 0.
    suffix_y = [0.] * len(ps)
    biggest = reference.safety
    for i in range(len(ps)-1, -1, -1):
        biggest = max(biggest, ps[i][1])
        suffix_y[i] = biggest
    previous = reference.reliability
    area = 0.
    for i, (x, _) in enumerate(ps):
        area += (x - previous) * (suffix_y[i] - reference.safety)
        previous = x
    return area


def expected_hvi_per_cost(
    archive: Sequence[ParetoPoint], proposal: AcquisitionProposal,
    samples: int = 512, seed: int = 7,
    reference: ParetoPoint = ParetoPoint(0, 0)
) -> float:
    """Monte Carlo EHVI/cost using independent truncated-normal predicted marginals.

    Independence is a simplifying pilot assumption; replace with a learned joint
    distribution and pre-registered uncertainty calibration before real claims.
    A Bernoulli valid-result draw is integrated analytically with probability_valid.
    """
    if samples <= 0:
        raise ValueError("samples must be positive")
    rng = Random(seed)
    base = hypervolume_2d(archive, reference)
    gain = 0.
    for _ in range(samples):
        q = min(1., max(0., rng.gauss(proposal.mean_reliability, proposal.sd_reliability)))
        s = min(1., max(0., rng.gauss(proposal.mean_safety, proposal.sd_safety)))
        gain += max(0., hypervolume_2d([*archive, ParetoPoint(q, s)], reference) - base)
    return (gain / samples) * proposal.probability_valid / proposal.cost


def select_ehvi_action(
    archive: Sequence[ParetoPoint], proposals: Sequence[AcquisitionProposal],
    remaining_budget: float, samples: int = 512, seed: int = 7,
    minimum_mean_reliability: float = 0.
) -> AcquisitionProposal | None:
    """Choose a feasible maximal EHVI/cost action; None is explicit abstention.

    Numeric reliability/safety estimates must be made before hidden-test data.
    minimum_mean_reliability is a *policy setting*, not a guarantee of safety.
    """
    if not isfinite(remaining_budget) or remaining_budget < 0:
        raise ValueError("remaining budget must be finite and >=0")
    if not 0 <= minimum_mean_reliability <= 1:
        raise ValueError("minimum reliability outside [0,1]")
    eligible = [p for p in proposals if p.cost <= remaining_budget and
                p.mean_reliability >= minimum_mean_reliability]
    if not eligible:
        return None
    scores = [(expected_hvi_per_cost(archive, p, samples, seed + i), i, p)
              for i, p in enumerate(eligible)]
    return max(scores, key=lambda t: (t[0], -t[1]))[2]
