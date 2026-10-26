# Stronger uncertainty-free search: bounded heuristic beam comparator

**Date:** 2026-10-26. **Stage:** committed first-party/offline reference, not an empirical or independently qualified model benchmark.

## Question and honest status

The primary registered policy ID is `no_uncertainty_search`. The previous
`blind_search.py` is a precommitted **fixed-schedule negative control**, not
the main comparator. `optimized_search.py` now supplies a different
**adaptive depth-limited beam search** over the same kinds of actions and
nominal five-component tool costs. It keeps a content-hash candidate archive,
binds diagnostic feedback to its original patch, replans after actual visible
results, and scores possible tool *opportunities* using frozen heuristics.

**Do not confuse an implemented strongER reference with a fully optimized,
tuned real-agent control.** Its current weights are illustrative, its future
tool outcomes are unknown, there is no real LLM/tool adapter or independent
oracle run, and its archive is not yet matched by conditional BES.
No model effectiveness, correctness, risk or runtime savings are measured.

## Interface and nonleakage contract

- `SearchAction(action_id, kind, ResourceVector)`: GENERATE, REPAIR, TEST,
  STATIC_ANALYSIS and RETRIEVE; IDs are one-use; each intervention spends a
  positive nonzero nominal cost and must fit **tokens, test_calls,
  gpu_seconds, cpu_seconds, wall_seconds separately**.
- `SearchCandidate(sha256, created_by, parent_sha256)`: immutable content
  fingerprint, append-only archive, explicit parent on repair.
- `SearchObservation(action_id, candidate_sha256, kind, positive)`:
  **visible** boolean tool result; not a hidden correctness oracle.
  Observations of patch A do not become evidence about repaired patch B.
- `SearchPolicy`: positive finite heuristic weights, depth 1–4, beam width
  1–64, archive capacity 1–32, minimum visible passing tests and planning
  prices. **Freeze and tune on training groups only; never tune on evaluation
  oracle outcomes.** Current defaults are not tuned.
- `choose_search`: deterministic, input-order-invariant heuristic beam
  scoring of feasible future action sequences; no posterior, prior,
  calibration likelihood, model forecast or gold label field. Future
  generation is treated as a *possible* candidate opportunity, not a
  guaranteed successful code artifact. Branches are **not** stochastic
  expected-value branches.
- `record_search`: verifies exact chosen action/charge; invalid generation
  may produce no candidate and still consumes nominal budget, then replans.
  Duplicate SHA and forged diagnostic generation fail closed.
- `search_catalog_from_public_manifest`: strict public-schema allowlist,
  refusing `confidence`, `oracle_passed`, `predicted_success`,
  `sensitivity`, `gold_patch`, hidden-test fields and ALL unknown fields.

The deterministic beam search is an **approximation for a surrogate
combinatorial allocation score**, not an optimal solver for software success,
Bayes utility, selective reliability or general POMDPs. The default heuristic
weights encode researcher preference for exploration, tests and repair after
visible failure, not an estimate of true patch acceptability. No test/analysis
observation is automatically a trustworthy external full-task oracle.

## Algorithmic reference

Given visible state `s`, remaining actions `A`, five-vector budget
`b`, and frozen heuristic weights `w`, choose a feasible sequence
`(a_1,...,a_h)` with `h <= depth` that maximizes

    proxy(path) = sum_k [ w[kind(a_k)] + visible_state_bonus(a_k)
                          + first_use_kind_bonus(a_k)
                          - resource_prices dot nominal_cost(a_k) ].

Each transition independently checks all five cost components; generate
and repair are not admissible after the archive capacity is reached, and
test/retrieve/static/repair require a current candidate. Future actions
are scheduled conditional on successful candidate creation, but if real
creation fails the policy replans with the actual no-candidate state.
The beam keeps at most `beam_width` highest proxy paths per depth,
with stable action-ID tie breaks; it considers at most 16 actions,
search depth <=4, and stops above 10,000 expansion attempts.
An upper-bound per-iteration comparison cost is
`O(depth * beam_width * action_count * log(beam_width*action_count))`;
it does not certify global surrogate optimality.

A patch is eligible for `release` only after at least the predeclared
number of **positive visible test results attached to THAT SAME SHA**,
and no failed visible test/static result attached to it. Multiple patches
remain in the archive, including failed candidates; any eligible archived
candidate can be selected as the final release. This is a heuristic
release rule, **not** correctness proof or risk control. If no positive
surrogate plan remains, release a passing archived patch or abstain.

## Exact parity achieved and parity NOT yet achieved

`matched_action_inventory.audit_optimized_action_parity` reuses the same
sorted action ID/kind/cost and initial five-budget SHA256 fingerprint as
the original fixed-schedule comparison. It prevents extra actions,
swapped tool kind, changed cost on any resource and mismatched budgets.
Static action opportunities are necessary but **not sufficient**:

1. **Unmatched architecture:** optimized baseline archives and may release
   older candidates; current single-candidate BES and diagnostic-only
   conditional BES do not. This is explicitly an advantage offered to the
   baseline, not grounds to claim fairness. Implement a common candidate
   archive and candidate selection semantics in a future U-CODE planner.
2. **Unmatched real generation:** there are no shared pinned prompts,
   pretrained checkpoint revisions, sampling seeds, tokenization, actual
   candidate pools, or identical tool implementations.
3. **Unmeasured true costs:** this module charges planning/nominal cost.
   Independent measured realized costs and sandbox enforcement remain
   the responsibility of an approved runner and
   `experiment_contract.py`. The price vector cannot override hard caps.
4. **No optimization fairness yet:** tune both methods using disjoint
   training/validation repo families under a fixed search/tuning
   budget. Freeze weights/hyperparameters, budget levels, selection
   criteria and one primary contrast *before* held-out evaluation.
5. **No physical evaluator isolation or oracle approval yet:** the two
   pinned PHP/Go dossiers still have all eight gates pending each.
   Do not execute their repository source or use PR-authored tests as gold.

## Required falsifiers before publication

- Compare against a version with genuine fixed-budget hyperparameter tuning,
  the existing fixed-schedule control, and external MCTS/replay/selective
  verifier baselines only after faithful adapters and tuning are available.
- Construct an **identical shared candidate/opportunity executor** for
  conditional BES and baseline. Diff per-task emitted action menus,
  allowed candidate pool, tool rights, sample proposals and measured
  five-cost receipts. An action ID SHA match alone is insufficient.
- Independently test cases in which blind heuristic beam succeeds and
  conditional BES fails; preserve negative effects.
- Report intention-to-treat full-task success, release coverage,
  conditional wrong-release risk (undefined at zero coverage), resource
  consumption, cluster effects and timeouts only from independently sealed,
  rights-approved real tasks. All current smoke/unit tests are synthetic.

**CI safety:** first-party Python/offline fixtures only. No third-party
repository program, gated model, paid inference or hidden evaluator is run.
