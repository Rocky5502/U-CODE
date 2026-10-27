"""Inspect frozen one-step scenario sensitivity of diagnostics AND generation.

Synthetic mathematical counterexample. Not model inference, no source checkout,
no independent evaluator, and no statistical calibration assertion.
"""
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, ConditionalState,
)
from ucode.joint_scenario_action import (
    FrozenJointScenario, ScenarioGenerationAction,
    ScenarioGenerationValue, choose_joint_scenario_action,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def scenario(name, se, fp, generation_value):
    return FrozenJointScenario(
        name,
        ConditionalKernel((ConditionalRow("check", (), se, fp),)),
        (ScenarioGenerationValue("generate", generation_value),))


def main():
    state = ConditionalState(.5, ResourceVector(tokens=100, test_calls=2))
    actions = (
        ConditionalProbe("check", "test", ResourceVector(test_calls=1)),
        ScenarioGenerationAction("generate", ResourceVector(tokens=5)),
    )
    prices = ResourcePrices(tokens=.002, test_calls=.01)
    rule = ReleaseRule(max_predicted_failure=.1)
    mixed = choose_joint_scenario_action(
        state, actions,
        (scenario("perfect_good_generator", 1., 0., .20),
         scenario("noisy_better_generator", .8, .2, .25)),
        prices, rule)
    verified = choose_joint_scenario_action(
        state, actions,
        (scenario("perfect_optimistic_generator", 1., 0., .80),
         scenario("strong_pessimistic_generator", .95, .05, .01)),
        prices, rule)
    if (mixed.action != "generate"
            or verified.action != "check"
            or abs(mixed.worst_case_net_gain - .19) > 1e-12
            or mixed.executable_task_results != 0):
        raise AssertionError("frozen joint scenario arithmetic drift")
    print("JOINT SCENARIOS 1: generate (worst-case gain = 0.190)")
    print("JOINT SCENARIOS 2: check (strong diagnostic, uncertain generator)")
    print("NO REAL CODE/TASK EXECUTION, NO CALIBRATION OR RISK CERTIFICATION")


if __name__ == "__main__":
    main()
