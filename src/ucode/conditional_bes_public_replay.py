"""One-candidate history-conditioned BES on immutable SYNTHETIC public receipts.

A real integration of the pre-existing finite-horizon diagnostic planner
with the candidate-bound matched-session trace; NOT the full mixed
generate/retrieve/test/repair U-CODE agent, model inference, calibrated
predictor, or authenticated resource meter. There is NO evaluator input.
"""
from __future__ import annotations

from .action_id_replay_bridge import ActionBoundBook
from .adaptive_reference_replay import AdaptiveReferenceResult
from .conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalState,
    plan_conditional, record_conditional,
)
from .matched_opportunities import matched_opportunities, opportunity_digest
from .matched_session import SharedDecision, SharedSession, commit_shared
from .uncertainty_only_reference import SyntheticRiskRegister
from .vector_policy import DIAGNOSTICS, ResourcePrices, ResourceVector
from .voi import ReleaseRule

_STAGE = "SYNTHETIC_ONE_CANDIDATE_HISTORY_CONDITIONAL_BES_NOT_REAL_TREATMENT"


def run_conditional_bes_synthetic_reference(
    task_id: str,
    budget: ResourceVector,
    book: ActionBoundBook,
    confidence: SyntheticRiskRegister,
    kernel: ConditionalKernel,
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    horizon: int = 2,
    max_steps: int = 20,
    max_candidates: int = 8,
) -> AdaptiveReferenceResult:
    """End-to-end decision/replay loop for bounded *diagnostic-only* BES.

    First attempts ONE synthetic generate action; then BES selects
    candidate-specific diagnostics based on a frozen conditional likelihood
    table, visible history, and conservative five-dimensional reservations.
    This restricted reference deliberately has no repair or subsequent
    candidate generation and is NOT a faithful implementation of all
    preregistered U-CODE intervention actions.
    """
    if type(task_id) is not str or not task_id.startswith("SYNTHETIC_"):
        raise ValueError("only synthetic public-replay tasks are permitted")
    if not isinstance(budget, ResourceVector) or budget.is_free():
        raise TypeError("typed nonzero five-vector budget required")
    if not isinstance(book, ActionBoundBook):
        raise TypeError("typed immutable synthetic public response book required")
    if not isinstance(confidence, SyntheticRiskRegister):
        raise TypeError("frozen hypothetical confidence required")
    if not isinstance(kernel, ConditionalKernel) or not isinstance(
            prices, ResourcePrices) or not isinstance(rule, ReleaseRule):
        raise TypeError("frozen typed likelihood, prices, release policy required")
    if rule.unit_cost_penalty != 0:
        raise ValueError("planning prices must be charged exactly once")
    if abs(confidence.release_min_probability-(1-rule.max_predicted_failure))>1e-9:
        raise ValueError("confidence and planner release gates must agree")
    if type(horizon) is not int or not 1 <= horizon <= 4:
        raise ValueError("bounded conditional horizon 1..4 required")
    if type(max_steps) is not int or not 1 <= max_steps <= 32:
        raise ValueError("bounded policy trace steps 1..32 required")
    if type(max_candidates) is not int or not 1 <= max_candidates <= 8:
        raise ValueError("one-patch restricted reference uses archive cap 1..8")

    session = SharedSession.empty(budget,max_candidates=max_candidates)
    initial_digest = opportunity_digest(session,book.catalog)
    lookup = {row.key: row for row in book.responses}
    probes = tuple(ConditionalProbe(a.action_id,a.kind,a.cost)
                   for a in book.catalog if a.kind in DIAGNOSTICS)
    selected: list[str] = []

    def finish(status: str, released: str | None = None):
        return AdaptiveReferenceResult(
            status=status,
            policy_name="ucode_conditional_bes",
            response_book_sha256=book.digest_sha256,
            initial_opportunity_sha256=initial_digest,
            session=session,
            selected_action_ids=tuple(selected),
            released_candidate_sha256=released,
            stage=_STAGE,
        )

    for _ in range(max_steps):
        menu = matched_opportunities(session,book.catalog)
        if not session.state.candidates:
            if session.state.attempted:
                return finish("ABSTAINED")
            first=next((item for item in menu if item.kind=="generate"),None)
            if first is None:
                return finish("ABSTAINED")
            choice=first.as_decision()
        else:
            if len(session.state.candidates)!=1:
                return finish("UNSUPPORTED_MULTICANDIDATE_REFERENCE")
            candidate=session.state.candidates[0].sha256
            card=confidence.card(candidate)
            if card is None:
                return finish("FROZEN_BELIEF_PROFILE_MISSING")
            # Reconstruct beliefs using only the purchased PUBLIC diagnostic
            # observations. Costs are from reported receipts, not fabricated
            # conditional gold labels. Generator spending remains in session.
            inferred=ConditionalState(card.prior_acceptable,budget)
            try:
                for receipt in session.receipts:
                    if receipt.kind not in DIAGNOSTICS:
                        continue
                    if receipt.target_sha256 != candidate:
                        return finish("UNSUPPORTED_CROSS_CANDIDATE_EVIDENCE")
                    observed_probe=ConditionalProbe(
                        receipt.action_id,receipt.kind,receipt.reported_cost)
                    inferred=record_conditional(
                        inferred,observed_probe,kernel,receipt.visible_positive)
                state=ConditionalState(
                    inferred.prior,session.state.remaining,inferred.history)
                plan=plan_conditional(
                    state,probes,kernel,prices,rule,horizon=horizon)
            except (ValueError,TypeError):
                # Missing conditional likelihoods and impossible outcomes
                # MUST NOT silently fall back to independence.
                return finish("FROZEN_CONDITIONAL_MODEL_INCOMPLETE")
            if plan.action=="abstain":
                return finish("ABSTAINED")
            if plan.action=="release":
                return finish("RELEASED_PENDING_INDEPENDENT_EVALUATION",
                              candidate)
            matches=tuple(item for item in menu
                          if item.action_id==plan.action
                          and item.target==candidate
                          and item.kind in DIAGNOSTICS)
            if len(matches)!=1:
                return finish("PLANNED_PROBE_NOT_AVAILABLE_IN_SHARED_MENU")
            choice=matches[0].as_decision()

        if not isinstance(choice, SharedDecision):
            raise TypeError("planner must select typed shared decision")
        if choice not in tuple(item.as_decision() for item in menu):
            return finish("INVALID_OR_UNAVAILABLE_ACTION_TARGET")
        row=lookup.get((choice.action_id,choice.target_sha256))
        if row is None:
            return finish("FROZEN_PUBLIC_RESPONSE_MISSING")
        if row.kind!=choice.kind or row.reserved!=choice.reserved_cost:
            return finish("FROZEN_PUBLIC_RESPONSE_IDENTITY_MISMATCH")
        # All receipts are immutable hypothetical PUBLIC fixture outcomes;
        # never count this as independent truth or actual tool metering.
        session=commit_shared(
            session,book.catalog,choice,
            reported_cost=row.used,
            observed_positive=row.visible_positive,
            new_candidate_sha256=row.produced_sha256)
        selected.append(choice.action_id)
    return finish("MAX_STEPS_REACHED_WITHOUT_TERMINAL")
