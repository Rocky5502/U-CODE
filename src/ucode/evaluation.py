"""Evaluator-only, paired, cluster-aware outcome accounting.

This module MUST be used only AFTER the frozen coding policy terminates.
Do not import evaluator-only outcomes into generation, retrieval, diagnostic
training or decision-selection code. No independent benchmark is run here.
"""
from dataclasses import dataclass
from math import isfinite
from random import Random
from typing import Sequence


@dataclass(frozen=True)
class EvaluationOutcome:
    task_id: str
    lineage_group: str
    model_id: str
    seed: int
    budget_id: str
    policy: str
    released: bool
    oracle_passed: bool | None

    def __post_init__(self):
        for name in ("task_id", "lineage_group", "model_id", "budget_id", "policy"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"{name} cannot be empty")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        if type(self.released) is not bool:
            raise ValueError("released must be boolean")
        if self.released:
            if type(self.oracle_passed) is not bool:
                raise ValueError("released patch requires boolean independent oracle label")
        elif self.oracle_passed is not None:
            raise ValueError("abstention has no released patch to score")

    @property
    def verified_success(self) -> int:
        return int(self.released and self.oracle_passed is True)

    @property
    def key(self) -> tuple[str, str, int, str]:
        return self.task_id, self.model_id, self.seed, self.budget_id


@dataclass(frozen=True)
class PolicyMeasures:
    attempts: int
    successes: int
    releases: int
    erroneous_releases: int
    full_task_success: float
    coverage: float
    wrong_release_risk: float | None


@dataclass(frozen=True)
class PairedDifference:
    pairs: int
    lineage_groups: int
    positive_discordant: int
    negative_discordant: int
    effect_success_difference: float
    cluster_bootstrap_ci_95: tuple[float, float] | None


def measure_policy(outcomes: Sequence[EvaluationOutcome]) -> PolicyMeasures:
    """Abstention counts in denominator but is not independently scored."""
    if not outcomes:
        raise ValueError("no evaluator outcomes")
    if len({(o.key, o.policy) for o in outcomes}) != len(outcomes):
        raise ValueError("duplicate policy/task/model/seed/budget evaluation")
    if len({o.policy for o in outcomes}) != 1:
        raise ValueError("measure one policy at a time")
    n = len(outcomes)
    s = sum(o.verified_success for o in outcomes)
    released = sum(o.released for o in outcomes)
    wrong = sum(int(o.released and o.oracle_passed is False) for o in outcomes)
    return PolicyMeasures(n, s, released, wrong, s / n, released / n,
                          (wrong / released) if released else None)


def paired_verified_success(
    outcomes: Sequence[EvaluationOutcome],
    treatment_policy: str,
    control_policy: str,
    bootstrap_samples: int = 1000,
    seed: int = 2026,
) -> PairedDifference:
    """Strictly match same task, model, seed and budget across two policies.

    Cluster bootstrap samples independent repository/fork lineages, keeping
    all constituent task/seed pairs. This interval is a descriptive
    uncertainty estimator, NOT a guarantee under repository shift.
    """
    if treatment_policy == control_policy or not treatment_policy or not control_policy:
        raise ValueError("two distinct named policies required")
    if not isinstance(bootstrap_samples, int) or bootstrap_samples < 0:
        raise ValueError("bootstrap_samples must be nonnegative integer")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if not outcomes:
        raise ValueError("outcome table empty")
    relevant = [o for o in outcomes if o.policy in (treatment_policy, control_policy)]
    if len(relevant) != len(outcomes):
        raise ValueError("only two compared policies are permitted")
    indexed: dict[tuple[str, str, int, str], dict[str, EvaluationOutcome]] = {}
    for o in relevant:
        bucket = indexed.setdefault(o.key, {})
        if o.policy in bucket:
            raise ValueError("duplicate record for paired policy/key")
        bucket[o.policy] = o
    if any(set(records) != {treatment_policy, control_policy}
           for records in indexed.values()):
        raise ValueError("unmatched task/model/seed/budget between policies")
    grouped: dict[str, list[int]] = {}
    pos = neg = 0
    for records in indexed.values():
        a = records[treatment_policy]
        b = records[control_policy]
        if a.lineage_group != b.lineage_group:
            raise ValueError("same paired task assigned to different fork lineage")
        delta = a.verified_success - b.verified_success
        pos += int(delta == 1)
        neg += int(delta == -1)
        grouped.setdefault(a.lineage_group, []).append(delta)
    n = len(indexed)
    if not n:
        raise ValueError("no complete pairs")
    effect = (pos - neg) / n
    interval = None
    if bootstrap_samples and len(grouped) >= 2:
        rng = Random(seed)
        groups = sorted(grouped)
        values = []
        for _ in range(bootstrap_samples):
            draws = [groups[rng.randrange(len(groups))] for _ in groups]
            sampled = [d for name in draws for d in grouped[name]]
            values.append(sum(sampled) / len(sampled))
        values.sort()
        # Nearest-rank percentile bootstrap, pre-specified alpha=.05.
        lower_index = max(0, int(.025 * bootstrap_samples) - 1)
        upper_index = min(bootstrap_samples - 1, int(.975 * bootstrap_samples))
        interval = (values[lower_index], values[upper_index])
    return PairedDifference(n, len(grouped), pos, neg, effect, interval)
