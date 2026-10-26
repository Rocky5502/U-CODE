"""Bounded, search-optimized, uncertainty-free coding-action reference.

A strongER comparator than fixed-schedule blind_search: deterministic
depth-limited beam search over tool opportunities, adaptive visible-diagnostic
feedback, candidate provenance/archive and five componentwise hard budgets.
Search scores are predeclared *heuristics*, not calibrated probabilities.
Future generated patches and test signs are UNKNOWN; the beam optimizes an
opportunity proxy, not expected correct software. This module never executes
repository code, inference, or a hidden evaluator oracle.

Not yet a fair END-TO-END comparison with one-candidate conditional BES:
the latter still needs a comparable archive and real action adapters.
"""
from dataclasses import dataclass, field
from math import isfinite
import re
from typing import Sequence

from .vector_policy import (
    DIAGNOSTICS, GENERATORS, RESOURCE_FIELDS, ResourcePrices, ResourceVector,
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_KINDS = ("generate", "repair", "test", "static_analysis", "retrieve")

def _digest(value: str) -> bool:
    return isinstance(value, str) and bool(_HASH.fullmatch(value))


@dataclass(frozen=True)
class SearchAction:
    action_id: str
    kind: str
    cost: ResourceVector

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("nonblank search action ID required")
        if self.action_id in ("release", "abstain"):
            raise ValueError("reserved terminal action ID")
        if self.kind not in DIAGNOSTICS | GENERATORS:
            raise ValueError("invalid search action kind")
        if not isinstance(self.cost, ResourceVector) or self.cost.is_free():
            raise ValueError("search action requires nonzero five-vector cost")


@dataclass(frozen=True)
class SearchCandidate:
    sha256: str
    created_by: str
    parent_sha256: str | None = None

    def __post_init__(self):
        if not _digest(self.sha256):
            raise ValueError("candidate requires SHA256 identity")
        if not isinstance(self.created_by, str) or not self.created_by:
            raise ValueError("candidate creation action required")
        if self.parent_sha256 is not None and not _digest(self.parent_sha256):
            raise ValueError("candidate parent requires SHA256 identity")
        if self.parent_sha256 == self.sha256:
            raise ValueError("candidate cannot be its own parent")


@dataclass(frozen=True)
class SearchObservation:
    action_id: str
    candidate_sha256: str
    kind: str
    positive: bool

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id:
            raise ValueError("diagnostic action ID required")
        if not _digest(self.candidate_sha256):
            raise ValueError("observation must bind SHA256 candidate")
        if self.kind not in DIAGNOSTICS or type(self.positive) is not bool:
            raise ValueError("typed visible diagnostic required")


@dataclass(frozen=True)
class SearchState:
    remaining: ResourceVector
    candidates: tuple[SearchCandidate, ...] = ()
    active_sha256: str | None = None
    attempted: tuple[str, ...] = ()
    observations: tuple[SearchObservation, ...] = ()

    def __post_init__(self):
        if not isinstance(self.remaining, ResourceVector):
            raise ValueError("five-resource budget required")
        if not isinstance(self.candidates, tuple) or not all(
            isinstance(c, SearchCandidate) for c in self.candidates
        ):
            raise ValueError("candidate archive must be immutable and typed")
        identities = [c.sha256 for c in self.candidates]
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate candidate artifact")
        if self.active_sha256 is not None and self.active_sha256 not in identities:
            raise ValueError("active candidate not in archive")
        if self.candidates and self.active_sha256 is None:
            raise ValueError("nonempty archive requires active candidate")
        if not isinstance(self.attempted, tuple) or any(
            not isinstance(x, str) or not x for x in self.attempted
        ) or len(set(self.attempted)) != len(self.attempted):
            raise ValueError("attempted action identifiers must be unique")
        if not isinstance(self.observations, tuple) or not all(
            isinstance(o, SearchObservation) for o in self.observations
        ):
            raise ValueError("visible evidence must be immutable and typed")
        if len({o.action_id for o in self.observations}) != len(self.observations):
            raise ValueError("diagnostic action can produce one recorded observation")
        seen = set()
        creators = set()
        creation_steps = {}
        attempted_steps = {aid: step for step, aid in enumerate(self.attempted)}
        for candidate in self.candidates:
            parent = candidate.parent_sha256
            if parent is not None and parent not in seen:
                raise ValueError("candidate parent must precede descendant")
            if candidate.created_by != "initial":
                if candidate.created_by not in attempted_steps:
                    raise ValueError("candidate must originate from attempted action")
                if candidate.created_by in creators:
                    raise ValueError("single-use generating action cannot create two artifacts")
                if parent is not None and (
                    attempted_steps[candidate.created_by] <= creation_steps[parent]
                ):
                    raise ValueError("child repair cannot precede parent creation")
                creators.add(candidate.created_by)
                creation_steps[candidate.sha256] = attempted_steps[candidate.created_by]
            else:
                creation_steps[candidate.sha256] = -1
            seen.add(candidate.sha256)
        observation_steps = []
        for obs in self.observations:
            if obs.action_id not in attempted_steps or obs.candidate_sha256 not in seen:
                raise ValueError("observation cannot refer to unseen action or patch")
            step = attempted_steps[obs.action_id]
            if step <= creation_steps[obs.candidate_sha256]:
                raise ValueError("diagnostic observation predates candidate creation")
            observation_steps.append(step)
        if observation_steps != sorted(observation_steps):
            raise ValueError("visible diagnostic sequence violates attempt chronology")


@dataclass(frozen=True)
class SearchPolicy:
    """Train-tunable fixed heuristic, NOT model confidence or gold supervision.

    Scores describe desirable *opportunities*. Resource prices affect ranking,
    never override componentwise feasibility. Freeze configuration on TRAIN.
    """
    depth: int = 3
    beam_width: int = 16
    max_candidates: int = 8
    min_positive_tests: int = 1
    action_rewards: tuple[float, ...] = (3.0, 3.0, 4.0, 2.0, 1.0)
    repair_after_failure_bonus: float = 3.0
    first_test_bonus: float = 2.0
    diversity_bonus: float = 0.3
    continue_threshold: float = 0.0
    resource_prices: ResourcePrices = field(default_factory=ResourcePrices)

    def __post_init__(self):
        for name, lo, hi in (("depth", 1, 4), ("beam_width", 1, 64),
                             ("max_candidates", 1, 32),
                             ("min_positive_tests", 1, 32)):
            value = getattr(self, name)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(name + " outside bounded positive integer range")
        if not isinstance(self.action_rewards, tuple) or len(self.action_rewards) != 5:
            raise ValueError("exactly five ordered action reward weights required")
        for v in self.action_rewards + (
            self.repair_after_failure_bonus, self.first_test_bonus,
            self.diversity_bonus, self.continue_threshold,
        ):
            if type(v) not in (float, int) or not isfinite(v) or v < 0:
                raise ValueError("heuristic weights must be finite nonnegative")
        if not isinstance(self.resource_prices, ResourcePrices):
            raise ValueError("five-component resource prices required")


@dataclass(frozen=True)
class SearchDecision:
    action: str
    kind: str
    candidate_sha256: str | None
    budget_after_first: ResourceVector
    proxy_score: float
    states_expanded: int
    explanation: str

    @property
    def terminal(self) -> bool:
        return self.kind in ("release", "abstain")


def _catalog(actions: Sequence[SearchAction]) -> tuple[SearchAction, ...]:
    items = tuple(actions)
    if len(items) > 16 or any(not isinstance(a, SearchAction) for a in items):
        raise ValueError("search catalog requires up to sixteen typed actions")
    if len({a.action_id for a in items}) != len(items):
        raise ValueError("duplicate action IDs")
    return tuple(sorted(items, key=lambda a: a.action_id))


def _validate_catalog_state(state: SearchState, actions: tuple[SearchAction, ...]):
    index = {a.action_id: a for a in actions}
    if any(a not in index for a in state.attempted):
        raise ValueError("previously attempted action absent from frozen catalog")
    for c in state.candidates:
        if c.created_by == "initial":
            if c.parent_sha256 is not None:
                raise ValueError("initial candidate cannot have repair parent")
        elif index[c.created_by].kind not in GENERATORS:
            raise ValueError("candidate origin must be generate or repair")
        elif (c.parent_sha256 is None) != (index[c.created_by].kind == "generate"):
            raise ValueError("generation and repair provenance mismatch")
    for o in state.observations:
        if index[o.action_id].kind != o.kind:
            raise ValueError("diagnostic type mismatches frozen catalog")


def _observed(state: SearchState, sha: str) -> tuple[SearchObservation, ...]:
    return tuple(o for o in state.observations if o.candidate_sha256 == sha)


def _quality(state: SearchState, sha: str) -> tuple[int, int, int, str]:
    obs = _observed(state, sha)
    tests = [o for o in obs if o.kind == "test"]
    # Discrete, observed evidence ONLY: not an estimate of probability correct.
    score = (4 * sum(o.positive for o in tests)
             - 6 * sum(not o.positive for o in tests)
             + sum(o.positive for o in obs if o.kind == "static_analysis")
             - 2 * sum(not o.positive for o in obs if o.kind == "static_analysis"))
    return (score, sum(o.positive for o in tests),
            -sum(not o.positive for o in tests), sha)


def _release_candidate(state: SearchState, policy: SearchPolicy) -> str | None:
    eligible = []
    for candidate in state.candidates:
        obs = _observed(state, candidate.sha256)
        tests = [o for o in obs if o.kind == "test"]
        if sum(o.positive for o in tests) < policy.min_positive_tests:
            continue
        if any(not o.positive for o in obs if o.kind in ("test", "static_analysis")):
            continue
        eligible.append(candidate.sha256)
    return max(eligible, key=lambda sha: _quality(state, sha)) if eligible else None


def _pick_target(state: SearchState) -> str | None:
    if not state.candidates:
        return None
    return max((c.sha256 for c in state.candidates),
               key=lambda sha: _quality(state, sha))


def _beam_schedule(state: SearchState, actions: tuple[SearchAction, ...],
                   policy: SearchPolicy, target_sha: str | None):
    """Search action sequences, NOT imagined test outcomes or correctness.

    Future generation is a conditional *potential* for a candidate; if the
    real tool produces none, record_search leaves the archive unchanged and
    the policy replans. This planning approximation is explicit.
    """
    attempted = frozenset(state.attempted)
    target_observations = _observed(state, target_sha) if target_sha else ()
    seen_test = any(o.kind == "test" for o in target_observations)
    failed = any(not o.positive for o in target_observations
                 if o.kind in ("test", "static_analysis"))
    # tuple: (score, budget, used IDs, possible candidate, possible archive size,
    #         planned actions, types chosen, test opportunity)
    beam = [(0.0, state.remaining, attempted, bool(state.candidates),
             len(state.candidates), (), frozenset(), seen_test)]
    best = None
    expanded = 0
    for _ in range(policy.depth):
        successors = []
        for score, remaining, used, exists, size, path, types, has_test in beam:
            for a in actions:
                if a.action_id in used or not remaining.affordable(a.cost):
                    continue
                if a.kind != "generate" and not exists:
                    continue
                if a.kind in GENERATORS and size >= policy.max_candidates:
                    continue
                new_types = types | {a.kind}
                bonus = (policy.repair_after_failure_bonus
                         if a.kind == "repair" and failed and not path else 0.0)
                if a.kind == "test" and not has_test:
                    bonus += policy.first_test_bonus
                increment = (policy.action_rewards[_KINDS.index(a.kind)]
                             + bonus
                             + (policy.diversity_bonus if a.kind not in types else 0)
                             - a.cost.total_price(policy.resource_prices))
                new_path = path + (a.action_id,)
                new_score = score + increment
                expanded += 1
                if expanded > 10000:
                    raise ValueError("beam search state cap exceeded")
                result = (new_score, remaining.subtract(a.cost),
                          used | {a.action_id}, exists or a.kind in GENERATORS,
                          size + (a.kind in GENERATORS), new_path, new_types,
                          has_test or a.kind == "test")
                successors.append(result)
                candidate = (new_score, new_path)
                if best is None or candidate[0] > best[0] + 1e-10 or (
                    abs(candidate[0]-best[0]) <= 1e-10 and candidate[1] < best[1]):
                    best = candidate
        if not successors:
            break
        # Beam approximation: proxy score only, stable action-ID tie breaking.
        successors.sort(key=lambda s: (-s[0], s[5]))
        beam = successors[:policy.beam_width]
    return best, expanded


def choose_search(
    state: SearchState, actions: Sequence[SearchAction],
    policy: SearchPolicy = SearchPolicy(),
) -> SearchDecision:
    """Budget-safe adaptive search using visible evidence, never calibrated risk."""
    if not isinstance(state, SearchState) or not isinstance(policy, SearchPolicy):
        raise TypeError("typed search state and policy required")
    catalog = _catalog(actions)
    _validate_catalog_state(state, catalog)
    target = _pick_target(state)
    best, expanded = _beam_schedule(state, catalog, policy, target)
    ready = _release_candidate(state, policy)
    if best is None or best[0] <= policy.continue_threshold + 1e-10:
        terminal = "release" if ready is not None else "abstain"
        return SearchDecision(terminal, terminal, ready, state.remaining, 0.0,
                              expanded, "visible test release gate or no positive proxy plan")
    selected = next(a for a in catalog if a.action_id == best[1][0])
    return SearchDecision(
        selected.action_id, selected.kind, target if target else None,
        state.remaining.subtract(selected.cost), best[0], expanded,
        "deterministic bounded beam search on public tool opportunity heuristic",
    )


def record_search(
    state: SearchState, actions: Sequence[SearchAction], decision: SearchDecision,
    *, observed_positive: bool | None = None,
    new_candidate_sha256: str | None = None,
    policy: SearchPolicy = SearchPolicy(),
) -> SearchState:
    """Record one selected action; never accept a self-reported gold outcome.

    A candidate-producing tool may return None (failed/invalid generation),
    but still consumes its predeclared budget. Actual measured costs must
    be independently enforced by the external runner/evaluator contract.
    """
    if not isinstance(decision, SearchDecision) or decision.terminal or (
        decision != choose_search(state, actions, policy)
    ):
        raise ValueError("unselected, altered, or terminal search action")
    catalog = _catalog(actions)
    chosen = next(a for a in catalog if a.action_id == decision.action)
    target = decision.candidate_sha256
    archive, observations, active = (state.candidates, state.observations,
                                    state.active_sha256)
    if chosen.kind in DIAGNOSTICS:
        if type(observed_positive) is not bool or new_candidate_sha256 is not None:
            raise ValueError("diagnostic requires only visible boolean evidence")
        if target is None:
            raise ValueError("cannot run diagnostics without a candidate")
        observations += (SearchObservation(chosen.action_id, target,
                                            chosen.kind, observed_positive),)
        active = target
    else:
        if observed_positive is not None:
            raise ValueError("candidate generation must not carry oracle outcomes")
        if new_candidate_sha256 is not None:
            if not _digest(new_candidate_sha256):
                raise ValueError("new candidate must be SHA256")
            if any(c.sha256 == new_candidate_sha256 for c in archive):
                raise ValueError("duplicate/replayed candidate SHA256")
            if chosen.kind == "repair" and target is None:
                raise ValueError("repair needs existing candidate parent")
            archive += (SearchCandidate(new_candidate_sha256, chosen.action_id,
                                        target if chosen.kind == "repair" else None),)
            active = new_candidate_sha256
        elif chosen.kind == "repair" and target is None:
            raise ValueError("repair needs existing candidate parent")
    return SearchState(decision.budget_after_first, archive, active,
                       state.attempted + (chosen.action_id,), observations)


def search_catalog_from_public_manifest(payload: list[dict]) -> tuple[SearchAction, ...]:
    """Strict allowlist prevents accidental forecast/gold/PR-answer exposure."""
    if not isinstance(payload, list):
        raise ValueError("action inventory must be a list")
    result = []
    for row in payload:
        if not isinstance(row, dict) or set(row) != {"action_id", "kind", "cost"}:
            raise ValueError("unknown action fields or potential oracle/forecast leakage")
        cost = row["cost"]
        if not isinstance(cost, dict) or set(cost) != set(RESOURCE_FIELDS):
            raise ValueError("all five budget components required")
        result.append(SearchAction(row["action_id"], row["kind"], ResourceVector(**cost)))
    return _catalog(result)
