"""Reproduce one-step evidence-vs-generation action switch (SYNTHETIC ONLY)."""
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, ConditionalState,
)
from ucode.robust_mixed_intervention import choose_evidence_vs_generation
from ucode.vector_policy import GenerativeForecast, ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def main():
    state = ConditionalState(.5, ResourceVector(tokens=100, test_calls=2))
    test = ConditionalProbe("check", "test", ResourceVector(test_calls=1))
    regenerate = GenerativeForecast("generate", .2, ResourceVector(tokens=5))
    weak = ConditionalKernel((ConditionalRow("check", (), .8, .2),))
    perfect = ConditionalKernel((ConditionalRow("check", (), 1, 0),))
    nearly = ConditionalKernel((ConditionalRow("check", (), .95, .05),))
    prices = ResourcePrices(tokens=.002, test_calls=.01)
    rule = ReleaseRule(max_predicted_failure=.1)
    uncertain = choose_evidence_vs_generation(
        state, [test, regenerate], [perfect, weak], prices, rule)
    stable = choose_evidence_vs_generation(
        state, [test, regenerate], [perfect, nearly], prices, rule)
    if (uncertain.action != "generate" or stable.action != "check"
            or abs(uncertain.conservative_net_improvement - .19) > 1e-12):
        raise AssertionError("synthetic mixed-action counterexample failed")
    print("MIXED ONE-STEP SCENARIO-SENSITIVE EVIDENCE: generate")
    print("MIXED ONE-STEP UNIFORMLY GOOD EVIDENCE: check")
    print("GENERATOR FORECASTS REMAIN POINT ESTIMATES AND CAN BE WRONG")
    print("ZERO REAL CODE/TASK EXECUTION OR VERIFIED PERFORMANCE IMPROVEMENT")


if __name__ == "__main__":
    main()
