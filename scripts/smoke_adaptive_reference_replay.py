"""Offline behavioral divergence of TWO scoped adaptive reference controls.

This is a reproducible synthetic illustration; no measured coding results.
"""
import json
from ucode.action_id_replay_bridge import ActionBoundBook, ActionBoundResponse
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.optimized_search import SearchAction, SearchPolicy
from ucode.vector_policy import ResourceVector as RV


def main():
    a="a"*64
    b="b"*64
    gen=SearchAction("gen","generate",RV(tokens=2))
    test=SearchAction("test","test",RV(test_calls=1))
    repair=SearchAction("repair","repair",RV(tokens=3))
    book=ActionBoundBook((gen,test,repair),(
        ActionBoundResponse("gen","generate",None,gen.cost,gen.cost,
                            produced_sha256=a),
        ActionBoundResponse("test","test",a,test.cost,test.cost,
                            visible_positive=False),
        ActionBoundResponse("repair","repair",a,repair.cost,RV(tokens=2),
                            produced_sha256=b),
    ))
    p=SearchPolicy(depth=1,beam_width=6,max_candidates=8,
                   min_positive_tests=1,
                   action_rewards=(1.,0.,5.,0.,0.),
                   repair_after_failure_bonus=6.,
                   first_test_bonus=2.,diversity_bonus=0.,
                   continue_threshold=0.1)
    cap=RV(tokens=10,test_calls=2,cpu_seconds=2,wall_seconds=2)
    runs={
        name:run_adaptive_synthetic_reference(
            "SYNTHETIC_ADAPTIVE_DEMO",name,cap,book,baseline=p)
        for name in ("fixed_testing","no_uncertainty_search")
    }
    assert runs["fixed_testing"].selected_action_ids == ("gen","test")
    assert runs["no_uncertainty_search"].selected_action_ids == (
        "gen","test","repair")
    assert all(r.independent_oracle_labels == 0 and
               r.model_inferences == 0 for r in runs.values())
    print(json.dumps({
        "stage":"SYNTHETIC_ONLY_NOT_REAL_POLICY_EFFECTIVENESS",
        "shared_response_book_sha256":book.digest_sha256,
        "policies":{
            name:{
                "status":r.status,
                "selected_action_ids":r.selected_action_ids,
                "reported_tokens_remaining":r.session.state.remaining.tokens,
                "public_trace_sha256":r.session.trace_sha256,
                "heldout_oracle_labels":0,
            } for name,r in runs.items()
        },
        "real_tasks_admitted":0,
        "model_inferences_executed":0,
        "authenticated_resource_meters":0,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
