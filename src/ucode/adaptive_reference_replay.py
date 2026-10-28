"""Adaptive, evaluator-blind SYNTHETIC replay for two reference policy choices.

Unlike a pre-scripted action trace, each policy selects its next action from
the same public matched opportunity menu after reading only public diagnostic
receipts. The resulting exact candidate-bound action receipts are consumed
from one immutable ActionBoundBook.

Only two scoped reference controls are implemented:
* 'fixed_testing': generate one patch, test it once, release only after
  one positive public test, otherwise abstain.
* 'no_uncertainty_search': existing bounded deterministic beam heuristic
  using public tests and fixed heuristic scores, not calibrated uncertainty.

Neither is a faithful reproduction of all eight confirmatory algorithms.
All input is first-party synthetic; no LLMs, repositories, hidden evaluators,
real meter or independently admitted tasks are executed.
"""
from __future__ import annotations

from dataclasses import dataclass

from .action_id_replay_bridge import ActionBoundBook
from .matched_opportunities import choose_matched_baseline, matched_opportunities, opportunity_digest
from .matched_session import SharedDecision, SharedSession, commit_shared
from .optimized_search import SearchPolicy
from .vector_policy import ResourceVector

_SCOPED = frozenset(("fixed_testing", "no_uncertainty_search"))
_STAGE = "SYNTHETIC_ADAPTIVE_TWO_REFERENCE_POLICIES_NOT_REAL_TRIAL"


@dataclass(frozen=True)
class AdaptiveReferenceResult:
    status: str
    policy_name: str
    response_book_sha256: str
    initial_opportunity_sha256: str
    session: SharedSession
    selected_action_ids: tuple[str, ...]
    released_candidate_sha256: str | None
    stage: str = _STAGE
    independent_oracle_labels: int = 0
    model_inferences: int = 0
    trusted_resource_meter: bool = False
    policy_fidelity_to_published_baselines: bool = False


def _fixed_testing(session: SharedSession, book: ActionBoundBook) -> SharedDecision:
    """One generated candidate, one bound public test, then terminal."""
    menu = matched_opportunities(session, book.catalog)
    none = ResourceVector()
    if not session.state.candidates:
        # Explicitly no repeated generation if a first attempt yielded no patch.
        if session.state.attempted:
            return SharedDecision("abstain", "abstain", None, none)
        generates = (o for o in menu if o.kind == "generate")
        first = next(generates, None)
        return (first.as_decision() if first is not None else
                SharedDecision("abstain", "abstain", None, none))
    target = session.state.candidates[0].sha256
    observations = tuple(o for o in session.state.observations
                         if o.candidate_sha256 == target and o.kind == "test")
    if observations:
        if all(o.positive for o in observations):
            return SharedDecision("release", "release", target, none)
        return SharedDecision("abstain", "abstain", None, none)
    tests = (o for o in menu if o.kind == "test" and o.target == target)
    test = next(tests, None)
    return (test.as_decision() if test is not None else
            SharedDecision("abstain", "abstain", None, none))


def run_adaptive_synthetic_reference(
    task_id: str,
    policy_name: str,
    initial_budget: ResourceVector,
    book: ActionBoundBook,
    *,
    baseline: SearchPolicy | None = None,
    max_steps: int = 20,
    max_candidates: int = 8,
) -> AdaptiveReferenceResult:
    """Select from live public menus; replay exactly frozen, synthetic receipts.

    Returns visible terminal/attrition status, NOT an evaluator verdict. A
    response that is absent or mismatched is never guessed or substituted.
    The preselected action-ID bridge remains useful for independently
    checking the resulting adaptive trace.
    """
    if type(task_id) is not str or not task_id.startswith("SYNTHETIC_"):
        raise ValueError("only explicitly SYNTHETIC tasks can enter offline replay")
    if policy_name not in _SCOPED or type(policy_name) is not str:
        raise ValueError("only two bounded reference policy names are implemented")
    if not isinstance(initial_budget, ResourceVector) or initial_budget.is_free():
        raise ValueError("typed nonzero five-resource cap required")
    if not isinstance(book, ActionBoundBook):
        raise TypeError("typed frozen public response book required")
    if type(max_steps) is not int or not 1 <= max_steps <= 32:
        raise ValueError("bounded max_steps must be 1..32")
    if type(max_candidates) is not int or not 1 <= max_candidates <= 32:
        raise ValueError("bounded candidate archive cap required")
    if baseline is not None and not isinstance(baseline, SearchPolicy):
        raise TypeError("bounded SearchPolicy required for the heuristic")
    policy = baseline if baseline is not None else SearchPolicy(max_candidates=max_candidates)
    if policy.max_candidates != max_candidates:
        raise ValueError("search configuration and session archive caps differ")

    session = SharedSession.empty(initial_budget, max_candidates=max_candidates)
    initial_digest = opportunity_digest(session, book.catalog)
    frozen = {row.key: row for row in book.responses}
    selected: list[str] = []

    def finish(status: str, released: str | None = None):
        return AdaptiveReferenceResult(
            status, policy_name, book.digest_sha256, initial_digest,
            session, tuple(selected), released,
        )

    for _ in range(max_steps):
        if policy_name == "fixed_testing":
            choice = _fixed_testing(session, book)
        else:
            choice = choose_matched_baseline(session, book.catalog, policy)
        if not isinstance(choice, SharedDecision):
            raise TypeError("offline selector must return a typed decision")
        if choice.terminal:
            if (choice.action_id != choice.kind or
                    choice.reserved_cost != ResourceVector()):
                return finish("INVALID_TERMINAL_ACTION")
            if choice.kind == "abstain":
                if choice.target_sha256 is not None:
                    return finish("INVALID_TERMINAL_ACTION")
                return finish("ABSTAINED")
            if choice.kind == "release":
                if choice.target_sha256 not in {
                    candidate.sha256 for candidate in session.state.candidates
                }:
                    return finish("INVALID_RELEASE_CANDIDATE")
                return finish("RELEASED_PENDING_INDEPENDENT_EVALUATION",
                              choice.target_sha256)
            return finish("INVALID_TERMINAL_ACTION")

        # Validate the chosen action against the *live* candidate-bound menu.
        available = tuple(o.as_decision()
                          for o in matched_opportunities(session, book.catalog))
        if choice not in available:
            return finish("INVALID_OR_UNAVAILABLE_ACTION_TARGET")
        row = frozen.get((choice.action_id, choice.target_sha256))
        if row is None:
            return finish("FROZEN_PUBLIC_RESPONSE_MISSING")
        if row.kind != choice.kind or row.reserved != choice.reserved_cost:
            return finish("FROZEN_PUBLIC_RESPONSE_IDENTITY_MISMATCH")
        session = commit_shared(
            session, book.catalog, choice,
            reported_cost=row.used,
            observed_positive=row.visible_positive,
            new_candidate_sha256=row.produced_sha256,
        )
        selected.append(choice.action_id)
    return finish("MAX_STEPS_REACHED_WITHOUT_TERMINAL")
