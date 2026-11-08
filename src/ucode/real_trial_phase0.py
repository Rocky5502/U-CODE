"""Fail-closed phase-0 readiness for a *future* real U-CODE experiment.

The only optional executable host command is a bounded read-only nvidia-smi
query on the operator's OWN machine. By default there is no subprocess,
download, external code import, GPU model load, model request, network call,
hidden-oracle access, approval, benchmark task execution, or spending.
Hardware telemetry is an untrusted local observation, NOT an attestation.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import subprocess
from typing import Mapping

from scripts.check_local_readiness import validate_local_preflight
from .model_readiness import validate_selected_manifest
from .pilot_preflight import build_pilot_preflight, ROOT
from .vector_policy import RESOURCE_FIELDS

_QUERY = (
    "nvidia-smi",
    "--query-gpu=name,memory.total,driver_version",
    "--format=csv,noheader,nounits",
)
_DRIVER = re.compile(r"^[0-9]{1,4}(?:[.][0-9]{1,4}){1,3}$")
_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .+_()/:-]{1,127}$")
_PHASE = "REAL_TRIAL_PHASE0_METADATA_AND_OPTIONAL_READONLY_HOST_SURVEY"


def _read_object(root: Path, relative: str) -> dict:
    obj = json.loads((root / relative).read_text(encoding="utf-8"))
    if type(obj) is not dict:
        raise ValueError("canonical study registry must be a JSON object")
    return obj


def read_only_nvidia_gpu_survey() -> dict:
    """Run ONLY a constant, read-only local NVIDIA CLI query on opt-in.

    Parsing detects ambiguous/garbled output rather than guessing. GPU name,
    memory and driver are *locally reported*, not independent or signed data.
    No GPU UUID, serial, hostname, device index, model weights or secret paths.
    """
    try:
        proc = subprocess.run(
            list(_QUERY),
            check=False, capture_output=True, text=True,
            timeout=6, stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "state": "NOT_OBSERVED_LOCAL_CLI_UNAVAILABLE",
            "local_gpu_report": [],
            "hardware_independently_attested": False,
        }
    if type(proc.returncode) is not int or proc.returncode != 0:
        return {
            "state": "NOT_OBSERVED_LOCAL_CLI_ERROR",
            "local_gpu_report": [],
            "hardware_independently_attested": False,
        }
    if (type(proc.stdout) is not str or len(proc.stdout) > 8192
            or not proc.stdout.strip()):
        raise ValueError("invalid or oversized local GPU query")
    items = list(csv.reader(proc.stdout.splitlines()))
    if not 1 <= len(items) <= 16:
        raise ValueError("expected one to sixteen locally reported NVIDIA GPUs")
    gpus = []
    for row in items:
        if len(row) != 3:
            raise ValueError("invalid NVIDIA GPU CLI fields")
        name, memory, driver = (x.strip() for x in row)
        if not _MODEL.fullmatch(name) or not _DRIVER.fullmatch(driver):
            raise ValueError("invalid locally reported NVIDIA model or driver")
        if not re.fullmatch(r"[0-9]{1,6}", memory):
            raise ValueError("GPU memory must be an integer count of MiB")
        mib = int(memory)
        if not 512 <= mib <= 1048576:
            raise ValueError("implausible locally reported GPU memory")
        gpus.append({
            "name_locally_reported": name,
            "memory_total_mib_locally_reported": mib,
            "driver_locally_reported": driver,
        })
    return {
        "state": "LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY",
        "local_gpu_report": gpus,
        "hardware_independently_attested": False,
    }


def build_real_trial_phase0(
    *,
    root: Path = ROOT,
    hypothetical_task_slots: int = 1,
    hypothetical_seed_count: int = 1,
    gpu_survey: Mapping | None = None,
) -> dict:
    """Cross-check all four frozen registries, then budget *hypothetical* slots.

    A slot count is a planning what-if, NEVER a registered or admitted task.
    This routine has no "approve" switch and cannot issue runner tokens.
    Budget vectors are per-arm *illustrative* upper envelopes; actual spend,
    enforceability, wall-clock duration and utilization are unmeasured.
    """
    if (type(hypothetical_task_slots) is not int
            or not 1 <= hypothetical_task_slots <= 20
            or type(hypothetical_seed_count) is not int
            or not 1 <= hypothetical_seed_count <= 3):
        raise ValueError("bounded hypothetical tasks [1,20] and seeds [1,3] required")
    if gpu_survey is not None:
        if (type(gpu_survey) is not dict
                or set(gpu_survey) != {
                    "state", "local_gpu_report", "hardware_independently_attested"
                }
                or gpu_survey["hardware_independently_attested"] is not False
                or gpu_survey["state"] not in (
                    "NOT_OBSERVED_LOCAL_CLI_UNAVAILABLE",
                    "NOT_OBSERVED_LOCAL_CLI_ERROR",
                    "LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY",
                )):
            raise ValueError("caller cannot insert authenticated hardware claims")
        # Caller-supplied survey is always untrusted, even if it has a valid
        # shape. A trusted host must separately authenticate its own devices.
        if (type(gpu_survey["local_gpu_report"]) is not list
                or len(gpu_survey["local_gpu_report"]) > 16):
            raise ValueError("invalid locally reported GPU observation count")
    root = Path(root)
    protocol = _read_object(root, "configs/confirmatory_sbse_protocol_2026-10-25.json")
    models = _read_object(root, "configs/accepted_six_model_study_2026-10-25.json")
    original_models = _read_object(root, "configs/models_v2_2026-10-24.json")
    local = _read_object(root, "configs/local_experiment_preflight_2026-10-29.json")
    with (root / "data/discovery/dataset_source_registry_v2_2026-10-24.csv").open(
            encoding="utf-8", newline="") as f:
        sources = list(csv.DictReader(f))
    local_audit = validate_local_preflight(local, models, protocol, sources)
    all_models = validate_selected_manifest(models, original_models)
    pilot = build_pilot_preflight(root)
    frozen_models = protocol.get("model_ids")
    frozen_policies = protocol.get("policy_ids")
    if (local_audit.get("status") != "BLOCKED_NOT_AUTHORIZED"
            or len(all_models) != 6
            or type(frozen_models) is not list or len(frozen_models) != 6
            or [r.model_id for r in all_models] != frozen_models
            or type(frozen_policies) is not list or len(frozen_policies) != 8
            or len(set(frozen_policies)) != 8
            or local_audit.get("independently_admitted_tasks") != 0
            or pilot.get("qualified_executable_tasks") != 0
            or pilot.get("pending_admission_checks") != 16
            or pilot.get("real_model_runs") != 0
            or protocol.get("status") != "PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"
            or protocol.get("qualified_task_ids") != []
            or protocol.get("seeds_frozen") is not False
            or protocol.get("final_budget_caps_frozen") is not False
            or protocol.get("model_revisions_frozen") is not False
            or protocol.get("policy_implementations_faithfully_reproduced") is not False
            or protocol.get("results_measured") is not False
            or protocol.get("external_code_executions") != 0
            or any(m.runnable for m in all_models)):
        raise ValueError("canonical frozen study/real-pilot blocker inconsistency")
    illustrative = protocol.get("planned_resource_caps_example_not_executed")
    if (type(illustrative) is not dict
            or set(illustrative) != {"B_pilot_illustrative"}):
        raise ValueError("illustrative only: exact canonical pilot budget required")
    budget = illustrative["B_pilot_illustrative"]
    if (type(budget) is not dict or set(budget) != set(RESOURCE_FIELDS)
            or any(type(budget[k]) is not int or budget[k] <= 0
                   or budget[k] > 1_000_000_000 for k in RESOURCE_FIELDS)):
        raise ValueError("canonical five-dimensional positive budget required")
    possible_seeds = protocol.get("assigned_seed_values_illustrative_not_final")
    if (type(possible_seeds) is not list or len(possible_seeds) < hypothetical_seed_count
            or any(type(x) is not int or x < 0 for x in possible_seeds)):
        raise ValueError("invalid illustrative seed count")
    one_seed = hypothetical_task_slots * len(frozen_models) * len(frozen_policies)
    all_slots = one_seed * hypothetical_seed_count
    return {
        "schema_version": "1.0",
        "stage": _PHASE,
        "experiment_initiated": False,
        "actual_task_assignments": 0,
        "approved_real_tasks": 0,
        "approved_hidden_oracles": 0,
        "real_llm_inferences": 0,
        "real_success_rate": None,
        "registered_model_count": len(frozen_models),
        "qualified_model_checkpoints": sum(r.runnable for r in all_models),
        "registered_policy_slots": len(frozen_policies),
        "faithful_real_policy_implementations_certified": 0,
        "first_party_offline_code_only": True,
        "model_blockers_by_id": [
            {"model_id": r.model_id, "blockers": list(r.blockers)} for r in all_models
        ],
        "gates_pending_php_and_go": pilot["pending_admission_checks"],
        "blocked_reason_classes": [
            "HISTORICAL_SOURCE_ERA_SPEC_AND_RIGHTS_NOT_INDEPENDENTLY_APPROVED",
            "EVALUATOR_ONLY_HIDDEN_ORACLE_NOT_INDEPENDENTLY_SEALED",
            "ISOLATED_ROOTLESS_REPRODUCIBLE_RUNNER_AND_FIVE_METERS_NOT_ATTESTED",
            "SIX_LICENSED_CHECKPOINTS_AND_CHAT_TEMPLATES_NOT_QUALIFIED",
            "EIGHT_POLICY_SOURCE_FIDELITY_AND_MATCHED_OPPORTUNITIES_NOT_PROVEN",
            "SEEDS_CAPS_AND_LINEAGE_SPLITS_NOT_FINALLY_FROZEN",
        ],
        "hypothetical_capacity_scenario_not_approved_or_scheduled": {
            "hypothetical_task_slots": hypothetical_task_slots,
            "illustrative_seeds_used": possible_seeds[:hypothetical_seed_count],
            "budget_id": "B_pilot_illustrative",
            "per_assignment_illustrative_cap": budget,
            "one_seed_six_model_eight_policy_slots": one_seed,
            "total_hypothetical_slots": all_slots,
            "aggregate_individual_resource_envelopes_not_measured": {
                k: all_slots * budget[k] for k in RESOURCE_FIELDS
            },
            "not_an_expected_execution_time_or_cost": True,
            "identical_declared_cap_is_not_verified_hardware_enforcement": True,
        },
        "local_hardware_survey": (
            gpu_survey if gpu_survey is not None else {
                "state": "NOT_PROBED_OPT_IN_REQUIRED",
                "local_gpu_report": [],
                "hardware_independently_attested": False,
            }
        ),
        "real_trial_authorized": False,
        "safe_next_actions": [
            "Run first-party metadata/host read-only checks without model download.",
            "Independently approve source-era task scope, file rights and sealed evaluator.",
            "On operator machine, obtain licenses/permissions and pin exact six revisions.",
            "Inspect rootless network-off sandbox, tools and physical five-resource meters.",
            "Freeze task-lineage splits, proposal opportunities, seeds, caps and policy fidelity.",
            "Only then schedule a separately authorized exploratory matched pilot.",
            "Keep the registered six-by-eight comparison and terminal ITT accounting separate.",
        ],
        "warning": (
            "This is a local preparation preview, not evidence of human approval, "
            "checkpoint load, security isolation, physical metering or task execution."
        ),
    }
