"""Exercise 6 x 8 registered policy slots through the blind trace, offline.

Every policy factory here is IDENTICAL scripted placeholder behavior, not
one of eight research algorithms. 48 runs are wiring smoke checks, not real
LLM calls, task resolutions, hidden evaluations or performance comparisons.
"""
import json
from hashlib import sha256
from pathlib import Path

from ucode.blind_policy_trace import BlindAction, PublicToolReceipt
from ucode.experiment_contract import FrozenStudy
from ucode.shadow_assignment_parity import AssignedOpportunity
from ucode.shadow_eight_arm_runner import run_shadow_eight_arm_matrix
from ucode.task_view_boundary import parse_agent_task_view
from ucode.vector_policy import ResourceVector as RV

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = json.loads((ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
    spec = "SYNTHETIC ONLY: no external task or code."
    task = parse_agent_task_view({
        "repository":"synthetic/fixture", "base_sha":"a"*40,
        "prefixed_spec":spec, "spec_sha256":sha256(spec.encode()).hexdigest(),
    })
    cap = RV(tokens=30,test_calls=2,gpu_seconds=1,cpu_seconds=2,wall_seconds=3)
    study=FrozenStudy(
        (("SYNTHETIC_OFFLINE_TASK","SYNTHETIC_LINEAGE"),),
        tuple(p["model_ids"]),tuple(p["policy_ids"]),(11,),
        (("UNFROZEN_ILLUSTRATIVE",cap),))
    rows=tuple(AssignedOpportunity(
        task_id="SYNTHETIC_OFFLINE_TASK",lineage_group="SYNTHETIC_LINEAGE",
        model_id=model,policy_id=policy,seed=11,
        budget_id="UNFROZEN_ILLUSTRATIVE",
        pre_fix_base_sha40=task.base_sha,
        model_checkpoint_sha40="b"*40,
        task_spec_sha256=task.spec_sha256,
        public_candidate_archive_sha256="d"*64,
        common_opportunity_catalog_sha256="e"*64,
        tool_access_sha256="f"*64,
        environment_image_sha256="1"*64,
        resource_cap=cap,
    ) for model in study.model_ids for policy in study.policies)

    def fake_policy_factory(assignment):
        def policy(state):
            if not state.history:
                return BlindAction("generate", RV(tokens=10,cpu_seconds=1,wall_seconds=1))
            if len(state.history)==1:
                return BlindAction("test",RV(test_calls=1,wall_seconds=1))
            return BlindAction("release",RV())
        return policy

    def fake_tool_factory(assignment):
        def tool(action, view, existing, public_history):
            if action.kind=="generate":
                return PublicToolReceipt("generate",
                    RV(tokens=8,cpu_seconds=1,wall_seconds=1),
                    patch="SYNTHETIC patch placeholder")
            if action.kind=="test":
                return PublicToolReceipt("test",RV(test_calls=1,wall_seconds=1),
                                         feedback="SYNTHETIC public observation")
            raise ValueError("scripted fake tool only supports generate and test")
        return tool

    report=run_shadow_eight_arm_matrix(
        study,rows,{"SYNTHETIC_OFFLINE_TASK":task},
        {p:fake_policy_factory for p in study.policies},
        fake_tool_factory)
    print(json.dumps({
        "stage":report.stage,
        "shadow_wiring_runs":report.total_shadow_arm_wirings,
        "policy_slots":len(study.policies),
        "model_names_not_loaded":len(study.model_ids),
        "statuses":sorted(set(a.terminal_status for a in report.arms)),
        "declared_assignment_digest":report.declared_assignment_sha256,
        "oracle_results":report.independent_oracle_labels,
        "external_executions":report.authorized_external_executions,
        "real_task_successes":report.real_task_successes,
        "model_inferences":report.verified_model_inferences,
        "policy_fidelity_attested":report.policy_fidelity_attested,
        "hardware_metering_verified":report.verified_hardware_metering,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
