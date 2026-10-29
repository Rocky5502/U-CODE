"""Fail-closed offline local study configuration audit.

This script is not a model server, task-admission authority, or security
attestation. It only checks that prospective configurations are coherent and
*remain blocked*. Never use its exit code as authorization for execution.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/local_experiment_preflight_2026-10-29.json"
MODELS = ROOT / "configs/accepted_six_model_study_2026-10-25.json"
PROTOCOL = ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json"
DATASETS = ROOT / "data/discovery/dataset_source_registry_v2_2026-10-24.csv"

_TOP = frozenset((
    "schema_version", "status", "created_on", "authoritative_model_registry",
    "authoritative_protocol", "external_source_registry", "planned_model_ids",
    "planned_policy_ids", "primary_treatment", "primary_comparator",
    "training_or_trial_approved", "allowed_to_download_weights",
    "allowed_to_execute_upstream_code", "allowed_to_access_sealed_oracle",
    "local_server_address", "hardware_observation", "gates",
    "local_model_overrides", "experiment_assignments", "outcomes_measured",
    "notes",
))
_HW = frozenset(("observed", "gpu_name", "actual_vram_gb",
                 "driver_version", "engine_version"))
_OVERRIDE = frozenset(("model_id", "checkpoint_revision",
                       "tokenizer_revision", "local_weight_path",
                       "quantization", "engine", "load_test_verified"))
_GATES = frozenset((
    "independent_task_admission", "independent_rights_review",
    "source_era_spec_attested", "hidden_oracle_sealed",
    "runner_isolated_and_attested", "five_resources_measured",
    "full_model_licenses_approved", "checkpoint_revisions_pinned",
    "policy_implementations_faithful",
))
_CANONICAL_PATHS = {
    "authoritative_model_registry":
        "configs/accepted_six_model_study_2026-10-25.json",
    "authoritative_protocol":
        "configs/confirmatory_sbse_protocol_2026-10-25.json",
    "external_source_registry":
        "data/discovery/dataset_source_registry_v2_2026-10-24.csv",
}


def validate_local_preflight(
    config: Mapping, selected: Mapping, protocol: Mapping, datasets: list[Mapping]
) -> dict:
    """Require exactly the planned six models/eight policies and *zero* approval.

    A new real-run configuration needs an independent, versioned scientific
    protocol; mutating this frozen negative-evidence preflight cannot
    grant that authorization.
    """
    if type(config) is not dict or set(config) != _TOP:
        raise ValueError("local configuration schema drift or secret injection")
    if (config["schema_version"] != "1.0"
            or config["status"] != "PROSPECTIVE_LOCAL_CONFIGURATION_ONLY_BLOCKED"
            or config["created_on"] != "2026-10-29"):
        raise ValueError("local preflight can only represent the original blocked stage")
    for key, expected in _CANONICAL_PATHS.items():
        if config[key] != expected:
            raise ValueError("canonical relative research source path changed")
    if (type(selected) is not dict or type(protocol) is not dict
            or selected.get("phase") !=
            "ALL_SIX_SELECTED_FOR_PLANNING_NOT_READY_FOR_INFERENCE"
            or protocol.get("status") !=
            "PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"):
        raise ValueError("authoritative study registries not in prospective state")
    m = selected.get("models")
    p = protocol.get("policy_ids")
    if type(m) is not list or len(m) != 6 or type(p) is not list or len(p) != 8:
        raise ValueError("six-model eight-policy roster required")
    model_ids = [row["model_id"] for row in m]
    if (len(set(model_ids)) != 6 or
            config["planned_model_ids"] != model_ids or
            protocol.get("model_ids") != model_ids):
        raise ValueError("selected model roster must exactly match canonical")
    if (len(set(p)) != 8 or config["planned_policy_ids"] != p):
        raise ValueError("planned policies must exactly match canonical")
    if (config["primary_treatment"] != protocol.get("primary_treatment")
            or config["primary_comparator"] != protocol.get("primary_comparator")):
        raise ValueError("changed preregistered primary comparison")
    if type(datasets) is not list or len(datasets) != 13:
        raise ValueError("thirteen source leads required, not runnable tasks")
    expected_cols = {
        "dataset", "unit", "primary_url", "access_state", "license_rights",
        "oracle_status", "local_execution", "distinct_cohort", "risk_or_limit",
    }
    if (any(type(row) is not dict or set(row) != expected_cols for row in datasets)
            or len({row["dataset"] for row in datasets}) != 13
            or any(row["local_execution"] != "not_executed" for row in datasets)):
        raise ValueError("dataset registry is no longer unexecuted source leads")
    for field in (
        "training_or_trial_approved", "allowed_to_download_weights",
        "allowed_to_execute_upstream_code", "allowed_to_access_sealed_oracle",
        "outcomes_measured",
    ):
        if config[field] is not False:
            raise ValueError("a planning file cannot self-authorize actions")
    if config["experiment_assignments"] != 0 or type(config["experiment_assignments"]) is not int:
        raise ValueError("no assigned experiments exist in this preflight")
    if config["local_server_address"] != "127.0.0.1":
        raise ValueError("only offline loopback address permitted in planning config")
    hw = config["hardware_observation"]
    if (type(hw) is not dict or set(hw) != _HW
            or hw["observed"] is not False
            or any(hw[k] is not None for k in _HW - {"observed"})):
        raise ValueError("unmeasured hardware must not be fabricated")
    gates = config["gates"]
    if type(gates) is not dict or set(gates) != _GATES:
        raise ValueError("missing or extra independently gated condition")
    if any(gates[k] is not False for k in _GATES):
        raise ValueError("prospective file cannot self-certify a gate")
    overrides = config["local_model_overrides"]
    if (type(overrides) is not list or len(overrides) != 6
            or [row.get("model_id") for row in overrides] != model_ids):
        raise ValueError("model overrides must preserve exact six identities/order")
    for row in overrides:
        if type(row) is not dict or set(row) != _OVERRIDE:
            raise ValueError("model override schema drift or unsafe fields")
        if (any(row[name] is not None for name in
                ("checkpoint_revision", "tokenizer_revision",
                 "local_weight_path", "quantization", "engine"))
                or row["load_test_verified"] is not False):
            raise ValueError("unverified model snapshot cannot be promoted")
    if type(config["notes"]) is not str or not config["notes"].strip():
        raise ValueError("missing limitation text")
    return {
        "status": "BLOCKED_NOT_AUTHORIZED",
        "source": "OFFLINE_FIRST_PARTY_PROSPECTIVE_CONFIG",
        "model_ids": model_ids,
        "policy_ids": p,
        "external_dataset_candidates": 13,
        "independently_admitted_tasks": 0,
        "sealed_oracles": 0,
        "measured_model_loads": 0,
        "gates_pending": sorted(_GATES),
        "safe_to_execute_third_party_code": False,
        "authorized_to_rent_gpu": False,
        "experiment_outcomes": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    args = parser.parse_args()
    with DATASETS.open(newline="", encoding="utf-8") as f:
        sources = list(csv.DictReader(f))
    result = validate_local_preflight(
        json.loads(args.config.read_text(encoding="utf-8")),
        json.loads(MODELS.read_text(encoding="utf-8")),
        json.loads(PROTOCOL.read_text(encoding="utf-8")),
        sources,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
