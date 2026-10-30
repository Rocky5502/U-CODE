# U-CODE — history-to-belief replay boundary (31 October 2026)

**Evidence status:** first-party, offline, hypothetical Bayesian integrity check. **No real LLM evaluation, repository repair, external source execution, tool-log authentication, sealed evaluator or independently enforced resource meter.**

## Problem revealed by the MCEA code audit

The model-coherent evidence planner takes a typed `CoherentBeliefState` containing (i) the observed public diagnostic history, (ii) the joint posterior `P(Theta,Y | h)`, and (iii) remaining nominal resources. The mathematical planner intentionally supports arbitrary synthetic starting beliefs, so a caller could construct a posterior that does **not** follow the supplied observations. Directly passing that state from an agent/integration layer would create a **belief-integrity and potential evaluator-leakage pathway**.

The issue is not that the Bayesian update in `record_coherent_observation` is incorrect. The issue is the absence of a separate **replay check at the planning boundary** for externally serialized or transferred state.

## Implemented guard

`src/ucode/coherent_history_replay.py` introduces:

- `replay_coherent_history(frozen_start, claimed, probes, hypotheses)`
- `plan_verified_coherent_evidence(frozen_start, claimed, probes, hypotheses, prices, rule, ...)`

The guard starts from a separately supplied, empty-history initial belief, consumes each recorded public boolean observation exactly once, enforces action-catalog membership and nominal budget, retains scenario/kernel fingerprints, and requires the **entire** reconstructed joint posterior, budget, history and model identity to equal the claimed state. The validated wrapper calls the existing planner only after this test passes. It does not accept a user-provided `trusted=True` flag.

It is an **exact deterministic structural replay**, not a new inference algorithm or cryptographic verification. The checking function shares the update implementation with the model-coherent reference and therefore is *not* an independently proved Bayesian posterior oracle; that separate role is served by the exact-rational reference tests already in the repository.

## Adversarial falsifiers

`tests/test_coherent_history_replay.py` includes checks for a correct empty, one-step and two-step replay; agreement of verified/direct planning for a legitimate state; counterfeit acceptability posterior; false budget refund; false history sign; missing/duplicated action catalog; silently replaced conditional kernel; incorrect frozen prior; and starting states with existing observations. All examples are manually invented, with two latent diagnostic models and two visible actions.

### Integration requirements before any empirical use

1. Freeze and independently authenticate the initial prior, complete kernel table, model identity, probe catalog and task base **before** any held-out observation.
2. Protect the initial state separately from the runtime agent; **never** let a policy author supply both the start and its claimed result and treat equality as certification.
3. Bind each public diagnostic result to a separately authenticated action/candidate tool receipt; structural replay cannot prove the event actually occurred.
4. Keep evaluator-only gold labels physically isolated from all public beliefs and model fitting; use independent training repository lineages.
5. Verify five resource measurements and hard caps in an independently attested execution environment; this code checks only declared nominal costs.

**Falsifiable claim:** tampering with the posterior or resource history while retaining the same frozen start and visible observations must cause replay to fail closed, not a high-confidence release. No measurable real-world risk reduction is asserted.
