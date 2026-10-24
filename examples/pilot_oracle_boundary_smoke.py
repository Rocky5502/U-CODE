"""Reproduce prospectively unsealed task registration and mathematical witness.

This example runs ONLY first-party metadata and arithmetic; no PHP/Go
repository source code, hidden oracle or LLM is accessed or executed.
"""
import json

from scripts.check_evaluator_boundary import check_registrations
from ucode.spec_ambiguity import (
    almost_equal_payout_witness, independent_spec_risks,
)


def demo() -> dict:
    reports = check_registrations()
    example = almost_equal_payout_witness(10, (0, 5))
    return {
        "warning": "PROSPECTIVE_ONLY; NO_EXTERNAL_CODE_EXECUTED; NO_SEALED_ORACLE",
        "registered_pilot_ids": [r["candidate_id"] for r in reports],
        "approved_pilots": sum(bool(r["independently_admitted"]) for r in reports),
        "visible_metadata_separated": True,
        "go_hypothetical_loser_deltas": list(example.actual_loser_deltas),
        "go_hypothetical_recovered_pool": example.recovered_pool,
        "go_multiple_fair_allocations": [
            list(x) for x in example.possible_winner_deltas
        ],
        "go_possible_oracle_risks": list(independent_spec_risks(example)),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
