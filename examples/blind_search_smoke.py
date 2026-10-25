"""Replay a SYNTHETIC, visible-feedback-only coding action sequence.

The two fake patch hashes and diagnostic outcomes are hand-authored fixture
inputs. No external repository checkout, executable code, LLM inference,
evaluator oracle, actual token accounting, GPU resource or valid
experimental success label exists.
"""
import json
from pathlib import Path

from ucode.blind_search import (
    BlindPolicy, BlindState, blind_catalog_from_public_manifest,
    choose_blind, record_blind,
)
from ucode.vector_policy import ResourceVector


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/blind_search_synthetic_schedule_2026-10-25.json"
OBSERVED_FIXTURES = {"retrieve_1": True,
                     "test_candidate_v1": False,
                     "test_candidate_v2": True}
PATCH_FIXTURES = {"generate_v1": "a"*64,
                  "repair_v1": "b"*64}


def reproduce() -> dict:
    spec = json.loads(CONFIG.read_text(encoding="utf-8"))
    if spec.get("status") != "SYNTHETIC_FIRST_PARTY_NO_REPOSITORY_CODE_EXECUTED":
        raise ValueError("example must remain explicitly synthetic")
    actions = blind_catalog_from_public_manifest(spec["actions"])
    budget = ResourceVector(**spec["budget"])
    policy = BlindPolicy(spec["min_positive_tests"])
    state = BlindState(budget)
    events = []
    for _ in range(len(actions)+1):
        dec = choose_blind(state, actions, policy)
        events.append({"action":dec.action,"kind":dec.kind,
                       "budget_after_action":dec.budget_after_first.__dict__})
        if dec.terminal:
            break
        if dec.kind in ("generate","repair"):
            state = record_blind(
                state,actions,dec,
                new_candidate_sha256=PATCH_FIXTURES[dec.action],
                policy=policy,
            )
        else:
            state = record_blind(
                state,actions,dec,
                observed_positive=OBSERVED_FIXTURES[dec.action],
                policy=policy,
            )
    else:
        raise ValueError("unexpected search loop beyond available actions")
    if state.remaining.tokens < 0 or state.remaining.test_calls < 0:
        raise AssertionError("hard budget violation")
    return {
        "provenance": "HAND_AUTHORED_SYNTHETIC_NOT_MEASURED",
        "hidden_oracle_results": 0,
        "external_code_executions": 0,
        "actions": events,
        "terminal_action": events[-1]["action"],
        "candidate_patch_sha256": state.candidate_sha256,
        "spent_tokens_fixture": budget.tokens-state.remaining.tokens,
        "spent_test_calls_fixture": budget.test_calls-state.remaining.test_calls,
        "success_rate": None,
        "wrong_release_risk": None,
    }


if __name__ == "__main__":
    print(json.dumps(reproduce(), indent=2))
