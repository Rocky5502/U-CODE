# Shared candidate archive and conditional BES adapter — research ledger

**Date:** 2026-10-26. **Status:** first-party offline engineering milestone; not a model/task effectiveness experiment, not a completed fair search comparison.

## Why this step

Previously, the optimized uncertainty-free beam controller retained multiple SHA256 candidate patches, while `conditional_bes.py` studied diagnostics for a single candidate. The difference invalidated any claim that the two controllers had identical candidate/release opportunities. This round introduces a common immutable archive/visible action ledger, and a **candidate-indexed conditional reference adapter** so that both policies can operate on exactly the same artifact identities and action catalog in offline tests.

## Implemented

- `src/ucode/matched_session.py`:
  `SharedSession(initial_budget, SearchState, SharedReceipt[], max_candidates)` with common patch SHA identity, repair parent links, old-patch evidence retained only for the originating SHA, and one-use action IDs. Typed `SharedDecision` requests are subject to the frozen catalog, independent five-component nominal affordability and reported five-component consumption cap. A failed candidate-production attempt consumes reported resources and does not fabricate an artifact. The entire ledger reconciles, and visible trace SHA256 changes with consumed budgets.
- `baseline_shared_decision` and `record_baseline_shared` call the **original** `choose_search` algorithm through this shared state; they do not add probabilities or latent oracle outcomes to its view.
- `src/ucode/conditional_archive.py`:
  `plan_conditional_archive` reconstructs per-candidate posteriors from frozen candidate priors and **exact visible diagnostic history** through the existing `record_conditional`/ `plan_conditional` algorithms. It evaluates possible diagnostics separately for each archived candidate and one-step frozen `CandidateAction` generation/repair scenarios against the current best terminal alternative. All predicted probabilities are **hypothetical train-only externally supplied inputs**, isolated from the uncertainty-free view. `record_conditional_archive` rejects forged off-policy steps.
- `audit_shared_start`: checks both policy arms start with **the same action IDs/kinds/nominal five-vector costs**, exact initial five-vector budgets, candidate capacity and original candidate SHA archive. Audit is performed before either policy executes; its digest is a reproducibility anchor, not proof of matched inference or physical sandbox enforcement.
- `tests/test_matched_session.py`: tests both policy paths on the same synthetic archive and evidence; checks all five reported resource limits, nominal-vs-reported accounting, stale evidence, candidate lineage, immutable action history, incomplete kernels, duplicate priors, missing candidate forecasts, budget and archive mismatch, permutation determinism, and a negative counterexample in which a blind positive-test release policy and a low-posterior conditional policy disagree.

## Decision-theoretic limitations

The conditional archive adapter is **NOT a new globally optimal multicandidate conditional BES**:

1. `conditional_bes.py` remains a finite-horizon **single-patch diagnostic** Bellman reference. The adapter takes the best predicted terminal value among archived candidates as an outside option but only computes a candidate-specific, not fully joint, diagnostic continuation; it cannot plan arbitrary interleavings of testing multiple candidates and generating repairs.
2. New candidate transitions are **one-step** frozen scenario forecasts. They do not sample actual models, guarantee generation success, or propagate a fully calibrated conditional transition kernel. An action with no frozen forecast is not silently granted favorable future patches. This is a deliberate conservative limitation for the uncertainty-aware prototype, NOT a limitation of the baseline's capability.
3. `SharedReceipt.reported_cost` is **caller-reported, not trusted actual measured runtime**; it does not enforce Linux cgroups, CUDA accounting, host wall-time limits, API token billing or malicious subprocess isolation. Any real receipt must be independently measured/enforced by the later approved runner and authenticated before joining the `experiment_contract.py` evaluator. Offline fairness is a necessary **opportunity-level** condition only.
4. `audit_shared_start` does not verify identical prompts, decoding, random sampling opportunities, checkpoint revisions, retrieval corpus, candidate quality, tool implementations, seed mapping, or model-runner snapshot. These must be made identical through a frozen paired executor contract.
5. A baseline's positive visible unit test is not a sealed independent acceptance oracle. The conditional predicted risk gate is not a statistical risk guarantee. Both release policies may be wrong; zero release coverage leaves wrong-release conditional risk undefined.
6. No real task is independently admitted. PHP #104 and Go #43 continue to have all eight gate instances pending each; **zero external repository programs run**. Six prospective model checkpoints and eight policy IDs are unchanged.

## Falsifiers and next experiments

- **Necessary engineering gate:** introduce an isolated, physically metered policy-neutral executor that issues the same generation/retrieval/test/analysis/repair opportunities to both policies. It must be impossible for either policy to read sealed oracle artifacts, and actual token/test/GPU/CPU/wall costs must be independently captured rather than self-reported.
- **Algorithmic gate:** extend conditional BES to truly joint multicandidate cross-candidate intervention planning with candidate-specific evidence kernels and bounded search complexity; compare it to an equally tuned uncertainty-free beam/MCTS search under the identical action and archive rules. The current adapter is a **bridge**, not completion of this gate.
- **Calibration/data gate:** fit the probability kernels using disjoint training repository/fork families only. Preregister tuning budgets, initial candidate generation, release/coverage floor and primary endpoint before evaluating sealed task families. Include synthetic cases where the uncertainty-blind controller's release differs from the posterior gate and where conditional evidence is redundant; never place these synthetic outcomes in manuscript Results.
- **Safety gate:** no third-party repository execution until independent file-level rights, immutable pre-fix specification, line-level attribution, independent sealed oracle, pinned toolchain, and approved rootless network-off sandbox are verified and signed outside the self-reported JSON process.

**Journal source:** `paper/overleaf/main.tex`. The `Results` section remains intentionally empty. Live Overleaf and publisher `sn-jnl.cls` compilation have not been verified.
