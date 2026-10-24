"""Closed-loop, oracle-blind observation adapter for Bounded Evidence Search.

Call BES with current visible belief and budget, execute the chosen action
ONLY in an independently authorized sandbox, then pass a visible result here.
This module itself does not execute, download, search a repository, or inspect
any hidden/oracle label. External producers of probabilities need audit.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .budgeted_belief_search import (
    CandidateAction, EvidenceAction, BeliefPlan,
    plan_bounded_evidence_search,
)
from .vector_policy import ResourcePrices, ResourceVector
from .voi import ReleaseRule


@dataclass(frozen=True)
class VisibleEvent:
    action_id: str
    kind: str
    outcome: str
    belief_after: float | None


@dataclass(frozen=True)
class BeliefSession:
    prior: float | None
    remaining: ResourceVector
    events: tuple[VisibleEvent, ...] = ()
    terminal: str | None = None

    def __post_init__(self):
        if self.prior is not None and (
            type(self.prior) not in (float, int)
            or not isfinite(self.prior)
            or not 0 <= self.prior <= 1
        ):
            raise ValueError("session prior must be a numeric probability")
        if self.terminal not in (None, "release", "abstain"):
            raise ValueError("invalid terminal status")
        ids = [e.action_id for e in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("an action cannot be purchased twice in a session")


def _admissible(state: BeliefSession, action) -> None:
    if state.terminal is not None:
        raise ValueError("session already finalized")
    if action.action_id in (e.action_id for e in state.events):
        raise ValueError("action already consumed in this session")
    if not state.remaining.affordable(action.cost):
        raise ValueError("action not feasible in every resource dimension")
    if state.prior is None and (
        isinstance(action, EvidenceAction) or action.kind == "repair"
    ):
        raise ValueError("cannot inspect or repair an absent candidate")


def record_evidence(
    state: BeliefSession,
    action: EvidenceAction,
    observed_positive: bool,
) -> BeliefSession:
    """Bayes update on a *visible* diagnostic with frozen likelihoods.

    A zero-likelihood reported outcome is a model contradiction, not license
    to make up a posterior or silently change the oracle label.
    """
    if not isinstance(action, EvidenceAction):
        raise TypeError("record_evidence requires a diagnostic")
    _admissible(state, action)
    if type(observed_positive) is not bool:
        raise ValueError("visible diagnostic result must be boolean")
    p = state.prior
    prob_pos = p * action.sensitivity + (1 - p) * (1 - action.specificity)
    prob_neg = 1 - prob_pos
    if observed_positive:
        if prob_pos <= 0:
            raise ValueError("observed impossible positive outcome under frozen model")
        updated = p * action.sensitivity / prob_pos
    else:
        if prob_neg <= 0:
            raise ValueError("observed impossible negative outcome under frozen model")
        updated = p * (1 - action.sensitivity) / prob_neg
    updated = min(1.0, max(0.0, updated))
    event = VisibleEvent(
        action.action_id, action.kind,
        "diagnostic_positive" if observed_positive else "diagnostic_negative",
        updated,
    )
    return BeliefSession(updated, state.remaining.subtract(action.cost),
                         state.events + (event,))


def record_candidate(
    state: BeliefSession,
    action: CandidateAction,
    observed_new_prior: float | None,
) -> BeliefSession:
    """Receive a post-generation *pre-evaluator* success-risk forecast.

    The observed prior must belong to a nonzero-probability forecast support
    branch; the method does not allow hidden oracle outcomes as its payload.
    Passing None represents no usable patch and preserves the prior candidate.
    """
    if not isinstance(action, CandidateAction):
        raise TypeError("record_candidate requires a generative action")
    _admissible(state, action)
    if observed_new_prior is not None and (
        type(observed_new_prior) not in (float, int)
        or not isfinite(observed_new_prior)
        or not 0 <= observed_new_prior <= 1
    ):
        raise ValueError("new model predicted acceptability must be finite in [0,1]")
    if not any(
        s.probability > 0 and (
            (s.new_prior is None and observed_new_prior is None)
            or (s.new_prior is not None and observed_new_prior is not None
                and abs(s.new_prior - observed_new_prior) <= 1e-12)
        )
        for s in action.scenarios
    ):
        raise ValueError("observed generated-state forecast not in frozen scenario support")
    next_p = state.prior if observed_new_prior is None else float(observed_new_prior)
    event = VisibleEvent(
        action.action_id, action.kind,
        "no_usable_candidate" if observed_new_prior is None else "candidate_forecast",
        next_p,
    )
    return BeliefSession(next_p, state.remaining.subtract(action.cost),
                         state.events + (event,))


def plan_session(
    state: BeliefSession,
    forecasts: Sequence[EvidenceAction | CandidateAction],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    horizon: int = 2,
    assume_independent_diagnostics: bool = False,
    max_states: int = 30000,
) -> BeliefPlan:
    """Plan only over unused pre-outcome forecasts, no hidden oracle access."""
    if state.terminal is not None:
        raise ValueError("session already finalized")
    spent = {e.action_id for e in state.events}
    return plan_bounded_evidence_search(
        state.prior, [a for a in forecasts if a.action_id not in spent],
        state.remaining, prices, rule, horizon,
        assume_independent_diagnostics=assume_independent_diagnostics,
        max_states=max_states,
    )


def finalize_session(
    state: BeliefSession,
    decision: str,
    release_rule: ReleaseRule,
) -> BeliefSession:
    """Lock a release/abstention decision; not an evaluator correctness label."""
    from .voi import terminal_value

    if state.terminal is not None:
        raise ValueError("session already finalized")
    if decision not in ("release", "abstain"):
        raise ValueError("terminal action must release or abstain")
    if decision == "release" and (
        state.prior is None or terminal_value(state.prior, release_rule) <= 0
    ):
        raise ValueError("release fails frozen predicted-risk/utility rule")
    return BeliefSession(state.prior, state.remaining, state.events, decision)
