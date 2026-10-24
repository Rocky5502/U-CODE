# BES — bounded evidence search: method, proof and falsifiers

**Date:** 2026-10-24. **Status:** U-CODE first-party algorithm implemented and offline tested; NOT an empirically demonstrated novel research contribution or a calibrated policy.

**Code:** [bounded look-ahead planner](../src/ucode/budgeted_belief_search.py); [visible-outcome replan/replay](../src/ucode/belief_session.py). **Tests:** [19 planner invariants](../tests/test_budgeted_belief_search.py) and [14 visible-session invariants](../tests/test_belief_session.py), using invented mathematical probabilities. No model inference, hidden-test outcome or third-party repository code was run.

## Scientific motivation

The existing one-step U-CODE controller misses tests which have **zero immediate** terminal benefit but create a worthwhile option for a second diagnostic. BES introduces explicit stochastic observation branches and finite-horizon look-ahead, distinguishing information acquisition about an existing candidate from candidate-changing generate/repair actions. Hard resource budgets apply independently to input/output tokens, test calls, GPU seconds, CPU seconds, and wall seconds.

BES currently tracks **one active patch candidate**, not a full Pareto archive. Generate/repair *replace* the active candidate; a forecast scenario with no usable new candidate keeps the previous candidate. Tests/static-analysis/retrieval affect **belief about the active patch**; context retrieval that improves a future patch generator is not modeled yet. Nonterminal actions are available at most once per planner call (and once per closed-loop session). This is deliberately bounded, not a full repository-level agent.

## Observable state and pre-outcome action models

The state is \((p,\mathbf b,A,d)\) where \(p\in[0,1]\) is the frozen estimated probability that the current patch is jointly acceptable (or the absent-candidate symbol), \(\mathbf b\) the remaining vector budget, \(A\) unused identified actions, and \(d\) remaining look-ahead depth.

A diagnostic has pre-outcome class-conditional sensitivity \(\mathrm{Se}_a\) and specificity \(\mathrm{Sp}_a\). Bayes predicts the visible positive/negative branches and associated posteriors. A generator or repair action has an externally supplied, finite probability distribution over **post-action predicted patch risks**; these are **not** gold correctness outcomes. Every action has nonzero vector resource costs, and only actions satisfying \(c(a)\preceq\mathbf b\) are feasible.

A terminal release is permitted by the frozen predicted risk gate only if \(1-p\le\alpha\) and its expected positive-minus-negative release reward exceeds zero. Abstention has zero terminal utility. Neither a threshold nor code execution in this repository creates a statistical risk guarantee.

## Finite-horizon Bellman recurrence

Define \(U_0(p)\) as the terminal release-or-abstain utility, \(U_0(\bot)=0\). For supplied transition scenarios \(K_a(o,p'\mid p)\),

\[
V_0(p,\mathbf b,A)=U_0(p)
\]
\[
V_d(p,\mathbf b,A)=\max \left\{ U_0(p),\
\max_{a\in A:c(a)\preceq\mathbf b}
\left[-\lambda^\top c(a)+
\sum_{o,p'} K_a(o,p'\mid p)
V_{d-1}(p',\mathbf b-c(a),A\setminus\{a\})\right]
\right\}.
\]

The planner returns its first action and expected net terminal utility; actual **visible** evidence is recorded by the closed-loop session, which updates the posterior and replans without any evaluator-only test label.

**Proposition A (resource safety).** Every executed search branch satisfies \(\mathbf b_t\succeq0\) componentwise. **Proof:** all initial resource fields are nonnegative by validation; an action is expanded only if \(c(a)\preceq\mathbf b_t\), and recursion subtracts only that feasible cost. Induction on step count maintains the invariant. A zero or small scalar price cannot bypass a hard budget. QED.

**Proposition B (finite-tree value optimality).** Given fixed and correctly specified discrete pre-outcome transition probabilities, additive scalar planning costs, the one-candidate representation, at-most-once actions and no more than depth \(d\), the recurrence maximizes expected terminal utility within this restricted decision tree. **Proof:** with \(d=0\) only the stop utility is feasible. If continuation values of depth \(d-1\) are optimal, each feasible root action's expectation of those continuations minus action cost is its best attainable conditional value. Maximizing these values versus stopping establishes optimality at depth \(d\). Induction completes the argument. QED. This is **standard finite-horizon dynamic programming**; we make no new general optimality theorem claim.

With \(m\) possible actions, \(B\) maximum branches per action and depth \(d\), worst-case unmerged tree paths can grow as \(O((mB)^d)\). Code bounds \(m\le10\), \(d\le4\), and at most 30,000 unique expanded memoized states by default, failing closed beyond the limit. It is not a scalable full POMDP solver.

## Counterexample to one-step action myopia — *analytical only*

Start with one hypothetical patch \(p=.5\). Permit release only for \(p\ge .9\); correct release reward \(+1\), wrong release penalty \(-1\). Two hypothetical tests \(a,b\) are conditionally independent given true patch correctness, each with sensitivity and specificity \(0.8\) and scalar price \(0.01\).

After **one** positive test, posterior becomes \(0.8\): still no permitted release. A myopic one-step policy therefore abstains. After **two** positive tests, posterior becomes \(16/17\approx 0.9412\) and release value is \(15/17\). The joint probability of those positives is \(0.34\), giving expected release value \(0.34(15/17)=0.30\). Buy the first test always, then the second only after the first positive (probability \(0.5\)); expected cost is \(0.01+0.5(0.01)=0.015\). The **hypothetical two-step optimal value is \(0.285\)**. The regression tests verify one-step abstention and two-step testing, and separate generate-then-verify synergy. This is not an empirical effect on software.

## Explicit uncertainty assumptions and leakage gate

Sequential probes are modeled as conditionally independent given true acceptability **only when the caller affirmatively declares that assumption**. BES rejects multiple distinct probes at horizon greater than one by default. The flag does not validate independence; shared faults in generated tests or repository-specific tools can make sequential Bayes updates wrong. A fitted history-conditioned observation kernel is a prerequisite for reliable deployment.

The agent and session receive only model-derived **pre-oracle** priors, allowed candidate-scenario forecasts, and visible tool outcomes. Neither software can cryptographically prove the upstream predictor was not exposed to hidden tests; a separately reviewed evaluator and immutable logs are mandatory. The current training-only diagnostic estimator and independent evaluation module remain separated on purpose.

## Novelty and experimental falsification

SWE-Search (MCTS), SWE-Replay, SWE-Verifier and other related work already establish search and selective verification. Implementing a standard finite-horizon Bellman recursion or revealing hypothetical action complementarity is **not by itself journal-level novelty**. The potential contribution is an **empirically reliable, calibrated heterogeneous resource-allocation policy** for repository code agents; it must beat strong equal-budget controls and expose limitations.

Compare BES with original one-step vector policy, no-uncertainty lookahead using the *same* action forecasts and budgets, fixed/always-test, random/cost-first, selective verifier, and faithful MCTS/replay-style baselines. Report held-out independent full-task success, coverage, conditional wrong-release risk, search time and all resource consumption. Never count repeated seeds as independent repository tasks.

**GO:** new bounded search implementation, exact restricted-model recurrence, CI unit tests, safe visible-observation replanning. **HOLD:** real-world effectiveness, formal selective risk certification, calibrated dependence, full Pareto archive, safe executable third-party benchmark, compiled/live-synced Overleaf manuscript.
