"""Finite-horizon observational equivalence audit for MCEA hypotheses.

The question is whether any feasible *adaptive diagnostic policy* can
distinguish two latent (evidence model, candidate acceptability) atoms from
the currently visible history. An action may be performed once globally.
This is model-relative observability, NOT a task oracle or a statistical
certificate about the true world.

For a pair (theta_i,Y_i),(theta_j,Y_j), if EVERY feasible action has
identical predictive distributions at each reachable public history,
the posterior ODDS of the pair never change under ANY policy using
only those actions, within the given horizon and hard resource cap.
The proof is direct Bayes likelihood-ratio cancellation, inductively
over public outcomes. It does not say the total posterior probability
of either atom stays constant when other atoms are present.

Only first-party frozen numeric likelihoods are read. No external
source, code, LLM, oracle, image or network action executes.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from .coherent_hypothesis_search import (
    CoherentBeliefState, EvidenceHypothesis, _aligned_models,
)
from .conditional_bes import ConditionalProbe, Observation
from .vector_policy import ResourceVector

_MAX_ACTIONS = 6


@dataclass(frozen=True)
class ObservationalEquivalenceAudit:
    left_atom: tuple[str, bool]
    right_atom: tuple[str, bool]
    indistinguishable: bool
    horizon: int
    context_count: int
    witness_action_id: str | None
    witness_history: tuple[Observation, ...] | None
    witness_positive_likelihoods: tuple[float, float] | None
    interpretation: str = "FINITE_FROZEN_DIAGNOSTIC_OBSERVABILITY_NOT_REAL_TASK_EVIDENCE"
    admitted_real_tasks: int = 0


def audit_latent_atom_observability(
    state: CoherentBeliefState,
    probes: Sequence[ConditionalProbe],
    hypotheses: Sequence[EvidenceHypothesis],
    left: tuple[str, bool],
    right: tuple[str, bool],
    *,
    horizon: int = 2,
    max_contexts: int = 10000,
) -> ObservationalEquivalenceAudit:
    """Exhaust the bounded public observation tree for a latent-atom pair.

    A positive audit requires STRICT equal numeric likelihoods at every
    reachable action/history, not an arbitrary floating tolerance.
    The two hypothetical atoms must have strictly positive posterior
    support now. They may have opposite correctness labels.

    A witness points to the first feasible diagnostic with different
    P(positive | theta,Y,history); the prefix history is reachable
    under BOTH atoms. Neither the witness nor a positive certificate
    uses an evaluator-only label from a real coding task.
    """
    if not isinstance(state, CoherentBeliefState):
        raise TypeError("typed frozen belief state required")
    models = _aligned_models(state, hypotheses)
    if type(horizon) is not int or not 0 <= horizon <= 4:
        raise ValueError("finite observability horizon must be 0..4")
    if type(max_contexts) is not int or not 1 <= max_contexts <= 100000:
        raise ValueError("positive bounded context budget required")
    if (type(left) is not tuple or type(right) is not tuple
            or len(left) != 2 or len(right) != 2
            or type(left[0]) is not str or type(right[0]) is not str
            or type(left[1]) is not bool or type(right[1]) is not bool
            or left == right):
        raise ValueError("distinct typed latent atom identities required")
    ids = state.scenario_ids
    if left[0] not in ids or right[0] not in ids:
        raise ValueError("latent atom scenario absent from frozen belief")
    li, ri = ids.index(left[0]), ids.index(right[0])
    if (state.joint[li][int(left[1])] <= 0
            or state.joint[ri][int(right[1])] <= 0):
        raise ValueError("both latent atoms require positive current posterior support")
    actions = tuple(probes)
    if (len(actions) > _MAX_ACTIONS
            or any(not isinstance(a, ConditionalProbe) for a in actions)):
        raise ValueError("at most six typed diagnostic actions supported")
    labels = [a.action_id for a in actions]
    if len(labels) != len(set(labels)):
        raise ValueError("globally duplicate diagnostic IDs")
    actions = tuple(sorted(actions, key=lambda x:x.action_id))
    seen_count = [0]

    def probability(action, history, model_idx, label):
        row = models[model_idx].get(action.action_id, history)
        return (row.positive_if_acceptable if label
                else row.positive_if_unacceptable)

    @lru_cache(maxsize=None)
    def visit(history: tuple[Observation, ...], budget: ResourceVector,
              remaining: int):
        seen_count[0] += 1
        if seen_count[0] > max_contexts:
            raise ValueError("finite observability context cap exceeded")
        if not remaining:
            return None
        consumed = {o.action_id for o in history}
        for action in actions:
            if action.action_id in consumed or not budget.affordable(action.cost):
                continue
            p_left = probability(action, history, li, left[1])
            p_right = probability(action, history, ri, right[1])
            # Exact comparison of frozen represented probabilities:
            # no epsilon relaxation that could certify distinct models.
            if p_left != p_right:
                return action.action_id, history, (p_left, p_right)
            future_budget = budget.subtract(action.cost)
            for positive in (False, True):
                # Because probabilities are equal, any nonzero outcome
                # is reachable for both atoms, preserving equal odds.
                if (p_left if positive else 1-p_left) == 0:
                    continue
                witness = visit(
                    history + (Observation(action.action_id, positive),),
                    future_budget, remaining-1,
                )
                if witness is not None:
                    return witness
        return None

    witness = visit(state.history, state.budget, horizon)
    return ObservationalEquivalenceAudit(
        left_atom=left, right_atom=right,
        indistinguishable=witness is None,
        horizon=horizon, context_count=seen_count[0],
        witness_action_id=None if witness is None else witness[0],
        witness_history=None if witness is None else witness[1],
        witness_positive_likelihoods=None if witness is None else witness[2],
    )
