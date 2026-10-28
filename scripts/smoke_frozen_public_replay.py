"""Run identical frozen synthetic candidate/tool outcomes across eight slots.

Read-only local smoke: no real model, source code, oracle or verified metering.
"""
from hashlib import sha256
import json
from pathlib import Path

from ucode.blind_policy_trace import BlindAction
from ucode.experiment_contract import FrozenStudy
from ucode.frozen_public_replay import (
    FrozenPublicOutcome, SyntheticReplayBook, run_shared_frozen_replay,
)
from ucode.shadow_assignment_parity import AssignedOpportunity
from ucode.task_view_boundary import parse_agent_task_view
from ucode.vector_policy import ResourceVector as RV

ROOT = Path(__file__).resolve().parents[1]


def main():
    p=json.loads((ROOT/"configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
    spec="SYNTHETIC frozen public opportunity test, not real task."
    view=parse_agent_task_view({
        "repository":"synthetic/replay-fixture","base_sha":"a"*40,
        "prefixed_spec":spec,"spec_sha256":sha256(spec.encode()).hexdigest(),
    })
    cap=RV(tokens=25,test_calls=2,cpu_seconds=3,wall_seconds=4)
    generate_cap=RV(tokens=10,cpu_seconds=1,wall_seconds=1)
    test_cap=RV(test_calls=1,wall_seconds=1)
    candidate="SYNTHETIC patch not code"
    book=SyntheticReplayBook("b"*64,(
        FrozenPublicOutcome("generate",0,None,generate_cap,
                            RV(tokens=7,cpu_seconds=1,wall_seconds=1),
                            patch=candidate),
        FrozenPublicOutcome("test",0,sha256(candidate.encode()).hexdigest(),
                            test_cap,test_cap,feedback="SYNTHETIC public diagnostic"),
    ))
    study=FrozenStudy(
        (("SYNTHETIC_REPLAY_TASK","SYNTHETIC_LINEAGE"),),
        tuple(p["model_ids"]),tuple(p["policy_ids"]),(11,),
        (("ILLUSTRATIVE_ONLY",cap),))
    assignments=tuple(AssignedOpportunity(
        task_id="SYNTHETIC_REPLAY_TASK",lineage_group="SYNTHETIC_LINEAGE",
        model_id=m,policy_id=policy,seed=11,budget_id="ILLUSTRATIVE_ONLY",
        pre_fix_base_sha40=view.base_sha,
        model_checkpoint_sha40="c"*40,task_spec_sha256=view.spec_sha256,
        public_candidate_archive_sha256="d"*64,
        common_opportunity_catalog_sha256=book.catalog_sha256,
        tool_access_sha256="e"*64,environment_image_sha256="f"*64,
        resource_cap=cap,
    ) for m in study.model_ids for policy in study.policies)

    def placeholder_factory(a):
        def policy(st):
            if not st.history:
                return BlindAction("generate",generate_cap)
            if len(st.history)==1:
                return BlindAction("test",test_cap)
            return BlindAction("release",RV())
        return policy
    books={(a.task_id,a.model_id,a.seed,a.budget_id):book for a in assignments}
    report=run_shared_frozen_replay(
        study,assignments,{"SYNTHETIC_REPLAY_TASK":view},
        {pid:placeholder_factory for pid in study.policies},books)
    print(json.dumps({
        "status":report.stage,
        "policy_slots":len(study.policies),
        "model_ids_only_not_loaded":len(study.model_ids),
        "synthetic_arm_traces":report.shadow.total_shadow_arm_wirings,
        "matched_books":report.matched_contexts,
        "book_manifest_sha256":report.book_manifest_sha256,
        "distinct_trace_hashes":len({a.visible_trace_sha256 for a in report.shadow.arms}),
        "real_model_inferences":report.model_inference_executed,
        "independent_oracle_labels":report.sealed_oracle_results,
        "authenticated_shared_sampling":report.authenticated_shared_sampling,
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
