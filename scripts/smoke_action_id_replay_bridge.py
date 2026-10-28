"""Source-free synthetic unique-action-ID and candidate-provenance smoke.

Identical frozen action/target responses are consumed by eight registered
policy *names* using scripted decisions. This does NOT implement eight
methods, execute LLM inference or attest any model-generated correctness.
"""
import json
from pathlib import Path

from ucode.action_id_replay_bridge import (
    ActionBoundBook, ActionBoundResponse, replay_bound_synthetic_actions,
)
from ucode.matched_session import SharedDecision
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector as RV

ROOT=Path(__file__).resolve().parents[1]


def main():
    protocol=json.loads((ROOT/"configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
    a="a"*64
    b="b"*64
    gen=SearchAction("gen-a","generate",RV(tokens=2))
    test=SearchAction("test-a","test",RV(test_calls=1))
    repair=SearchAction("repair-a","repair",RV(tokens=3))
    book=ActionBoundBook((gen,test,repair),(
        ActionBoundResponse("gen-a","generate",None,gen.cost,
                            RV(tokens=2),produced_sha256=a),
        ActionBoundResponse("test-a","test",a,test.cost,
                            RV(test_calls=1),visible_positive=False),
        ActionBoundResponse("repair-a","repair",a,repair.cost,
                            RV(tokens=2),produced_sha256=b),
    ))
    script=(
        SharedDecision("gen-a","generate",None,gen.cost),
        SharedDecision("test-a","test",a,test.cost),
        SharedDecision("repair-a","repair",a,repair.cost),
        SharedDecision("release","release",b,RV()),
    )
    arms={}
    for pid in protocol["policy_ids"]:
        result=replay_bound_synthetic_actions(
            "SYNTHETIC_ACTION_ID_FIXTURE",
            RV(tokens=10,test_calls=2,cpu_seconds=1,wall_seconds=2),
            book,script)
        arms[pid]={
            "status":result.status,
            "public_trace_digest":result.session.trace_sha256,
            "chosen_action_ids":result.chosen_action_ids,
            "candidate_count":len(result.session.state.candidates),
        }
    assert len(arms)==8
    assert len({x["public_trace_digest"] for x in arms.values()})==1
    print(json.dumps({
        "stage":"SYNTHETIC_PUBLIC_ACTION_ID_REPLAY_NO_EXECUTION",
        "registered_policy_names":list(arms),
        "action_count":len(arms[protocol["primary_treatment"]]["chosen_action_ids"]),
        "candidate_archive_size":2,
        "shared_public_trace_digest":arms[protocol["primary_treatment"]]["public_trace_digest"],
        "book_sha256":book.digest_sha256,
        "real_task_admissions":0,
        "hidden_oracles":0,
        "model_inferences":0,
        "trusted_hardware_meters":0,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
