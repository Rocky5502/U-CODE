"""Fail-closed structural replay for model-coherent diagnostic belief states.

A caller-created CoherentBeliefState is NOT evidence of a valid Bayesian
history. This module deterministically derives the claimed state from a
separately supplied *frozen* starting state and public observation sequence.
Neither that starting state nor tool outputs are authenticated here: the
external runner must protect and bind both. No code, model or oracle executes.
"""
from __future__ import annotations

from typing import Sequence

from .coherent_hypothesis_search import (
    CoherentBeliefState, CoherentEvidencePlan, EvidenceHypothesis,
    kernel_fingerprint, plan_coherent_evidence, record_coherent_observation,
)
from .conditional_bes import ConditionalProbe, Observation
from .vector_policy import ResourcePrices
from .voi import ReleaseRule


def replay_coherent_history(
    frozen_start: CoherentBeliefState,
    claimed: CoherentBeliefState,
    probes: Sequence[ConditionalProbe],
    hypotheses: Sequence[EvidenceHypothesis],
) -> CoherentBeliefState:
    """Reconstruct the exact posterior, budget and observation chronology.

    The start must be supplied separately, BEFORE any diagnostic observation.
    All observations must correspond to single-use actions in the same typed
    catalog. A byte-for-byte-equivalent Python float state is required: the
    replay uses the same deterministic posterior and budget operations as
    the legitimate public update path; no approximate tolerance permits an
    unexplained posterior change.

    This checks INTERNAL consistency, not authenticity of the start, frozen
    kernels, public tool observations, repository task, or external evaluator.
    """
    if not isinstance(frozen_start, CoherentBeliefState) or not isinstance(
            claimed, CoherentBeliefState):
        raise TypeError("typed frozen start and claimed coherent state required")
    if frozen_start.history:
        raise ValueError("frozen starting state must precede every observation")
    if not isinstance(probes, (list, tuple)) or not isinstance(
            hypotheses, (list, tuple)):
        raise TypeError("typed frozen catalog and hypotheses required")
    catalog = tuple(probes)
    if len(catalog) > 6 or any(
            not isinstance(probe, ConditionalProbe) for probe in catalog):
        raise ValueError("bounded typed diagnostic catalog required")
    lookup = {probe.action_id: probe for probe in catalog}
    if len(lookup) != len(catalog):
        raise ValueError("duplicate frozen diagnostic IDs")
    if (claimed.scenario_ids != frozen_start.scenario_ids
            or claimed.kernel_fingerprints != frozen_start.kernel_fingerprints):
        raise ValueError("frozen scenario or likelihood identity drift")
    models = tuple(hypotheses)
    if (len(models) != len(frozen_start.scenario_ids)
            or any(not isinstance(model, EvidenceHypothesis) for model in models)
            or len({model.scenario_id for model in models}) != len(models)
            or set(model.scenario_id for model in models)
               != set(frozen_start.scenario_ids)):
        raise ValueError("frozen scenario ensemble identity mismatch")
    model_by_id = {model.scenario_id: model for model in models}
    for scenario_id, digest in zip(
            frozen_start.scenario_ids, frozen_start.kernel_fingerprints):
        if kernel_fingerprint(model_by_id[scenario_id].kernel) != digest:
            raise ValueError("frozen kernel fingerprint drift")
    if any(not isinstance(obs, Observation) for obs in claimed.history):
        raise ValueError("public history contains an untyped observation")

    result = frozen_start
    for observation in claimed.history:
        probe = lookup.get(observation.action_id)
        if probe is None:
            raise ValueError("history action not present in frozen catalog")
        result = record_coherent_observation(
            result, probe, hypotheses, observation.positive,
        )

    if result != claimed:
        raise ValueError(
            "claimed posterior, resource budget or history differs from replay"
        )
    return result


def plan_verified_coherent_evidence(
    frozen_start: CoherentBeliefState,
    claimed: CoherentBeliefState,
    probes: Sequence[ConditionalProbe],
    hypotheses: Sequence[EvidenceHypothesis],
    prices: ResourcePrices,
    rule: ReleaseRule,
    *,
    horizon: int = 2,
    max_states: int = 10000,
    release_gate: str = "all_surviving_models",
) -> CoherentEvidencePlan:
    """Plan only after reconstructing the claim from its public history.

    The legacy plan_coherent_evidence remains a mathematical reference for
    arbitrary hypothetical joint beliefs. Use THIS wrapper in any future
    integration that treats belief states as serialized agent observations.
    """
    checked = replay_coherent_history(
        frozen_start, claimed, probes, hypotheses,
    )
    return plan_coherent_evidence(
        checked, probes, hypotheses, prices, rule,
        horizon=horizon, max_states=max_states, release_gate=release_gate,
    )
