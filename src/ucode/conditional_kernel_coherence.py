"""S04 source-only audit: diagnostic likelihoods must commute across orders.

The frozen likelihood rows P(O_a | Y, visible history) are hypothetical
or training-only. This audit never consumes an evaluator gold label,
authenticates training provenance, proves global calibration, or runs a model.
It checks the necessary joint-probability equality for two observations
when BOTH orders are represented by the given conditional table.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import isfinite
from typing import Sequence

from .conditional_bes import ConditionalKernel, Observation

TERMINAL_NAMES = frozenset(("release", "abstain"))


@dataclass(frozen=True)
class CommutationViolation:
    """One incompatible joint event, conditional on a fixed latent class."""

    history: tuple[Observation, ...]
    first_action: str
    second_action: str
    first_positive: bool
    second_positive: bool
    class_acceptable: bool
    probability_first_then_second: float
    probability_second_then_first: float
    absolute_discrepancy: float


@dataclass(frozen=True)
class ConditionalCoherenceAudit:
    action_ids: tuple[str, ...]
    inspected_histories: int
    compared_event_class_cells: int
    missing_order_event_cells: int
    maximum_absolute_discrepancy: float
    violations: tuple[CommutationViolation, ...]
    status: str
    independently_authenticated_training: bool = False
    statistical_calibration_proven: bool = False
    qualified_executable_task_runs: int = 0


def audit_conditional_order_coherence(
    kernel: ConditionalKernel,
    action_ids: Sequence[str],
    *,
    tolerance: float = 1e-10,
    max_history_length: int = 3,
    require_complete: bool = False,
) -> ConditionalCoherenceAudit:
    """Check P(a=x,b=y|Y,h) from two possible action acquisition orders.

    For every history h, pair (a,b), signs (x,y), and latent outcome
    Y in {acceptable, unacceptable}, compare:
        P(a=x|Y,h) P(b=y|Y,h,a=x) and
        P(b=y|Y,h) P(a=x|Y,h,b=y).

    Disagreement demonstrates that the supplied table cannot describe a
    common joint observation process (under the *same* latent correctness).
    Sparse tables are reported INCOMPLETE, not silently judged coherent;
    require_complete=True fails closed on missing alternative paths.
    Agreement is NECESSARY, not a proof of globally consistent calibration.
    This diagnostic is bounded to 10 probes, <=3000 conditional rows and
    maximum conditioning history length three.
    """
    if type(kernel) is not ConditionalKernel:
        raise TypeError("typed frozen ConditionalKernel required")
    if type(action_ids) not in (tuple, list):
        raise TypeError("bounded ordered action ID sequence required")
    acts = tuple(action_ids)
    if (not 2 <= len(acts) <= 10
            or any(type(x) is not str or not x.strip()
                   or x in TERMINAL_NAMES for x in acts)
            or len(set(acts)) != len(acts)):
        raise ValueError("2-10 unique nonterminal action IDs required")
    if (type(tolerance) not in (float, int)
            or not isfinite(tolerance) or not 0 <= tolerance <= 1e-6):
        raise ValueError("finite bounded numeric tolerance required")
    if type(max_history_length) is not int or not 0 <= max_history_length <= 3:
        raise ValueError("max_history_length must be integer 0 to 3")
    if type(require_complete) is not bool:
        raise TypeError("require_complete must be boolean")
    if len(kernel.rows) > 3000:
        raise ValueError("bounded conditional table exceeded 3000 rows")
    rows = {(r.action_id, r.history): r for r in kernel.rows}
    visible = set(acts)
    histories = {()}
    for row in kernel.rows:
        if row.action_id not in visible:
            raise ValueError("kernel row action outside frozen set")
        if any(x.action_id not in visible for x in row.history):
            raise ValueError("kernel context action outside frozen set")
        if len(row.history) <= max_history_length:
            histories.add(row.history)
    ordered_histories = sorted(
        histories, key=lambda h: (
            len(h), tuple((o.action_id, o.positive) for o in h)
        )
    )
    compared = 0
    missing = 0
    largest = 0.0
    violations = []
    for history in ordered_histories:
        consumed = {o.action_id for o in history}
        remaining = sorted(visible - consumed)
        for a, b in combinations(remaining, 2):
            root_a = rows.get((a, history))
            root_b = rows.get((b, history))
            if root_a is None or root_b is None:
                # Four sign pairs cannot be cross-ordered without both roots.
                missing += 4
                continue
            for x, y in product((False, True), repeat=2):
                row_b_after_a = rows.get((
                    b, history + (Observation(a, x),)
                ))
                row_a_after_b = rows.get((
                    a, history + (Observation(b, y),)
                ))
                if row_b_after_a is None or row_a_after_b is None:
                    missing += 1
                    continue
                for acceptable in (False, True):
                    kind = (
                        "positive_if_acceptable" if acceptable
                        else "positive_if_unacceptable"
                    )
                    pa = getattr(root_a, kind)
                    pb = getattr(root_b, kind)
                    pab = getattr(row_b_after_a, kind)
                    pba = getattr(row_a_after_b, kind)
                    joint_ab = (pa if x else 1 - pa) * (
                        pab if y else 1 - pab
                    )
                    joint_ba = (pb if y else 1 - pb) * (
                        pba if x else 1 - pba
                    )
                    difference = abs(joint_ab - joint_ba)
                    largest = max(largest, difference)
                    compared += 1
                    if difference > tolerance:
                        violations.append(CommutationViolation(
                            history, a, b, x, y, acceptable,
                            joint_ab, joint_ba, difference,
                        ))
    status = (
        "INCOHERENT_TWO_ORDER_JOINT_EVENTS"
        if violations else (
            "INCOMPLETE_TWO_ORDER_COVERAGE"
            if missing or compared == 0
            else "LOCALLY_COHERENT_TWO_ORDER_EVENTS_ONLY"
        )
    )
    result = ConditionalCoherenceAudit(
        action_ids=acts,
        inspected_histories=len(ordered_histories),
        compared_event_class_cells=compared,
        missing_order_event_cells=missing,
        maximum_absolute_discrepancy=largest,
        violations=tuple(violations),
        status=status,
    )
    if violations:
        raise ValueError(
            "incoherent conditional diagnostic order: "
            f"{len(violations)} joint event-class discrepancies, "
            f"max={largest:.8g} (first {a}/{b} violation)"
        )
    if require_complete and (missing or not compared):
        raise ValueError(
            "incomplete conditional order coverage: "
            f"{missing} uncheckable event cells and {compared} compared"
        )
    return result
