"""Offline one-step evidence ambiguity witness; not a real code success result."""
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, ConditionalState,
)
from ucode.scenario_robust_evidence import (
    choose_scenario_robust_probe, conditional_one_step_net_gain,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def main():
    state = ConditionalState(.5, ResourceVector(test_calls=2))
    probe = ConditionalProbe("test", "test", ResourceVector(test_calls=1))
    rule = ReleaseRule(max_predicted_failure=.1)
    prices = ResourcePrices(test_calls=.01)
    perfect = ConditionalKernel((ConditionalRow("test", (), 1, 0),))
    inaccurate = ConditionalKernel((ConditionalRow("test", (), .8, .2),))
    nominal = conditional_one_step_net_gain(
        state, probe, perfect, prices, rule)
    uncertain = choose_scenario_robust_probe(
        state, [probe], [perfect, inaccurate], prices, rule)
    if not abs(nominal - .49) < 1e-12:
        raise AssertionError("nominal evidence arithmetic")
    if (uncertain.action != "abstain" or
            uncertain.assessments[0].label != "SCENARIO_SENSITIVE"
            or abs(uncertain.assessments[0].worst_case_gain + .01) > 1e-12
            or abs(uncertain.assessments[0].best_case_gain - .49) > 1e-12):
        raise AssertionError("scenario-robust evidence arithmetic")
    print(f"SYNTHETIC NOMINAL ONE-STEP GAIN: {nominal:.3f}")
    print("SYNTHETIC MODEL ENSEMBLE GAIN RANGE: [-0.010, +0.490]")
    print("FINITE-SCENARIO ROBUST ACTION: abstain")
    print("NO REAL MODEL INFERENCE / NO TASK EVALUATION / NO RISK CERTIFICATE")


if __name__ == "__main__":
    main()
