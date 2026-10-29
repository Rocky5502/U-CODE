"""Synthetic-only action-policy mechanism: two complementary public probes.

The code does NOT execute repositories, call real LLMs or use a hidden oracle.
No actual correctness or risk reduction follows from this constructed example.
"""
import json

from ucode.action_id_replay_bridge import ActionBoundBook,ActionBoundResponse
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.conditional_bes import ConditionalKernel,ConditionalRow,Observation
from ucode.conditional_bes_public_replay import run_conditional_bes_synthetic_reference
from ucode.optimized_search import SearchAction
from ucode.uncertainty_only_reference import SyntheticConfidenceCard,SyntheticRiskRegister
from ucode.vector_policy import ResourcePrices,ResourceVector as RV
from ucode.voi import ReleaseRule


def main():
    sha="a"*64
    gen=SearchAction("gen","generate",RV(tokens=3))
    first=SearchAction("a","test",RV(test_calls=1))
    second=SearchAction("b","static_analysis",RV(cpu_seconds=1))
    budget=RV(tokens=4,test_calls=2,cpu_seconds=2,wall_seconds=3)
    book=ActionBoundBook((gen,first,second),(
        ActionBoundResponse("gen","generate",None,gen.cost,RV(tokens=2),
                            produced_sha256=sha),
        ActionBoundResponse("a","test",sha,first.cost,first.cost,
                            visible_positive=True),
        ActionBoundResponse("b","static_analysis",sha,second.cost,second.cost,
                            visible_positive=True),
    ))
    cards=SyntheticRiskRegister((SyntheticConfidenceCard(sha,.5,.8,.8),),.9)
    rows=[]
    for action,other in (("a","b"),("b","a")):
        rows.append(ConditionalRow(action,(),.8,.2))
        for sign in (False,True):
            rows.append(ConditionalRow(action,(Observation(other,sign),),.8,.2))
    kernel=ConditionalKernel(tuple(rows))
    two_step=run_conditional_bes_synthetic_reference(
        "SYNTHETIC_TWO_PROBE",budget,book,cards,kernel,
        ResourcePrices(test_calls=.01,cpu_seconds=.01),
        ReleaseRule(max_predicted_failure=.1),horizon=2)
    one_test=run_adaptive_synthetic_reference(
        "SYNTHETIC_TWO_PROBE","uncertainty_only",budget,book,
        uncertainty_register=cards)

    if (two_step.selected_action_ids!=("gen","a","b") or
        one_test.selected_action_ids!=("gen","a") or
        two_step.status!="RELEASED_PENDING_INDEPENDENT_EVALUATION" or
        one_test.status!="ABSTAINED"):
        raise AssertionError("synthetic decision divergence no longer reproduced")
    if two_step.independent_oracle_labels or one_test.independent_oracle_labels:
        raise AssertionError("no independent evaluator must be invoked")
    print(json.dumps({
        "status":"SYNTHETIC_OFFLINE_POLICY_MECHANISM_NOT_EMPIRICAL",
        "same_public_action_catalog_digest":(
            two_step.initial_opportunity_sha256==one_test.initial_opportunity_sha256),
        "same_frozen_public_outcome_book":(
            two_step.response_book_sha256==one_test.response_book_sha256),
        "conditional_BES":{
            "chosen":two_step.selected_action_ids,"terminal":two_step.status},
        "uncertainty_only":{
            "chosen":one_test.selected_action_ids,"terminal":one_test.status},
        "real_model_calls":0,"independent_gold_labels":0,
        "real_task_correctness_measured":False,
        "calibrated_predictor":False,
        "trusted_hardware_meter":False,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
