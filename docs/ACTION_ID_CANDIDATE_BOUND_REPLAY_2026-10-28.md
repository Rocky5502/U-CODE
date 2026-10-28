# U-CODE action-ID and candidate-target replay bridge — 28 October 2026

**Evidence status:** synthetic, source-free interface verification only.
**Do not count as an admitted task, real model run, measured trial, or
independent oracle evaluation.**

## Exact engineering gap closed

The previous frozen public book keyed each scripted response by action
**kind**, occurrence count, and candidate SHA. That was useful for a
smoke test but it was not identical to the richer `matched_opportunities.py`
model, where distinct `SearchAction.action_id` entries may share one kind,
each can be attempted only once, and diagnostics/repairs choose one
candidate in a shared archive.

The new `src/ucode/action_id_replay_bridge.py` provides a separate
synthetic-only bridge between these representations:

- A frozen action catalog of at most ten unique `SearchAction` IDs
  and typed five-resource reservations.
- `ActionBoundResponse` entries keyed by the **exact action ID and
  candidate SHA256**, not merely action kind/occurrence.
- A `SharedSession` archive and `matched_opportunities()` menu that
  rejects unaffordable actions, incorrect resource reservations,
  duplicate action attempts, absent candidate targets, and
  target mismatches **before** any response is consumed.
- `commit_shared()` produces traceable public candidate parentage,
  diagnostic receipts and a five-resource accounting ledger.
- Terminal release is allowed only for an archived candidate;
  `ABSTAINED`, missing frozen response and invalid action cases
  are separate statuses, never converted to task successes.
- Deterministic book and visible session trace SHA256 digests that
  contain no raw patch text or hidden correctness labels.

The smoke `scripts/smoke_action_id_replay_bridge.py` uses a single
scripted *generate -> diagnostic -> repair -> release* sequence
with immutable synthetic candidate SHA strings. It repeats that
script under all eight registered policy **names** solely to assert
replay consistency; it does **not** run or implement those eight
decision rules. `tests/test_action_id_replay_bridge.py` exercises
adversarial candidate swapping, wrong action ID/type, future
candidate references, duplicate reuse, inadequate budgets,
resource overruns, missing outcomes, and invalid release.

## Scientific limitations

This is a complementary, **non-executable interface bridge**; it
does not modify `BlindAction` or assert that a real LLM chose its
unique action. There is **no attested mapping** from live tool calls
to catalog IDs, no confidential production patch containment, and
no authenticated independent receipt ingestion. The frozen
`visible_positive` boolean is a *synthetic policy-visible diagnostic*,
NOT a held-out evaluator verdict. Candidate SHA strings are
fabricated references, not evaluated executable programs.
The apparent equality of eight scripted traces is not an
experimental effectiveness result or proof of control-fidelity.

Before confirmatory RQ3:
1. Have independent reviewers admit a rights-cleared, genuine
   pre-fix task and seal a separate full-task oracle.
2. Construct a trusted execution adapter that safely maps tool
   calls, candidate artifacts and unique action IDs; enforce tokens,
   test calls, GPU, CPU and wall time from independent metering.
3. Implement and fidelity-review all eight distinct policy
   algorithms; preserve common candidate opportunities and
   randomized/frozen seeds without oracle data in policy feedback.
4. Join evaluator-only verdicts after policy termination through
   the existing experiment contract; report all assigned runs,
   abstention and incomplete-case denominators.

## Reproduction (no external code)

```bash
python -m scripts.smoke_action_id_replay_bridge
python -m unittest discover -s tests -v
```

All commands use first-party offline logic, without downloading
models or executing untrusted task source.
