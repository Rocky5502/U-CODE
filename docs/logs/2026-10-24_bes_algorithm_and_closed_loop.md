# U-CODE work-block ledger — BES algorithm and closed-loop evidence

**Date:** 2026-10-24. **Starting HEAD:** fe2df288e5d78c620a04b5ded08b5ffe7d6f9000. **Target journal:** Springer *Automated Software Engineering*, SBSE/LLM agents special issue (2027-01-30).

## Scientific gap and decision

A standalone one-step expected evidence-value controller can abstain even when a *sequence* of individually insufficient diagnostics could justify a useful release. We implemented **Bounded Evidence Search (BES)**, a finite-depth stochastic Bellman look-ahead over an active candidate and fixed five-dimensional budget. The method is exact **only within a supplied, finite, single-candidate forecast model with correctly specified transition probabilities and one-use action restrictions**. This is not a novel general POMDP solution or an empirically validated result.

## Code committed to GitHub main

1. [BES planner](../../src/ucode/budgeted_belief_search.py): branch enumeration of diagnostic positives/negatives and multi-scenario patch-producing actions; memoization and strict caps (10 actions, depth 4, 30,000 memoized states); componentwise resource feasibility; terminal risk-gated release/abstain; explicit refusal of multiple unverified conditionally dependent probe channels.
2. [Closed-loop adaptor](../../src/ucode/belief_session.py): record a visible diagnostic result, perform Bayes posterior update with frozen likelihood, account resource costs, disallow reuse of spent action ID, accept a new candidate score only if consistent with precommitted scenario support, and replan. Terminal locking does not expose the hidden functional gold oracle.
3. [Algorithmic tests](../../tests/test_budgeted_belief_search.py): 19 synthetic unit cases for look-ahead synergy, generation-then-test, impossible branches, hard budget feasibility, risk gate, cost charging, model assumption declarations and state caps.
4. [Session tests](../../tests/test_belief_session.py): 14 synthetic cases including an invented two-positive branch with posterior 16/17, outcome impossibility, hidden-oracle-free state update, generation plus verification and terminal locks.
5. [Synthetic demonstration](../../examples/bes_lookahead_smoke.py) and [two demonstration tests](../../tests/test_bes_demo.py): outputs contain explicit synthetic/no-repository-executed warnings. GitHub CI now runs the smoke demo in addition to offline tests.
6. [Formal BES method/falsification memo](../BES_ALGORITHM_METHOD_AND_FALSIFIERS_2026-10-24.md) with exact restricted Bellman equation, backward-induction proof, vector feasibility invariant and a mathematical two-probe counterexample.
7. [Springer manuscript main.tex](../../paper/overleaf/main.tex) now includes BES equations, restricted proof argument, synthetic option-value counterexample, computational caps, group-dependent test limitations and comparison contracts. An added first-party manuscript test checks BES equation labels and honest qualifiers.
8. [README](../../README.md) explains reproducible execution, method scope and lack of trained/evaluated model results.

## Actual offline validation and issue encountered

Initial first-party CI suite: **145/145** on Python 3.10/3.12.

BES tests extended the suite to **164**, and the closed-loop and synthetic smoke tests added another **16**. Manuscript integrity assertions added one: **181 Python tests**.
- First session fixture incorrectly expected an 80%-accurate single diagnostic to push a 50%-confidence patch beyond a 90% acceptance gate; CI correctly showed abstention. The fixture was corrected to a sufficiently informative diagnostic rather than distorting the algorithm.
- A manuscript integrity test originally corrupted existing LaTeX regex escapes through an overbroad replacement; CI caught it and the regex was restored.
- [Run 40084542752](https://github.com/Rocky5502/U-CODE/actions/runs/40084542752) verified **181 offline tests passing for both Python 3.10 and 3.12** after these fixes. The later workflow smoke-demo addition requires a fresh final CI verification and artifact check.

The counterexample is deliberately **hypothetical**: prior .5, two independent .8-sensitivity/.8-specificity probes, .9 release threshold, each 0.01 cost; one-step abstains and two-step expected net terminal utility is .285. No real software correctness outcomes, token counts, independent tests or costs were measured.

## Hard unresolved scientific gates

- Strong closest-method comparisons: SWE-Search/MCTS, SWE-Verifier/selective verification, SWE-Replay/reuse, same-search-no-calibration and fixed test. A standard Bellman recursion does not establish publication-level algorithmic originality.
- Independence of evidence channels must be validated, not assumed; current test-reuse, retrieval and single-candidate limitations must be addressed before claiming a fully integrated coding agent. Expected terminal utilities/scenario kernels still lack independently calibrated real-task estimates.
- Issue #1 discovery screening (historical checkpoint 84 attempts/120, 83 successful metadata reads, 0 eligible tasks) and G4 safe independent oracle environment remain scientific blockers. No third-party code executed in ordinary CI.
- No model weights, gated benchmark data, hidden evaluator labels, paid APIs, GPUs or real RQ effects were introduced.
- GitHub paper/overleaf is updated; **no authenticated live Overleaf project was edited**. The existing Actions export publishes a source-only ZIP, not a Springer compile.
- No fabricated safety/risk certificate or figure/result table.

**Next unblocked code/research milestone:** design history-conditional diagnostic transition kernels or a justified conditional-dependence stress test using real training groups; build a source/rights-qualified isolated executable task before measuring any policy advantage. If BES cannot exceed equal-budget uncertainty-free search on held-out tasks, report the negative finding.
