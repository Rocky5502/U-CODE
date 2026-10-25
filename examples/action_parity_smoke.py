"""First-party PREEXECUTION action parity proof for synthetic forecast vs blind.

The probabilistic forecasts are invented parameters; they are not model
measurements or oracle labels. Only static tool/action catalog parity is
checked, NOT dynamic equivalence of implemented agents.
"""
import json
from pathlib import Path

from ucode.blind_search import blind_catalog_from_public_manifest
from ucode.budgeted_belief_search import (
    EvidenceAction, CandidateAction, CandidateScenario,
)
from ucode.matched_action_inventory import audit_action_parity
from ucode.vector_policy import ResourceVector

CONFIG=(Path(__file__).resolve().parents[1]
        /"configs/blind_search_synthetic_schedule_2026-10-25.json")


def reproduce_parity() -> dict:
    conf=json.loads(CONFIG.read_text(encoding="utf-8"))
    if conf["status"] != "SYNTHETIC_FIRST_PARTY_NO_REPOSITORY_CODE_EXECUTED":
        raise ValueError("do not relabel a fake smoke trial as an experiment")
    blind=blind_catalog_from_public_manifest(conf["actions"])
    forecasts=[]
    for action in blind:
        if action.kind in {"generate","repair"}:
            forecasts.append(CandidateAction(
                action.action_id,action.kind,
                (CandidateScenario(1,0.5),), action.cost))
        else:
            forecasts.append(EvidenceAction(
                action.action_id,action.kind,
                0.8,0.8,action.cost))
    budget=ResourceVector(**conf["budget"])
    same=audit_action_parity(
        forecasts, blind,
        bes_initial_budget=budget,
        blind_initial_budget=budget,
    )
    return {
        "scope":same.comparison_scope,
        "action_count":same.action_count,
        "ordered_action_ids":list(same.action_ids),
        "same_five_resource_budget":True,
        "opportunity_digest":same.action_opportunity_sha256,
        "real_model_runs":0,
        "measured_effectiveness":None,
    }


if __name__=="__main__":
    print(json.dumps(reproduce_parity(),indent=2))
