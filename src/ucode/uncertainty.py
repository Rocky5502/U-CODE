"""Pre-verification uncertainty signals and proper calibration metrics.

Probabilities MUST be based on predictions made before seeing held-out outcomes.
A self-reported LLM confidence score is not assumed to be calibrated.
"""
from collections import Counter
from math import isfinite, log2
from typing import Iterable, Sequence


def _probability(value: float) -> float:
    p = float(value)
    if not isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("probability must be finite and in [0,1]")
    return p


def binary_entropy(probability: float) -> float:
    """Binary Shannon entropy, normalized to [0,1] (unit: bit)."""
    p = _probability(probability)
    if p in (0.0, 1.0):
        return 0.0
    return -p * log2(p) - (1.0 - p) * log2(1.0 - p)


def predictive_entropy(class_probabilities: Sequence[float]) -> float:
    """Normalized categorical entropy of a valid probability distribution."""
    ps = [_probability(p) for p in class_probabilities]
    if not ps or abs(sum(ps) - 1.0) > 1e-8:
        raise ValueError("class probabilities must sum to one")
    if len(ps) == 1:
        return 0.0
    return -sum(p * log2(p) for p in ps if p > 0) / log2(len(ps))


def variation_ratio(predictions: Iterable[str]) -> float:
    """Fraction not agreeing with the most common independent prediction."""
    votes = list(predictions)
    if not votes:
        raise ValueError("at least one prediction required")
    return 1.0 - max(Counter(votes).values()) / len(votes)


def brier_score(probabilities: Sequence[float], labels: Sequence[int]) -> float:
    """Mean squared error of pre-outcome P(success) against binary correctness."""
    pairs = _validated_pairs(probabilities, labels)
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs)


def expected_calibration_error(
    probabilities: Sequence[float], labels: Sequence[int], bins: int = 10
) -> float:
    """Equal-width ECE (diagnostic; report Brier and calibration plots too)."""
    if bins < 1:
        raise ValueError("bins must be positive")
    pairs = _validated_pairs(probabilities, labels)
    grouped: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for p, y in pairs:
        grouped[min(int(p * bins), bins - 1)].append((p, y))
    total = len(pairs)
    return sum(
        len(g) / total
        * abs(sum(p for p, _ in g) / len(g) - sum(y for _, y in g) / len(g))
        for g in grouped if g
    )


def risk_coverage_curve(
    probabilities: Sequence[float], labels: Sequence[int]
) -> list[tuple[float, float]]:
    """(coverage, empirical failure risk) when accepting highest P(success) first.

    Do not derive probabilities from the held-out labels, or this leaks the oracle.
    """
    pairs = _validated_pairs(probabilities, labels)
    pairs.sort(key=lambda z: z[0], reverse=True)
    failures = 0
    output = []
    for i, (_, y) in enumerate(pairs, start=1):
        failures += 1 - y
        output.append((i / len(pairs), failures / i))
    return output


def _validated_pairs(
    probabilities: Sequence[float], labels: Sequence[int]
) -> list[tuple[float, int]]:
    if len(probabilities) != len(labels) or not probabilities:
        raise ValueError("nonempty equal-length probabilities and labels required")
    if any(y not in (0, 1) or isinstance(y, bool) for y in labels):
        raise ValueError("labels must be integer 0 or 1")
    return list(zip((_probability(p) for p in probabilities), labels))
