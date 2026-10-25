"""Audit action-opportunity parity between BES and uncertainty-blind search.

Prediction parameters in BES (patch prior, candidate transition likelihood,
test sensitivity/specificity) are *deliberately omitted* from the common
action manifest. Equal frozen action ID/kind/cost and initial budget are a
necessary, NOT sufficient condition for fair real-agent comparisons.
The two policies may select different actions or spend different totals.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Sequence

from .blind_search import BlindAction
from .budgeted_belief_search import EvidenceAction, CandidateAction
from .vector_policy import ResourceVector, RESOURCE_FIELDS


@dataclass(frozen=True)
class MatchedInventory:
    action_count: int
    action_ids: tuple[str, ...]
    resource_components: tuple[str, ...]
    action_opportunity_sha256: str
    initial_budget: ResourceVector
    comparison_scope: str = "PREEXECUTION_ACTION_PARITY_ONLY_NOT_MATCHED_REAL_INFERENCE"


def audit_action_parity(
    forecast_actions: Sequence[EvidenceAction | CandidateAction],
    blind_actions: Sequence[BlindAction],
    *,
    bes_initial_budget: ResourceVector,
    blind_initial_budget: ResourceVector,
) -> MatchedInventory:
    """Refuse added tools, altered action costs, swapped types and budgets."""
    if not isinstance(bes_initial_budget, ResourceVector) or not isinstance(
            blind_initial_budget, ResourceVector):
        raise ValueError("both initial hard budgets must be five-component vectors")
    if bes_initial_budget != blind_initial_budget:
        raise ValueError("matched policies start with different hard vector budgets")
    forecast_actions = tuple(forecast_actions)
    blind_actions = tuple(blind_actions)
    if not forecast_actions or not blind_actions:
        raise ValueError("action-opportunity registries must be nonempty")
    if any(not isinstance(a,(EvidenceAction,CandidateAction)) for a in forecast_actions):
        raise ValueError("all BES actions must be typed")
    if any(not isinstance(a,BlindAction) for a in blind_actions):
        raise ValueError("all blind actions must be typed")
    bes_index = {x.action_id: x for x in forecast_actions}
    blind_index = {x.action_id: x for x in blind_actions}
    if len(bes_index) != len(forecast_actions) or len(blind_index) != len(blind_actions):
        raise ValueError("duplicate actions cannot prove fair opportunity parity")
    if set(bes_index) != set(blind_index):
        raise ValueError("mismatched action IDs/available tools across policies")
    manifest = []
    for aid in sorted(bes_index):
        ba, ca = bes_index[aid], blind_index[aid]
        if ba.kind != ca.kind:
            raise ValueError("mismatched action kind: " + aid)
        if ba.cost != ca.cost:
            raise ValueError("mismatched action resource costs: " + aid)
        manifest.append({
            "action_id": aid, "kind":ba.kind,
            "cost": {k:getattr(ba.cost,k) for k in RESOURCE_FIELDS},
        })
    immutable = {"actions":manifest,
                 "budget":{k:getattr(bes_initial_budget,k)
                           for k in RESOURCE_FIELDS}}
    digest=sha256(json.dumps(immutable,sort_keys=True,
                            separators=(",",":")).encode("utf-8")).hexdigest()
    return MatchedInventory(
        len(manifest), tuple(sorted(bes_index)), tuple(RESOURCE_FIELDS),
        digest, bes_initial_budget,
    )
