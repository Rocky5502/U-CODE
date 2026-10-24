"""First-party synthetic BES evidence-dependence counterexample; no real tasks."""
import json

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow,
    ConditionalState, Observation, plan_conditional,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def _kernel(independent: bool) -> ConditionalKernel:
    rows = []
    for a, b in (("a", "b"), ("b", "a")):
        rows.append(ConditionalRow(a, (), .8, .2))
        for positive in (False, True):
            if independent:
                good, bad = .8, .2
            else:
                good = bad = 1. if positive else 0.
            rows.append(ConditionalRow(
                a, (Observation(b, positive),), good, bad))
    return ConditionalKernel(tuple(rows))


def run_demo() -> dict:
    state = ConditionalState(.5, ResourceVector(test_calls=2))
    probes = [
        ConditionalProbe("a", "test", ResourceVector(test_calls=1)),
        ConditionalProbe("b", "test", ResourceVector(test_calls=1)),
    ]
    prices = ResourcePrices(test_calls=.01)
    rule = ReleaseRule(.1)
    independent = plan_conditional(state, probes, _kernel(True),
                                   prices, rule, horizon=2)
    redundant = plan_conditional(state, probes, _kernel(False),
                                 prices, rule, horizon=2)
    return {
        "evidence": "SYNTHETIC ONLY; zero third-party repository or model executions",
        "common_first_probe_sensitivity": .8,
        "common_first_probe_specificity": .8,
        "independent_first_action": independent.action,
        "independent_hypothetical_utility": independent.expected_net_utility,
        "redundant_first_action": redundant.action,
        "redundant_hypothetical_utility": redundant.expected_net_utility,
        "interpretation": "Marginal test quality does not identify joint evidence value",
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
