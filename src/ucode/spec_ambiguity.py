"""Preexperimental ambiguity witness for a repository's settlement rules.

Based on PRE-PR requirements (nonnegative loser balances and zero-sum
payout), not on any claim that the merged Go patch is correct/incorrect.

The nearly-equal-winner constraint is a *stronger hypothetical fairness*
assumption added to make the underdetermination witness conservative.
It is not asserted to appear in the pre-fix business requirements.
"""
from dataclasses import dataclass

MAX_BALANCE = 2**63 - 1


@dataclass(frozen=True)
class PayoutWitness:
    nominal_loss_per_loser: int
    loser_balances: tuple[int, int]
    actual_loser_deltas: tuple[int, int]
    recovered_pool: int
    possible_winner_deltas: tuple[tuple[int, int], ...]
    pre_fix_spec_determines_unique_winner_assignment: bool
    source_scope: str = "hypothetical_fair_split_from_pre_fix_invariants"


def almost_equal_payout_witness(
    nominal_loss_per_loser: int,
    loser_balances: tuple[int, int],
) -> PayoutWitness:
    """Enumerate almost-equal allocations rather than assume a hidden gold.

    Actual losses follow balances >=0 and no more than nominal loss. We
    intentionally do not use a PR's chosen winner-ID tie break. The
    witness does not check real DB transactions, and is NOT an evaluator.
    """
    if type(nominal_loss_per_loser) is not int or not 0 <= nominal_loss_per_loser <= MAX_BALANCE:
        raise ValueError("nominal loss must be a nonnegative int64 amount")
    if not isinstance(loser_balances, tuple) or len(loser_balances) != 2:
        raise ValueError("exactly two loser balances required")
    if any(type(v) is not int or not 0 <= v <= MAX_BALANCE
           for v in loser_balances):
        raise ValueError("balances must be nonnegative int64 amounts")
    losses = tuple(-min(balance, nominal_loss_per_loser)
                   for balance in loser_balances)
    pool = -sum(losses)
    lower, remainder = divmod(pool, 2)
    candidates = ((lower, lower),) if remainder == 0 else (
        (lower, lower + 1), (lower + 1, lower))
    for awards in candidates:
        if (sum(awards) + sum(losses) != 0
                or any(b + delta < 0 for b, delta in zip(loser_balances, losses))
                or abs(awards[0] - awards[1]) > 1):
            raise AssertionError("internal conservation/feasibility violation")
    return PayoutWitness(
        nominal_loss_per_loser, loser_balances, losses, pool,
        candidates, len(candidates) == 1,
    )


def independent_spec_risks(w: PayoutWitness) -> tuple[str, ...]:
    """Return candidate-oracle questions, NEVER patch correctness labels."""
    risks = []
    if not w.pre_fix_spec_determines_unique_winner_assignment:
        risks.append("odd_remainder_tiebreak_not_determined_by_checked_invariants")
    risks.extend((
        "winner_initial_balances_and_rank_updates_not_modelled",
        "database_idempotency_and_retry_semantics_not_modelled",
        "authoritative_task_scope_and_oracle_still_unapproved",
    ))
    return tuple(risks)
