"""Synthetic BES look-ahead demonstration; NOT a software benchmark result."""
import json
from dataclasses import asdict

from ucode.belief_session import BeliefSession, plan_session, record_evidence
from ucode.budgeted_belief_search import EvidenceAction
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def run_demo() -> dict:
    budget = ResourceVector(test_calls=2)
    prices = ResourcePrices(test_calls=.01)
    rule = ReleaseRule(max_predicted_failure=.1)
    probes = [
        EvidenceAction("synthetic-test-a", "test", .8, .8,
                       ResourceVector(test_calls=1)),
        EvidenceAction("synthetic-test-b", "test", .8, .8,
                       ResourceVector(test_calls=1)),
    ]
    state = BeliefSession(.5, budget)
    myopic = plan_session(state, probes, prices, rule, horizon=1)
    lookahead = plan_session(state, probes, prices, rule, horizon=2,
                             assume_independent_diagnostics=True)
    # The following positives are fabricated scenario observations,
    # not output from running any test suite or third-party code.
    after_a = record_evidence(state, probes[0], True)
    after_b = record_evidence(after_a, probes[1], True)
    return {
        "warning": "SYNTHETIC analytical fixture; zero executed repositories/models/oracles",
        "one_step_action": myopic.first_action,
        "two_step_action": lookahead.first_action,
        "hypothetical_two_step_net_utility": lookahead.expected_net_utility,
        "fabricated_two_positive_posterior": after_b.prior,
        "remaining_test_calls_after_two_fabricated_positives":
            after_b.remaining.test_calls,
    }


def main() -> None:
    print(json.dumps(run_demo(), indent=2))


if __name__ == "__main__":
    main()
