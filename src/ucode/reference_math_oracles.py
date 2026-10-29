"""Independent exact-rational mathematical checks for U-CODE research claims.

These are SMALL discrete reference oracles, written separately from the
floating-point BES / VOI implementations. They do not inspect held-out
software tests, generate code or certify a real agent. Exactness applies
only to the specified finite hypothetical probability model.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import product


def _prob(value, name: str) -> F:
    if type(value) is bool or type(value) not in (int, F):
        raise ValueError(name + " must be an exact int/Fraction")
    if not 0 <= value <= 1:
        raise ValueError(name + " must be a probability in [0,1]")
    return F(value)


def binary_update(prior, sensitivity, specificity):
    """Independent Bayes joint-mass calculation; impossible posterior is None.

    Returns (P(+), P(-), P(Y=1|+), P(Y=1|-)) with exact fractions.
    """
    p = _prob(prior, "prior")
    se = _prob(sensitivity, "sensitivity")
    sp = _prob(specificity, "specificity")
    joint_pos_y = p * se
    joint_neg_y = p * (1 - se)
    pos = joint_pos_y + (1-p) * (1-sp)
    neg = joint_neg_y + (1-p) * sp
    assert pos + neg == 1
    return (pos, neg,
            joint_pos_y / pos if pos else None,
            joint_neg_y / neg if neg else None)


def exact_terminal(prior, *, failure_gate=F(1, 10),
                   reward=F(1), penalty=F(1)) -> F:
    """Predictive gate + release/abstain utility; not a risk certificate."""
    p = _prob(prior, "prior")
    gate = _prob(failure_gate, "failure_gate")
    if any(type(v) is bool or type(v) not in (int, F) or v < 0
           for v in (reward, penalty)):
        raise ValueError("reward and penalty must be nonnegative exact values")
    payoff = p*reward - (1-p)*penalty
    return F(payoff) if 1-p <= gate and payoff > 0 else F(0)


def one_probe_expectation(prior, sensitivity, specificity, *,
                          failure_gate=F(1, 10), price=F(0)) -> F:
    """Independent exact one-step value of a PRECOMMITTED diagnostic."""
    if type(price) is bool or type(price) not in (int, F) or price < 0:
        raise ValueError("price must be nonnegative exact value")
    qpos, qneg, ppos, pneg = binary_update(prior, sensitivity, specificity)
    ev = F(0)
    if qpos:
        ev += qpos * exact_terminal(ppos, failure_gate=failure_gate)
    if qneg:
        ev += qneg * exact_terminal(pneg, failure_gate=failure_gate)
    return ev - price


def exhaustive_two_probe(prior=F(1, 2), *,
                         sensitivity=F(4, 5), specificity=F(4, 5),
                         price=F(1, 100), failure_gate=F(1, 10),
                         dependence="independent"):
    """Enumerate policies for at most two probes, without BES recursion.

    'duplicate' means the second test is the EXACT same visible signal,
    conditional on the first, so it has zero incremental evidence.
    Evaluates stop, one test, and the outcome-contingent second purchase.
    The output is the max expected utility of these explicit policies.
    """
    if dependence not in ("independent", "duplicate"):
        raise ValueError("only independent/identically repeated tests specified")
    p = _prob(prior, "prior")
    se = _prob(sensitivity, "sensitivity")
    sp = _prob(specificity, "specificity")
    if type(price) is bool or type(price) not in (int, F) or price < 0:
        raise ValueError("nonnegative rational price required")
    gate = _prob(failure_gate, "failure_gate")
    baseline = exact_terminal(p, failure_gate=gate)
    q_pos, q_neg, posterior_pos, posterior_neg = binary_update(p, se, sp)

    # Every branch can independently stop or buy one remaining test.
    # A purchased test incurs price only on the branch where purchased.
    after_first = F(0)
    for observed, q, posterior in ((True, q_pos, posterior_pos),
                                   (False, q_neg, posterior_neg)):
        if not q:
            continue
        stop = exact_terminal(posterior, failure_gate=gate)
        if dependence == "independent":
            second = one_probe_expectation(
                posterior, se, sp, failure_gate=gate, price=price)
        else:
            # Duplicated evidence is deterministic given the first outcome.
            # It cannot change the posterior or improve terminal utility.
            second = stop - price
        after_first += q * max(stop, second)
    return max(baseline, after_first-price)


def exhaustive_missingness_envelopes(s: int, w: int, u: int,
                                     known_nonreleases: int):
    """Brute-force all assignments of u missing cells into S/W/N outcomes.

    Sharp bounds on ITT success, coverage and conditional wrong-release
    risk for this finite set; conditional risk is null if no release
    is possible. This is NOT a frequentist sampling confidence interval.
    """
    counts = (s, w, u, known_nonreleases)
    if any(type(k) is not int or k < 0 for k in counts):
        raise ValueError("nonnegative integer counts required")
    n = sum(counts)
    if n == 0:
        raise ValueError("at least one assignment required")
    successes, covers, risks = [], [], []
    for unknown_successes in range(u+1):
        for unknown_wrong in range(u-unknown_successes+1):
            releases = s+w+unknown_successes+unknown_wrong
            successes.append(F(s+unknown_successes, n))
            covers.append(F(releases, n))
            if releases:
                risks.append(F(w+unknown_wrong, releases))
    return {
        "success": (min(successes), max(successes)),
        "coverage": (min(covers), max(covers)),
        "conditional_wrong_release": (
            (min(risks), max(risks)) if risks else None),
    }


def formula_missingness_envelopes(s: int, w: int, u: int,
                                  known_nonreleases: int):
    """Closed-form counterpart, independently cross-checked by enumeration."""
    if any(type(k) is not int or k < 0 for k in
           (s, w, u, known_nonreleases)):
        raise ValueError("nonnegative integer counts required")
    n = s+w+u+known_nonreleases
    if not n:
        raise ValueError("at least one assignment required")
    r = s+w
    return {
        "success": (F(s, n), F(s+u, n)),
        "coverage": (F(r, n), F(r+u, n)),
        "conditional_wrong_release": (
            (F(w, r+u), F(w+u, r+u)) if r+u else None),
    }
