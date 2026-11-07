"""Reproduce a closed-form three-event DRPA action reversal: SYNTHETIC ONLY.

No model inference, licensed source checkout, hidden test, external task
runner, measured costs or paper performance claim. Values are illustrative.
"""
import json

from ucode.dependence_robust_acquisition import (
    RobustParetoProposal, TwoPointOutcome, bound_candidate_hvi,
    choose_dependence_robust_action,
)
from ucode.joint_validity_acquisition import (
    bound_joint_validity_hvi, choose_joint_validity_action,
)
from ucode.vector_policy import ResourceVector, ResourcePrices


def demo():
    proposal = RobustParetoProposal(
        action_id="SYNTHETIC_generate",
        action="generate",
        reliability=TwoPointOutcome(0, 1, .7),
        safety=TwoPointOutcome(0, 1, .7),
        probability_valid=.7,
        cost=ResourceVector(tokens=2),
    )
    prices = ResourcePrices(tokens=.1)
    cap = ResourceVector(tokens=4)
    before = bound_candidate_hvi((), proposal, prices)
    after = bound_joint_validity_hvi((), proposal, prices)
    old = choose_dependence_robust_action((),(proposal,),cap,prices)
    new = choose_joint_validity_action((),(proposal,),cap,prices)
    assert abs(before.gross_hvi_range[0] - .28) < 1e-12
    assert abs(after.gross_hvi_range[0] - .1) < 1e-12
    assert old.action_id == "SYNTHETIC_generate" and new.action == "stop"
    return {
        "stage": "SYNTHETIC_EXACT_THREE_WAY_MARGINAL_COUPLING_NOT_REAL_TASK",
        "reliability_high_marginal": .7,
        "safety_high_marginal": .7,
        "validity_marginal": .7,
        "legacy_two_way_independent_validity_lower_hvi": before.gross_hvi_range[0],
        "three_way_arbitrary_dependence_lower_hvi": after.gross_hvi_range[0],
        "three_way_arbitrary_dependence_upper_hvi": after.gross_hvi_range[1],
        "five_component_cost": {"tokens":2,"test_calls":0,"gpu_seconds":0,
                                "cpu_seconds":0,"wall_seconds":0},
        "scalarized_cost": after.scalar_cost,
        "legacy_action": old.action,
        "three_way_action": new.action,
        "three_way_min_joint_witness": list(after.min_coupling_weights),
        "joint_distribution_atom_order": after.atom_order,
        "qualified_real_tasks": 0,
        "external_code_executed": False,
        "independent_functional_oracles": 0,
        "llm_inferences": 0,
        "measured_policy_effect": None,
    }


def main():
    print(json.dumps(demo(),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
