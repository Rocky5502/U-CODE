"""Validate U-CODE confirmatory SE registration WITHOUT running experiments.

It is deliberately impossible to turn a zero-task prospective plan into
a complete trial through this CLI. Models/policies are selected, not yet
verified executable. For real trials, separate signed task/oracle/runner
approval and measured receipts are prerequisites.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json"
SELECTED = ROOT / "configs/accepted_six_model_study_2026-10-25.json"
RESOURCE_NAMES = {"tokens", "test_calls", "gpu_seconds",
                  "cpu_seconds", "wall_seconds"}
REQUIRED_POLICIES = {
    "ucode_conditional_bes", "ucode_unconditional_bes",
    "no_uncertainty_search", "uncertainty_only", "fixed_testing",
    "selective_verification", "mcts_search", "replay_search",
}


def validate_prospective_protocol(spec: dict, selected: dict) -> dict:
    if spec.get("status") != "PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS":
        raise ValueError("provisional plan cannot self-declare executed trial")
    ids = spec.get("model_ids", [])
    src_ids = [x.get("model_id") for x in selected.get("models", [])]
    if len(ids) != 6 or len(set(ids)) != 6 or set(ids) != set(src_ids):
        raise ValueError("exactly six user-selected models must be preserved")
    policies = spec.get("policy_ids", [])
    if len(policies) != 8 or len(set(policies)) != 8 or set(policies) != REQUIRED_POLICIES:
        raise ValueError("eight specified policies and controls are required")
    for key in ("primary_treatment", "primary_comparator"):
        if spec.get(key) not in REQUIRED_POLICIES:
            raise ValueError("primary comparison not represented by policies")
    if spec["primary_treatment"] == spec["primary_comparator"]:
        raise ValueError("treatment and control must differ")
    if (spec.get("qualified_task_ids") != []
            or spec.get("qualified_lineage_groups") != {}
            or spec.get("task_admission_status") != "NONE_ATTESTED"
            or spec.get("results_measured") is not False
            or spec.get("external_code_executions") != 0):
        raise ValueError("unqualified real tasks/results cannot enter planned study")
    for field in (
        "model_revisions_frozen", "independent_oracles_sealed",
        "runner_isolated_and_attested", "seeds_frozen",
        "final_budget_caps_frozen",
        "policy_implementations_faithfully_reproduced",
    ):
        if spec.get(field) is not False:
            raise ValueError(field + " must remain false until audited")
    caps = spec.get("planned_resource_caps_example_not_executed")
    if not isinstance(caps, dict) or not caps:
        raise ValueError("hypothetical budget examples must be explicitly labeled")
    for budget in caps.values():
        if set(budget) != RESOURCE_NAMES:
            raise ValueError("all five budget dimensions must be present")
        if any(type(n) not in (int, float) or n < 0 for n in budget.values()):
            raise ValueError("resource caps must be finite nonnegative numbers")
    return {
        "status": "PROSPECTIVE_NOT_EXPERIMENTAL",
        "user_selected_model_checkpoints": len(ids),
        "prospectively_listed_policies": len(policies),
        "qualified_tasks": 0,
        "independent_oracle_results": 0,
        "external_comparator_adapters_implemented": 0,
        "measured_policy_effects": 0,
    }


def main():
    spec = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    print(json.dumps(validate_prospective_protocol(spec, selected), indent=2))


if __name__ == "__main__":
    main()
