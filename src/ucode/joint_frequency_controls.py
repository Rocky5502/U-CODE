"""Fair four-way same-proposal Pareto controls, SOURCE-ONLY integration.

Each candidate's three Bernoulli marginals MUST exactly match its frozen
train-only joint frequency forecast. This isolates (some) dependence-model
differences: fully independent, two-way robust with independent validity,
three-way robust, and categorical fitted-joint expected HVI all receive
the SAME candidate menu, cost vector, budget, support and reference point.

No model is fitted on evaluation data here. No code repair, secret oracle,
real hardware meter or successful outcome is inferred from these scores.
The fitted categorical frequency is a *minimal* joint baseline; a strong
context-sensitive trained joint predictor remains a required comparator.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .acquisition import ParetoPoint, hypervolume_2d
from .dependence_robust_acquisition import RobustParetoProposal
from .joint_frequency_fit import FrozenJointFrequency
from .joint_validity_acquisition import bound_joint_validity_hvi
from .vector_policy import ResourcePrices, ResourceVector

_ATOMS=tuple((r,s,v) for r in (0,1) for s in (0,1) for v in (0,1))
_POLICIES=(
    "fully_independent_expected",
    "two_way_dependence_robust_independent_validity",
    "three_way_dependence_robust",
    "train_only_joint_frequency_expected",
)
_TOL=1e-10


@dataclass(frozen=True)
class JointForecastCandidate:
    proposal: RobustParetoProposal
    forecast: FrozenJointFrequency


@dataclass(frozen=True)
class MatchedCandidateScores:
    action_id: str
    action: str
    gross_joint_expected: float
    gross_three_way_lower: float
    gross_three_way_upper: float
    scalar_cost: float
    net_fully_independent: float
    net_two_way_robust: float
    net_three_way_robust: float
    net_joint_frequency: float


@dataclass(frozen=True)
class MatchedJointComparison:
    candidate_scores: tuple[MatchedCandidateScores, ...]
    choices: tuple[tuple[str,str|None], ...]
    shared_resource_budget: ResourceVector
    source_model_id: str
    source_model_checkpoint_sha256: str
    source_labeling_protocol_id: str
    eligible_candidate_count: int
    status: str = "FOUR_SCORES_SAME_MARGINALS_SOURCE_ONLY_NOT_REAL_TASK"


def compare_same_marginal_joint_controllers(
    archive: Sequence[ParetoPoint],
    candidates: Sequence[JointForecastCandidate],
    remaining_budget: ResourceVector,
    unit_prices: ResourcePrices,
    reference: ParetoPoint = ParetoPoint(0,0),
) -> MatchedJointComparison:
    """A deterministic same-menu first-party policy-comparison *reference*.

    This function does not implement or impersonate the eight registered
    confirmatory agents. It does not call experimental code, hidden evaluators,
    trained network models, or real repository tasks.
    """
    if (not isinstance(remaining_budget,ResourceVector)
            or not isinstance(unit_prices,ResourcePrices)
            or not isinstance(reference,ParetoPoint)):
        raise TypeError("typed common budget, prices and reference required")
    points=tuple(archive)
    if len(points)>256 or any(not isinstance(x,ParetoPoint) for x in points):
        raise ValueError("at most 256 public Pareto points required")
    rows=tuple(candidates)
    if not rows or len(rows)>64:
        raise ValueError("bounded nonempty candidate menu required")
    if any(not isinstance(x,JointForecastCandidate)
           or not isinstance(x.proposal,RobustParetoProposal)
           or not isinstance(x.forecast,FrozenJointFrequency) for x in rows):
        raise TypeError("typed frozen-fit and proposal pairs required")
    ids=[x.proposal.action_id for x in rows]
    if len(set(ids))!=len(ids):
        raise ValueError("duplicate candidate action IDs")
    # Compare one model + one independent labeling protocol only; no
    # cross-checkpoint result or label-protocol pooling disguised as parity.
    models={x.forecast.model_id for x in rows}
    revisions={x.forecast.model_checkpoint_sha256 for x in rows}
    protocols={x.forecast.labeling_protocol_id for x in rows}
    if len(models)!=1 or len(revisions)!=1 or len(protocols)!=1:
        raise ValueError("cross-model or cross-label-protocol or checkpoint revision comparison forbidden")
    # All candidates with the same model/action/context must reference
    # the SAME frozen fit; otherwise implicit retraining per candidate
    # (possibly on a different label set) can confound the controls.
    fit_by_context={}
    for row in rows:
        f=row.forecast
        key=(f.action,f.public_context_bucket,f.labeling_protocol_id)
        previous=fit_by_context.setdefault(key,(
            f.training_fingerprint_sha256,f.smoothing_per_atom,f.masses))
        if previous!=(f.training_fingerprint_sha256,
                      f.smoothing_per_atom,f.masses):
            raise ValueError("inconsistent frozen joint fit within public context")
    for row in rows:
        p=row.proposal
        if p.action!=row.forecast.action:
            raise ValueError("frozen forecast action does not match proposed action")
        received=(p.reliability.probability_high,
                  p.safety.probability_high,p.probability_valid)
        expected=row.forecast.marginal_high()
        if any(abs(a-b)>_TOL for a,b in zip(received,expected)):
            raise ValueError("marginal mismatch: unfair joint versus independent control")
    baseline=hypervolume_2d(points,reference)
    scored=[]
    for row in sorted(rows,key=lambda x:x.proposal.action_id):
        p=row.proposal
        if not remaining_budget.affordable(p.cost):
            continue
        band=bound_joint_validity_hvi(points,p,unit_prices,reference)
        two_support_r=(p.reliability.low,p.reliability.high)
        two_support_s=(p.safety.low,p.safety.high)
        deltas=[
            0. if not v else max(0.,hypervolume_2d(
                (*points,ParetoPoint(two_support_r[r],two_support_s[s])),reference
            )-baseline)
            for r,s,v in _ATOMS
        ]
        fitted=sum(q*g for q,g in zip(row.forecast.masses,deltas))
        if (not isfinite(fitted) or
                fitted+_TOL<band.gross_hvi_range[0] or
                fitted>band.gross_hvi_range[1]+_TOL):
            raise AssertionError("fitted joint distribution violates sharp marginal bounds")
        c=band.scalar_cost
        scored.append(MatchedCandidateScores(
            p.action_id,p.action,fitted,band.gross_hvi_range[0],
            band.gross_hvi_range[1],c,
            band.fully_independent_gross_hvi-c,
            band.legacy_independent_validity_range[0]-c,
            band.gross_hvi_range[0]-c,fitted-c,
        ))
    score_fields=(
        "net_fully_independent", "net_two_way_robust",
        "net_three_way_robust","net_joint_frequency",
    )
    selections=[]
    for name,field in zip(_POLICIES,score_fields):
        # sorted order gives lexical action-ID tie breaks; STOP has value 0.
        best=max(scored,key=lambda x:getattr(x,field),default=None)
        chosen=(best.action_id if best is not None
                and getattr(best,field)>1e-12 else None)
        selections.append((name,chosen))
    return MatchedJointComparison(
        tuple(scored),tuple(selections),remaining_budget,
        next(iter(models)),next(iter(revisions)),
        next(iter(protocols)),len(scored),
    )
