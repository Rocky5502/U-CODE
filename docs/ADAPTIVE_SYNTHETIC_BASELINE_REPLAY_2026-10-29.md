# U-CODE — adaptive public-evidence baseline replay (29 October 2026)

**Stage:** First-party synthetic reference evaluation; not a qualified
software-repair experiment, eight faithful baselines, trained uncertainty
controller, independent oracle, or verified hardware metering.

## Why this sprint matters

Previously, `action_id_replay_bridge.py` checked whether a **preselected**
list of candidate-bound tool actions was consistent with a frozen book of
public observations. That established replay integrity, but did not show
whether any policy could make **adaptive** choices based on those observations.
`adaptive_reference_replay.py` now performs policy selection inside an
immutable, task-specific public action/target menu after every observed
synthetic diagnostic.

## Two scoped reference controls

- **Fixed testing reference:** select the first available `generate`
  action, test the resulting candidate once, release on a positive visible
  test and otherwise abstain. If generation produces no candidate, it
  abstains. Its one-test rule is a fully specified **local reference
  schedule**, not an asserted faithful recreation of a published method.
- **Uncertainty-free search reference:** invoke the existing
  `choose_matched_baseline` bounded beam heuristic from
  `matched_opportunities.py` at every step. Selection uses immutable
  `SearchPolicy` scores, public test signs, fixed resource prices and
  the live candidate archive. It uses no calibrated uncertainty scores,
  held-out correctness, model generation or independent evaluator. Search
  rewards are an **opportunity proxy**, not expected task success.

Both operate against the *same* `ActionBoundBook` with candidate-bound
action IDs, reserved and reported five-vector resource costs and immutable
public outcomes. The candidate and its original source action remain in
`SharedSession`. Missing responses, incorrect targets and resource
overruns fail closed. All real/unqualified task identities are rejected
by the explicit `SYNTHETIC_` gate.

## Reproducible, falsifiable synthetic difference

Run:

```bash
python -m scripts.smoke_adaptive_reference_replay
python -m unittest discover -s tests -v
```

The smoke's public `test` sign is synthetically **negative**. The fixed
reference therefore takes `generate -> test -> abstain`, while the
uncertainty-free search heuristic may take `generate -> test -> repair ->
abstain` under the same prepared book and hard resource caps.

That is an **action-policy implementation difference**, **not** a measured
correctness or reliability improvement. Neither run has a sealed oracle
verdict, and no LLM has generated a patch. The scripts reject attempts to
insert gold labels or connect this workflow to real PHP/Go repository
identities.

## Remaining before claiming RQ3 scientific evidence

1. Independently admit genuinely task-era specifications, rights,
   independent hidden functional oracles and source-level attribution.
2. Create externally isolated, metered real repository tooling with
   authenticated token/test/GPU/CPU/wall accounting.
3. Pin the six selected model checkpoints/tokenizers and security/terms
   permissions, then obtain actual generated patches and real diagnostics.
4. Verify faithful eight-policy algorithms, shared candidate/opportunity
   draws and pre-registered search hyperparameters. This sprint only adds
   **two scoped reference controls**.
5. Use real paired, blinded evaluator-only verdicts and report all
   assigned-task denominators, attrition, coverage, risk and failure cases.

Both branches of historical vs independently designed prospective tasks
remain distinct. Do not populate Springer Results with this smoke study.
