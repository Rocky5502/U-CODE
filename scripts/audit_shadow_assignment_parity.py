"""Reproduce an illustrative 6-by-8 two-seed assignment parity check.

All task identifiers and SHA-shaped fingerprints in this demonstration are
clearly synthetic, not real model revisions, third-party approvals or traces.
"""
import json
from pathlib import Path

from ucode.experiment_contract import FrozenStudy
from ucode.shadow_assignment_parity import AssignedOpportunity, audit_shadow_assignment_parity
from ucode.vector_policy import ResourceVector

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json"


def main():
    protocol = json.loads(PROTOCOL.read_text("utf-8"))
    cap = ResourceVector(tokens=100, test_calls=2, gpu_seconds=5,
                         cpu_seconds=5, wall_seconds=10)
    study = FrozenStudy(
        (("SYNTHETIC_ONLY_NONEXECUTABLE", "SYNTHETIC_LINEAGE"),),
        tuple(protocol["model_ids"]), tuple(protocol["policy_ids"]),
        (11,29), (("ILLUSTRATIVE_UNFROZEN_BUDGET",cap),))
    rows = tuple(AssignedOpportunity(
        task_id=task,lineage_group="SYNTHETIC_LINEAGE",
        model_id=model,policy_id=policy,seed=seed,
        budget_id=budget,pre_fix_base_sha40="a"*40,
        model_checkpoint_sha40="b"*40,task_spec_sha256="c"*64,
        public_candidate_archive_sha256="d"*64,
        common_opportunity_catalog_sha256="e"*64,
        tool_access_sha256="f"*64,
        environment_image_sha256="1"*64,resource_cap=cap,
    ) for task,model,seed,budget,policy in (
        (t,m,s,b,p) for t,_ in study.task_lineages
        for m in study.model_ids for s in study.seeds
        for b,_ in study.budgets for p in study.policies))
    result = audit_shadow_assignment_parity(study,rows)
    print(json.dumps({
        "status":result.status,
        "assignment_count":result.verified_shadow_assignments,
        "matched_contexts":result.matrix_pairs,
        "policies_per_context":result.policies_per_pair,
        "declared_hash_only":result.declared_assignment_digest,
        "real_models_executed":0,
        "independent_evaluator_results":0,
        "real_tasks_admitted":0,
    },indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
