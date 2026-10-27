# U-CODE novelty and falsification ledger
Date: 2026-10-27. Status: prospective research hypothesis, not observed repository-agent success.

## What is NOT new

- SWE-Search (ICLR 2025) uses Monte Carlo tree search and iterative candidate repair: https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html
- SWE-Verifier (2026) selectively checks coding-agent actions: https://arxiv.org/abs/2610.30284
- PATSSEL (EMNLP Findings 2026) routes debug versus regenerate with test-guided selection: https://aclanthology.org/2026.findings-emnlp.2173/
- RETRACE (2026) independently checks patches by forward/backward reconstruction: https://arxiv.org/abs/2608.08950
- Bayesian experimental design, dynamic programming, VOI, selective prediction and finite-scenario maximin are general established mathematical tools.

Therefore we cannot claim inventing uncertainty, search, verification, debugging-vs-regeneration routing, abstention, or robust decision-making.

## Precise proposed U-CODE contribution

An adaptive repository coding agent allocates a shared, independently metered, hard FIVE-resource budget among (1) patch candidate generation/repair, (2) diagnostic evidence acquisition, and (3) release/abstention, where tests can be correlated and uncertain diagnostic likelihood estimates can change the action ranking. The incremental scientific claim is whether this evidence-aware action policy improves held-out full-task correctness over cost-matched uncertainty-removed search and recent verification policies.

Distinct modules exist for one-step vector policy, bounded single-candidate lookahead, history-conditional correlated evidence, joint candidate archive, and one-step frozen-scenario model sensitivity. THEY ARE NOT YET VALIDATED AS AN INTEGRATED END-TO-END SIX-MODEL REPOSITORY AGENT.

## Mathematical one-step diagnostic sensitivity

For the same current belief p, visible diagnostic history h, action a, and frozen possible diagnostic kernel K(k):

\[
g(a,K^{(k)}\mid h) =
\sum_{o\in\{+,-\}}P_k(o\mid h,a)\,
U_0(P_k(Z=1\mid h,o,a))
- U_0(p) - \lambda^\top c(a).
\]

For a FINITE preselected family of hypotheses K, define lower and upper gain as the minimum and maximum of g(a,K(k)) across k. The one-step maximin policy selects a resource-feasible action having STRICTLY POSITIVE minimum gain with the greatest lower gain, else releases or abstains. Finite-scenario lower gain > 0 does not statistically guarantee the true kernel is in K or certify a population risk bound.

With p=.5, predicted release threshold p>=.9, reward/penalty (+1,-1), and test cost .01, a perfectly informative diagnostic has predicted net gain .49; a (.8 sensitivity, .8 specificity) diagnostic has gain -.01. If both are plausible for the same action, its finite-scenario gain interval is [-.01,.49], and the one-step maximin policy stops. This is synthetic illustration, not improved actual code correctness. A zero/negative upper gain permits stopping ONLY in the one-step problem; multi-step option value may still justify the first test.

Implementation: src/ucode/scenario_robust_evidence.py
Synthetic checks: tests/test_scenario_robust_evidence.py
Related math: src/ucode/conditional_bes.py, src/ucode/voi.py, src/ucode/vector_policy.py

## Falsifiable research questions

RQ1 PRIMARY: At identical five hard budget caps and matched proposal opportunities, does U-CODE improve independently held-out full-task success relative to the preregistered no-uncertainty search policy? NO advantage or a disadvantage falsifies the performance claim.

RQ2 MECHANISTIC: Does using true visible-history conditioning rather than false diagnostic independence change actions and improve correctness versus cost? Equivalent outcomes or reduced success falsify incremental usefulness.

RQ3 EXPLORATORY (not silently added to existing eight-policy confirmatory design): Do frozen train-only diagnostic model alternatives improve robustness to estimation instability, or simply increase abstention and harm coverage/success? A stable, well-performing nominal policy would falsify claimed extra utility.

RQ4 SECONDARY: What are verified success, wrong-release risk, coverage, and actual token/test/GPU/CPU/wall spend by independently qualified task family and true changed-source language? Abstentions, failures, malformed and rejected tasks stay in denominators.

## Controls needed before any claim

- Split by independently adjudicated repository/issue/task families, not PR rows; seal independent oracles.
- Equal immutable pre-fix snapshot, task intention, model identity, seed, candidate opportunities, action menus and hard budgets within randomized paired arms.
- Fit diagnostic kernels and scenario variations only from training families and freeze before independent test.
- Cost-only, no-uncertainty search, unconditional conditional-dependence ablation, robust-vs-nominal, and faithful established verification controls.
- Cluster paired uncertainty estimates by task family; preregister primary endpoint, alpha treatment and omission handling. The release threshold is not a statistical risk certificate.
- Keep unknown rights, build failures and missing tests separate from true model failures.

## Dataset factual progress, not measured method performance

120 discovery PR links/unique repository-name strings across 12 query-language strata; 119 PR metadata retrievals; 62 source-path leads; 12 reviewer forms; ZERO independently approved executable tasks or real six-model results. PHP candidate #104 and Go candidate #43 now have official read-only GitHub original-issue timing and pre-fix Git tree metadata. PHP issue created 152 seconds before PR, Go issue created 8 seconds before PR. Issue-body versions at PR creation have not been archived, so current issue text is not a guaranteed pre-PR task specification. Baseline files and toolchain metadata were observed at immutable Git tree SHA. No source clones, builds or independent oracles were executed.

Evidence:
- data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json
- data/admission/2026-10-27/two_candidate_pre_fix_tree_inventory.json

## Publication boundaries

The defensible ASE contribution, if confirmed by real experiments, is conditional and misspecification-aware evidence acquisition versus candidate generation under shared five-resource constraints, not generic "uncertainty improves code". Scientific Data requires independently technically validated, reusable, rights-cleared research data with deposited, reviewable files and a citable version; the current PR discovery metadata alone does not meet the intended executable-task benchmark claim.
