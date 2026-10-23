"""Pluggable agent orchestration; external execution must be sandboxed.

The runner never executes generated code, imports third-party repos, or exposes
secrets to the LLM. Supply a separately isolated verifier for actual experiments.
"""
from dataclasses import dataclass
from typing import Callable, Sequence

from .search import ActionEstimate, SearchState, choose_action


@dataclass(frozen=True)
class Verification:
    passed: bool
    summary: str
    oracle_id: str


@dataclass(frozen=True)
class AgentTrace:
    step: int
    action: str
    cost: float
    remaining_budget: float
    verifier_passed: bool | None


@dataclass(frozen=True)
class AgentRun:
    status: str
    patch: str | None
    trace: tuple[AgentTrace, ...]
    total_spent: float


class AgentRunner:
    """A bounded generator/retriever/verifier controller with explicit abstention.

    generator(task, prior_patch, feedback) -> candidate patch string
    verifier(candidate_patch) -> Verification (run out of process in a sandbox)
    risk_model(candidate_patch | None, public_evidence) -> P(failure)
    estimates(state, last_verification) -> action proposals using PRE-OUTCOME data
    """

    def __init__(
        self,
        generator: Callable[[str, str | None, str], str],
        verifier: Callable[[str], Verification],
        risk_model: Callable[[str | None, str], float],
        estimates: Callable[[SearchState, Verification | None], Sequence[ActionEstimate]],
        retriever: Callable[[str], str] | None = None,
    ) -> None:
        self.generator = generator
        self.verifier = verifier
        self.risk_model = risk_model
        self.estimates = estimates
        self.retriever = retriever

    def run(self, task: str, budget: float = 20, max_steps: int = 20,
            policy: str = "uncertainty_pareto", seed: int = 0) -> AgentRun:
        if budget < 0 or max_steps < 0:
            raise ValueError("invalid budget or max_steps")
        patch = None
        evidence = ""
        previous_verification = None
        history: list[AgentTrace] = []
        remaining = float(budget)
        for index in range(max_steps):
            state = SearchState(
                remaining_budget=remaining,
                predicted_failure_risk=self.risk_model(patch, evidence),
                has_candidate=patch is not None,
                evidence_count=len(history),
            )
            action = choose_action(state, list(self.estimates(state, previous_verification)),
                                   policy, seed + index)
            if action.action == "abstain":
                break
            remaining -= action.cost
            outcome = None
            if action.action in ("generate", "repair"):
                patch = self.generator(task, patch, evidence)
                if not isinstance(patch, str) or not patch.strip():
                    raise ValueError("generator must provide a nonempty patch")
                previous_verification = None
            elif action.action == "retrieve":
                if self.retriever is None:
                    raise ValueError("retrieve selected but no retriever provided")
                evidence = self.retriever(task)
            elif action.action in ("test", "static_analysis"):
                if patch is None:
                    raise ValueError("verifier selected without a candidate")
                previous_verification = self.verifier(patch)
                outcome = previous_verification.passed
                evidence = previous_verification.summary
            history.append(AgentTrace(index, action.action, action.cost, remaining, outcome))
            if outcome is True:
                return AgentRun("verified_by_provided_oracle", patch,
                                tuple(history), budget - remaining)
        return AgentRun("abstained_or_budget_exhausted", patch,
                        tuple(history), budget - remaining)
