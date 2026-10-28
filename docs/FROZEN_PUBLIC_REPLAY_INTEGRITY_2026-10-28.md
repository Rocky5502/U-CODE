# Frozen synthetic PUBLIC response replay — 28 October 2026

**Scope: OFFLINE INTERFACE INTEGRITY ONLY.** No admitted task, actual LLM
inference, third-party repository checkout, executable oracle, approved
hardware meter or measured effectiveness result.

## What changed

`src/ucode/frozen_public_replay.py` introduces an immutable
`SyntheticReplayBook` with bounded `FrozenPublicOutcome` rows, each
indexed by (action kind, occurrence ordinal, prior candidate SHA256).
Actions that inspect or repair an existing patch cannot accidentally
consume observations recorded for a different candidate. Generative
draws are frozen by their within-arm ordinal, never resampled for
each policy. Missing or duplicate entries are rejected rather than
silently falling back to ad-hoc model output or a hidden evaluator.

One replay book per (task, model, seed, budget) group is shared
by ALL eight registered policy arms. Exact opportunity-catalog hashes
must agree with the prospective M4 `AssignedOpportunity` declarations;
the entire assignment grid and all books are validated BEFORE any
policy callback is constructed. A canonical digest fingerprints
the supplied PUBLIC synthetic response book, including declared
five-vector resource consumption and reservations. The digest is not
a trusted attestation of independently captured hardware usage.
The adapter does not execute or obtain new outcomes, and callbacks
can still be unsafe in other environments.

The `run_shared_frozen_replay` integration reuses the previously
validated `run_shadow_eight_arm_matrix` and `run_blind_policy`
interfaces. All task views must be synthetic and the results remain
`RELEASED_PENDING_INDEPENDENT_EVALUATION`, `ABSTAINED`,
`TOOL_FAILED_COST_UNVERIFIED`, etc. These statuses never become
independent correctness labels. All model identities are NAMES ONLY,
not loaded checkpoints. The original six model identities and eight
confirmatory arms were not changed.

## How to reproduce, without downloading anything

```bash
python -m scripts.smoke_frozen_public_replay
python -m unittest discover -s tests -v
```

The smoke uses exactly 6 selected model names x 8 registered policy
names = **48 synthetically replayed arms** on one artificial
task and one illustrative seed. The same artificially constructed
candidate text, diagnostic result and reported costs are served
for a common action/candidate/ordinal across policies.
This is not 48 independent benchmark instances or model samples.

The accompanying unit tests adversarially check missing book
groups, unequal catalog IDs, incorrect candidate targets, missing
ordinal draws, duplicate keys, cost/reservation conflicts,
unsafe non-synthetic text, actual repo rejection and differing
policy abstention. All tests must pass on both Python 3.10 and 3.12.

## Scientific and security limits

- A static public replay book is a **common-random-number fixture**,
  not a proven model-conditioned production trace. Real candidate
  proposals may depend on intervening policy prompts, repairs,
  stateful tools and context windows. Additional independent capture
  and versioned replay are required before asserting true
  opportunity equivalence.
- Existing `BlindAction` includes action kind and vector cap but not
  a unique action/catalog ID. Ordinal + candidate matching reduces
  substitution risk but is not a faithful integration with the
  target-aware `matched_session.py` action semantics. That richer
  mapping is a remaining engineering task.
- The synthetic patch/feedback must start with `SYNTHETIC `.
  This is a *type-level convention*, not proof that an arbitrary
  malicious string is free of secrets or oracle leaks.
- Policy factories remain ordinary Python callables; the
  function alone cannot confine filesystem/network effects or
  attest a sandbox. No real repository is authorized.
- Actual measured five-resource caps need independent
  metering. The frozen consumption vectors are fabricated
  fixture values and cannot support cost/performance claims.
- Independent external reviewer approval of PHP #104 remains
  **pending**. No sealed hidden oracle has been constructed.
- The eight policy slots are still mostly placeholder adapters;
  this new module does NOT claim eight faithful methods or an
  observed comparative benefit.

**Next research work:** map frozen unique action IDs and candidate
provenance from `matched_opportunities.py` into the shared trace;
implement and fidelity-check registered policy adapters; obtain a
rights-reviewed admitted task and sealed independent oracle; then
conduct a genuinely metered paired study. Keep no-result and
rejection statuses visible in the full intention-to-treat denominator.
