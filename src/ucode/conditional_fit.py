"""Training-only history-conditioned diagnostic likelihood estimation.

All probes must be administered according to a PRECOMMITTED FULL PANEL,
regardless of their observed outcomes. This rules out omission by adaptive
policies in the input contract; it does not validate actual collection logs.
Train/evaluation fork groups are strictly segregated. No hidden evaluator
outcome is ever returned to the runtime action policy.
"""
from dataclasses import dataclass
import json
from hashlib import sha256
from math import isfinite
from typing import Sequence

from .conditional_bes import (
    ConditionalKernel, ConditionalRow, Observation,
)
from .diagnostic_fit import GroupPartitions
from .vector_policy import DIAGNOSTICS


@dataclass(frozen=True)
class FullPanelTrainingTrace:
    task_id: str
    lineage_group: str
    model_id: str
    action_order: tuple[str, ...]
    outcomes: tuple[bool, ...]
    visible_times: tuple[int, ...]
    oracle_acceptable: int
    oracle_time: int
    oracle_id: str
    assignment_protocol: str = "precommitted_full_panel"

    def __post_init__(self):
        for name in ("task_id", "lineage_group", "model_id", "oracle_id"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"{name} required")
        if self.assignment_protocol != "precommitted_full_panel":
            raise ValueError("adaptive or untracked diagnostic selection prohibited")
        n = len(self.action_order)
        if (not 1 <= n <= 4 or len(self.outcomes) != n
                or len(self.visible_times) != n):
            raise ValueError("full panel must have 1-4 observed diagnostics")
        if any(not isinstance(a, str) or not a.strip() for a in self.action_order):
            raise ValueError("invalid action ID")
        if len(set(self.action_order)) != n:
            raise ValueError("duplicate diagnostic action in full panel")
        if any(type(x) is not bool for x in self.outcomes):
            raise ValueError("diagnostic results must be booleans")
        if type(self.oracle_acceptable) is not int or self.oracle_acceptable not in (0, 1):
            raise ValueError("training oracle label must be integer 0/1")
        if type(self.oracle_time) is not int or self.oracle_time < 0:
            raise ValueError("oracle timestamp must be nonnegative integer")
        last = -1
        for t in self.visible_times:
            if type(t) is not int or t <= last or t >= self.oracle_time:
                raise ValueError("diagnostic timestamps must be increasing and pre-oracle")
            last = t


@dataclass(frozen=True)
class ConditionalFitManifest:
    kernel: ConditionalKernel
    training_task_count: int
    lineage_count: int
    context_count: int
    minimum_per_class: int
    input_fingerprint: str
    status: str = "training_only_not_independently_validated"
    minimum_lineages_per_context_class: int = 2
    weakest_class_context_lineages: int = 0


