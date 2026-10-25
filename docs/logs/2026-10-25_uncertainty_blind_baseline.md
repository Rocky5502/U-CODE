# U-CODE research execution block — uncertainty-blind negative control

**Date:** 2026-10-25. **Starting commit:** ef25cd84de3571c050df2611b455510c1d2d1233, 379 offline tests passing. **Research deliverable:** implement a genuine, reproducible fixed-schedule negative control for the planned BES versus uncertainty-free software-agent decision study.

## Committed and CI-audited

- [blind_search.py](../../src/ucode/blind_search.py): typed uncertainty-blind action selector, hard vector budget, ex ante priority schedule, candidate SHA256, visible boolean diagnostic observations, single-use tool action IDs, release gate based on positive visible tests, repair path that invalidates old candidate observations. **No posterior/prior, sensitivity, predicted correctness or evaluator verdict fields** in the public interface.
- [tests/test_blind_search.py](../../tests/test_blind_search.py): 27 adversarial and behavioral tests covering generation, retrieval, testing, repair, release/abstain, five-component budget feasibility, negated/no-result traces, invented gold-label injection, stale candidate observation rejection and fixed predeclared action ordering.
- [Synthetic action config](../../configs/blind_search_synthetic_schedule_2026-10-25.json), [offline trajectory](../../examples/blind_search_smoke.py), and [four smoke tests](../../tests/test_blind_search_smoke.py). Hand-authored toy sequence: generate fake candidate -> retrieve positive -> visible test negative -> repair -> visible test positive -> release; fake cost accounting uses 37 tokens and two calls, **neither real inference nor measured task success**.
- [matched_action_inventory.py](../../src/ucode/matched_action_inventory.py): exact common static manifest of action IDs/kinds/five-vector costs and initial caps, canonical digest sorted to remove order dependence. BES-only model predictions and blind-only scheduler priorities intentionally omitted. A changed tool/category/cost/cap fails the checker.
- [13 action-parity tests](../../tests/test_matched_action_inventory.py), [reproduction](../../examples/action_parity_smoke.py) and [three reproducibility checks](../../tests/test_action_parity_smoke.py).
- [Springer LaTeX](../../paper/overleaf/main.tex): new section on blind fixed schedule and Eq. `eq:action-parity`, explicitly separating a weak negative control from the **as-yet-unimplemented strong optimized uncertainty-free primary comparison**. [Scientific limits memo](../BLIND_SEARCH_AND_PARITY_2026-10-25.md), [README](../../README.md) and [GitHub Actions](../../.github/workflows/ci.yml) updated.

## Findings and true limits

**Engineering observation:** the blind controller can exercise the same *kinds* of intervention as the one-candidate BES reference while lacking any access to predictive confidence or hidden oracle labels. A common digest can detect basic static mismatches in tools, costs and caps; simulated tests enforce this across unit fixtures. It is not proof that actions have equivalent implementations, model contexts, prompts, retrieval results or real runtime costs in an externally executed benchmark.

**Negative controls do not settle strong efficacy claims.** A fixed-schedule action policy is too simple to support the journal's primary hypothesis alone: a well-tuned uncertainty-free search, selective verifier and credible MCTS/replay comparators remain necessary. Related work has already implemented sophisticated patch verification and coding-agent search. The negative-control implementation is a material engineering step, not a novel theorem or empirical evidence of improved coding-agent reliability.

**Evidence:** frozen 120 discovery links, 119 metadata retrieved, 62 source-path hints, 14 first-pass human-review leads, two real pinned admission dossiers, **0 fully admitted executable tasks, 0 independent functional gold evaluations, 0 six-model inference**. No third-party repository source was executed and no paid resources were used.

## Next scientific gate

Implement a stronger uncertainty-free search-optimized baseline with candidate branching/archives and equal tuning/search opportunities; independently clear at least one real task's source/file rights, task specification, sealed oracle and hardened execution runner; pin model and tool revisions, then collect paired real run receipts and only then populate Results. Current CI is first-party offline unit tests and synthetic examples.

**Verification:** final GitHub CI run must be checked on both Python 3.10 and 3.12 and source-only Overleaf artifact confirmed; no authenticated live Overleaf sync is claimed.
