"""Policy-neutral, offline action-target menu for both U-CODE policies.

Only public candidate lineage, visible observations, single-use action IDs and
nominal five-resource reservations enter this module. Neither posterior nor
hidden evaluator outcomes are permitted. Symbolic keys are INTERNAL to bounded
planning; never commit them as actual candidate SHA identities.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Sequence

from .matched_session import SharedDecision, SharedSession, _common_catalog, commit_shared
from .optimized_search import (
    SearchAction, SearchPolicy, _KINDS, _observed, _quality, _release_candidate,
)
from .vector_policy import DIAGNOSTICS, GENERATORS, RESOURCE_FIELDS, ResourceVector


@dataclass(frozen=True)
class Opportunity:
    action_id: str
    kind: str
    target: object | None
    cost: ResourceVector

    @property
    def sort_key(self):
        return (self.action_id, _key(self.target))

    def as_decision(self) -> SharedDecision:
        if self.target is not None and not (
            isinstance(self.target, str) and len(self.target) == 64
            and all(c in "0123456789abcdef" for c in self.target)
        ):
            raise ValueError("symbolic target cannot become execution decision")
        return SharedDecision(self.action_id, self.kind, self.target, self.cost)


def _key(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return "r:" + value
    return "s:" + repr(value)


def _expand_keys(
    keys: tuple[object, ...], used: frozenset[str], budget: ResourceVector,
    max_candidates: int, catalog: tuple[SearchAction, ...],
) -> tuple[Opportunity, ...]:
    """Identical action/target feasibility for public and hypothetical states."""
    out = []
    for action in catalog:
        if action.action_id in used or not budget.affordable(action.cost):
            continue
        if action.kind in GENERATORS and len(keys) >= max_candidates:
            continue
        if action.kind == "generate":
            out.append(Opportunity(action.action_id, action.kind, None, action.cost))
        else:
            for key in keys:
                out.append(Opportunity(action.action_id, action.kind, key, action.cost))
    return tuple(sorted(out, key=lambda x: x.sort_key))


def matched_opportunities(
    session: SharedSession, actions: Sequence[SearchAction],
) -> tuple[Opportunity, ...]:
    if not isinstance(session, SharedSession):
        raise TypeError("typed shared session required")
    catalog = _common_catalog(actions)
    if not set(session.state.attempted).issubset({a.action_id for a in catalog}):
        raise ValueError("attempted action absent from frozen catalog")
    return _expand_keys(
        tuple(c.sha256 for c in session.state.candidates),
        frozenset(session.state.attempted), session.state.remaining,
        session.max_candidates, catalog,
    )


def opportunity_digest(session: SharedSession, actions: Sequence[SearchAction]) -> str:
    """Canonical PUBLIC menu digest: no confidence, kernel or oracle field."""
    menu = matched_opportunities(session, actions)
    def vector(v):
        return {field: getattr(v, field) for field in RESOURCE_FIELDS}
    payload = {
        "initial_budget": vector(session.initial_budget),
        "remaining": vector(session.state.remaining),
        "max_candidates": session.max_candidates,
        "archive": sorted(
            (c.sha256, c.created_by, c.parent_sha256)
            for c in session.state.candidates
        ),
        "attempted": sorted(session.state.attempted),
        "menu": [
            (o.action_id, o.kind, o.target, vector(o.cost)) for o in menu
        ],
    }
    return sha256(json.dumps(payload, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def choose_matched_baseline(
    session: SharedSession, actions: Sequence[SearchAction],
    policy: SearchPolicy,
) -> SharedDecision:
    """Target-aware uncertainty-FREE bounded beam over the common menu.

    Future candidate production is only an opportunity proxy, not an invented
    success probability or executable patch. The first selected opportunity
    always refers to a real candidate (or target-free generate).
    """
    if not isinstance(policy, SearchPolicy):
        raise TypeError("typed heuristic policy required")
    if session.max_candidates != policy.max_candidates:
        raise ValueError("baseline and session archive capacity mismatch")
    catalog = _common_catalog(actions)
    root = matched_opportunities(session, catalog)
    release = _release_candidate(session.state, policy)
    terminal = SharedDecision("release" if release else "abstain",
                              "release" if release else "abstain",
                              release, ResourceVector())
    if not root:
        return terminal

    # score, budget, used IDs, candidate keys, used types, first opportunity,
    # opportunity path. Future symbolic keys are never exposed to the executor.
    beam = [(0.0, session.state.remaining, frozenset(session.state.attempted),
             tuple(c.sha256 for c in session.state.candidates),
             frozenset(), None, ())]
    best_score, best_first, best_path = policy.continue_threshold, None, ()
    expanded = 0
    for depth in range(policy.depth):
        successors = []
        for score, budget, used, keys, types, first, path in beam:
            for opportunity in _expand_keys(
                keys, used, budget, session.max_candidates, catalog
            ):
                target = opportunity.target
                observed = (_observed(session.state, target)
                            if isinstance(target, str) and len(target) == 64 else ())
                failed = any(not o.positive for o in observed
                             if o.kind in ("test", "static_analysis"))
                has_test = any(o.kind == "test" for o in observed)
                bonus = (policy.repair_after_failure_bonus
                         if opportunity.kind == "repair" and failed else 0.0)
                if opportunity.kind == "test" and not has_test:
                    bonus += policy.first_test_bonus
                inc = (policy.action_rewards[_KINDS.index(opportunity.kind)]
                       + bonus
                       + (policy.diversity_bonus
                          if opportunity.kind not in types else 0.0)
                       - opportunity.cost.total_price(policy.resource_prices))
                new_score = score + inc
                new_first = opportunity if first is None else first
                new_path = path + (opportunity.sort_key,)
                expanded += 1
                if expanded > 10000:
                    raise ValueError("matched baseline beam state cap exceeded")
                if (new_score > best_score + 1e-10 or
                    (abs(new_score-best_score) <= 1e-10 and best_first is not None
                     and new_path < best_path)):
                    best_score, best_first, best_path = new_score, new_first, new_path
                new_keys = keys
                if opportunity.kind in GENERATORS:
                    # Symbolic availability only; no fabricated posterior.
                    new_keys += (("future", opportunity.action_id, depth,
                                  _key(target)),)
                successors.append((
                    new_score, budget.subtract(opportunity.cost),
                    used | {opportunity.action_id}, new_keys,
                    types | {opportunity.kind}, new_first, new_path,
                ))
        if not successors:
            break
        successors.sort(key=lambda x: (-x[0], x[6]))
        beam = successors[:policy.beam_width]
    return best_first.as_decision() if best_first is not None else terminal


def record_matched_baseline(
    session: SharedSession, actions: Sequence[SearchAction],
    policy: SearchPolicy, decision: SharedDecision, *,
    reported_cost: ResourceVector,
    observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
) -> SharedSession:
    if decision != choose_matched_baseline(session, actions, policy):
        raise ValueError("unselected matched-baseline decision")
    return commit_shared(
        session, actions, decision, reported_cost=reported_cost,
        observed_positive=observed_positive,
        new_candidate_sha256=new_candidate_sha256,
    )