def fit_history_conditional_kernel(
    traces: Sequence[FullPanelTrainingTrace],
    partitions: GroupPartitions,
    model_id: str,
    action_ids: tuple[str, ...],
    *,
    minimum_per_class: int = 1,
    minimum_lineages: int = 2,
    pseudocount: float = 1.0,
    minimum_lineages_per_context_class: int = 2,
) -> ConditionalFitManifest:
    """Fit pre-oracle P(+|Y,h) only on complete training-group panels.

    Requires all specified actions per task even if an early probe appears
    decisive. Individual action order may differ between tasks; real studies
    must preregister/randomize it and verify that assignment is independent
    of latent patch correctness. The fit DOES NOT enforce such randomization.

    Sparse observed contexts FAIL instead of inheriting independence or
    silently applying a parent-context estimate. Missing unobserved
    contexts remain absent; the planner will refuse a reachable missing row.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("model_id required")
    if (not isinstance(action_ids, tuple) or not 1 <= len(action_ids) <= 4
            or len(set(action_ids)) != len(action_ids)
            or any(not isinstance(a, str) or not a.strip() for a in action_ids)):
        raise ValueError("1-4 unique frozen action IDs required")
    if type(minimum_per_class) is not int or minimum_per_class < 1:
        raise ValueError("minimum_per_class must be at least one")
    if type(minimum_lineages) is not int or minimum_lineages < 2:
        raise ValueError("minimum_lineages must be at least two")
    if (type(minimum_lineages_per_context_class) is not int
            or minimum_lineages_per_context_class < 2):
        raise ValueError("minimum_lineages_per_context_class must be at least two")
    if type(pseudocount) not in (int, float) or not isfinite(pseudocount) or pseudocount <= 0:
        raise ValueError("smoothing must be positive finite")
    if not traces:
        raise ValueError("no training full-panel traces")

    used_tasks: set[str] = set()
    groups: set[str] = set()
    # For each (action, visible prefix), track acceptable/unacceptable counts
    # and positive outcomes separately, without any evaluation fold labels.
    counts: dict[tuple[str, tuple[Observation, ...]], list[int]] = {}
    context_lineages: dict[
        tuple[str, tuple[Observation, ...]], tuple[set[str], set[str]]
    ] = {}
    fingerprints: list[str] = []
    for trace in traces:
        if not isinstance(trace, FullPanelTrainingTrace):
            raise TypeError("each row must be a FullPanelTrainingTrace")
        if partitions.partition(trace.lineage_group) != "train":
            raise ValueError("validation/evaluation trace is forbidden in training fit")
        if trace.model_id != model_id:
            raise ValueError("cannot pool distinct model checkpoints")
        if len(trace.action_order) != len(action_ids) or set(trace.action_order) != set(action_ids):
            raise ValueError("each task must have complete precommitted full action panel")
        if trace.task_id in used_tasks:
            raise ValueError("duplicate task in training panel")
        used_tasks.add(trace.task_id)
        groups.add(trace.lineage_group)
        # Structured JSON avoids collisions when identifiers contain '|',
        # commas or newlines. This is only an input-change fingerprint;
        # no signature or independent source attestation is implied.
        fingerprints.append(json.dumps(
            [trace.task_id, trace.lineage_group, trace.model_id,
             list(trace.action_order), list(trace.outcomes),
             list(trace.visible_times), trace.oracle_acceptable,
             trace.oracle_time, trace.oracle_id],
            ensure_ascii=False, separators=(",", ":"),
        ))
        hist: tuple[Observation, ...] = ()
        for action, positive in zip(trace.action_order, trace.outcomes):
            key = (action, hist)
            # indices: acceptable_total, unacceptable_total,
            # acceptable_positive, unacceptable_positive
            stats = counts.setdefault(key, [0, 0, 0, 0])
            supports = context_lineages.setdefault(key, (set(), set()))
            label = trace.oracle_acceptable
            supports[0 if label else 1].add(trace.lineage_group)
            stats[0 if label else 1] += 1
            if positive:
                stats[2 if label else 3] += 1
            hist = hist + (Observation(action, positive),)
    if len(groups) < minimum_lineages:
        raise ValueError("too few independent training repository lineages")

    rows = []
    weakest_context = min(
        min(len(supports[0]), len(supports[1]))
        for supports in context_lineages.values()
    )
    for (action, history), (good, bad, good_positive, bad_positive) in sorted(
        counts.items(), key=lambda z: (z[0][0], tuple(
            (h.action_id, h.positive) for h in z[0][1]))):
        if min(good, bad) < minimum_per_class:
            raise ValueError("sparse conditional context; no silent backoff is allowed")
        # The existing global two-lineage gate cannot rule out that an
        # action/history/label cell draws exclusively from one repository.
        # Such an estimate could confound latent correctness with repository
        # structure and make the sequential planner appear calibrated.
        supports = context_lineages[(action, history)]
        if min(len(supports[0]), len(supports[1])) < minimum_lineages_per_context_class:
            raise ValueError(
                "insufficient independent training lineages per conditional "
                "context and acceptability class"
            )
        rows.append(ConditionalRow(
            action, history,
            (good_positive + pseudocount)/(good + 2*pseudocount),
            (bad_positive + pseudocount)/(bad + 2*pseudocount),
        ))
    payload = json.dumps(
        ["ucode-conditional-fit-v2", sorted(fingerprints)],
        ensure_ascii=False, separators=(",", ":"),
    )
    fingerprint = sha256(payload.encode("utf-8")).hexdigest()
    return ConditionalFitManifest(
        kernel=ConditionalKernel(tuple(rows)),
        training_task_count=len(traces), lineage_count=len(groups),
        context_count=len(rows), minimum_per_class=minimum_per_class,
        input_fingerprint=fingerprint,
        minimum_lineages_per_context_class=minimum_lineages_per_context_class,
        weakest_class_context_lineages=weakest_context,
    )
