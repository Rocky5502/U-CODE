# U-CODE v2 — problem definition, novelty falsifiers and experiment contract

**Date:** 2026-10-24 · **Status:** pre-experimental proposal, **not** an observed new algorithmic or empirical finding.  
**Audience:** PI / SBSE methods / software verification / uncertainty / reproducibility / three skeptical reviewers.  
**Target:** Springer *Automated Software Engineering*, [SBSE + LLM agents special issue](https://link.springer.com/collections/jjcfecffai), 2027-01-30.

## Decision from primary-source novelty audit

A claim such as "the first uncertainty-aware multi-objective search for coding agents" is **not defensible**. Prior work already includes (i) SWE-Search MCTS (ICLR 2025), (ii) GA4GC multiobjective agent configuration optimization (SSBSE 2025), (iii) SWE-Replay test-time trajectory reuse, (iv) October 2026 SWE-Verifier selectively spending computation on agent-action verification, and (v) uncertainty-guided token/code revision. A recent controlled code-generation study reports that uncertainty-triggered regeneration can *harm* Pass@1 while execution-based correction helps. See the [23-source, primary-link verified matrix](../literature/novelty_matrix_2026-10-24.csv).

The proposed narrow research gap is **not "more search" or "more tests."** It is:

> Under a **vector-valued inference, verification and latency budget**, can a coding agent use independently calibrated evidence-transition predictions to choose **which kind of evidence** to acquire next, rather than simply generating more code or verifying every step, while reducing independently measured erroneous *released* patches at a prespecified acceptance coverage?

This is a **candidate distinction**, not proof of novelty. Any real novelty depends on a demonstrable new decision rule or scientifically important, independently replicated discovery beyond the nearest methods, especially SWE-Verifier, SWE-Replay, GA4GC and uncertainty-only correction. The other active projects OpenCoderX-E and CALM-SE must be audited for overlapping code, tasks, and claims (see [boundaries](PROJECT_BOUNDARIES.md)).

## 1. Units, sources and outcomes

- Primary controlled evaluation unit: task-instance \(i\) from a fixed pre-fix repository snapshot, independent issue description and sealed oracle. Pair the same task/model/seed/budget across competing policies.
- Naturalistic descriptive cohort: authenticated merged coding-agent PRs screened for *actual changed source*, line/commit ownership, rights and independently verified tests. A bot PR does not imply every line or file in the repository was AI-authored.
- \(g(i)\): immutable repository/fork lineage cluster; language is inferred from actual changed production files, potentially multilabel. Split by **cluster and time**, not PR row.
- \(Y_i(x)\in\{0,1\}\): result of a *held-out*, post-policy independently administered correctness oracle applied to candidate patch \(x\). Results inaccessible to generation, retrieval, test selection, model selection or policy action selection.
- \(S_i(x)\in\{0,1\}\): separately defined safety/security acceptability by preregistered independent checks. Security scanner flags are not synonymous with exploitable vulnerabilities.
- Joint release-acceptable latent outcome \(Z_i(x)=Y_i(x)S_i(x)\). Do not assume independence of \(Y\) and \(S\). If an adequate safety oracle is unavailable, report correctness and observed analyzer alerts separately and do not call them a single validated event.
- Runtime/maintainability measurements are secondary objective vectors with declared valid domains and workload protocols.

## 2. Sequential decision process — what policy sees and what it must not see

At step \(t\), the observable information is
\[
h_t=(d_i,\mathrm{snapshot}_i,\mathcal C_t,e_t,m_t,\mathcal F_t,b_t,\mathcal H_{<t}),
\]
where \(d_i\) is the issue description, \(\mathcal C_t\) a set of candidate patch IDs,
\(e_t\) contains **only visible qualified verifier** observations,
\(m_t\) is the frozen model/calibrator metadata, \(\mathcal F_t\) the current
estimated nondominated candidate frontier, \(b_t\) the resource balance, and
\(\mathcal H_{<t}\) the admissible action history.

Neither \(Y_i(x)\) nor hidden test names/expected outputs, gold patches, independent safety labels, other policies' hold-out results or test-derived calibration labels may appear in \(h_t\). Use a tamper-evident separation between *policy-visible* diagnostic tests and *evaluator-only* held-out tests.

Action set:
\[
\mathcal A_t=\{\mathrm{generate},\mathrm{retrieve},\mathrm{test},
\mathrm{static\_analysis},\mathrm{repair}\}.
\]
An optional supported 'ask human' arm must include user-time costs and be excluded from zero-human baselines. \(\mathrm{release}(x)\) and \(\mathrm{abstain}\) are **terminal decisions**, not ordinary verification tools. In particular, abstention cannot falsely gain hypervolume by manufacturing a new candidate.

Resource vector for action \(a\):
\[
c(a)=(\text{output+input tokens},\text{test calls},\text{GPU seconds},
\text{CPU seconds},\text{wall seconds})\in\mathbb R_{\ge0}^{5}.
\]
The policy is feasible only if cumulative measured cost satisfies
\(\sum_{t<T}c_j(a_t)\le B_j\) for **every** resource \(j\).
For policy comparison, register the same bounds \(\mathbf B\) (not an arbitrary trade of 1 token for 1 test). If pricing is needed for a scalar acquisition, units and conversion rates \(\lambda_j\) must be specified **ex ante**; also report raw units.

The state is partially observed: generated code can be wrong despite a green visible test. A frozen, held-out calibrated estimator predicts
\[
p_t(x)=\Pr(Z_i(x)=1\mid h_t)
\]
and action-conditional observable evidence kernels
\[
K_a(o,h'\mid h_t)
=\Pr(O_{t+1}=o,H_{t+1}=h'\mid h_t,a).
\]
A kernel is a learned/tested probabilistic hypothesis, not a guarantee. Diagnostic tests can modify the posterior and *do not necessarily produce any new patch*. A generate/repair action can add candidates. A retrieval action can change model context and evidence; static analysis yields a potentially correlated imperfect diagnostic. Do **not** treat a passing visible test as a perfect oracle or add a fictitious Pareto point for a test action.

## 3. Objective: release, coverage, risk and search

Final output \(D_i^\pi \in \mathcal C_T\cup\{\bot\}\), with \(\bot\) = abstention.
Define full-task verified success (abstention is not success):
\[
S(\pi)=\mathbb E[\mathbf1\{D_i^\pi\ne\bot\}\,Y_i(D_i^\pi)].
\]
Coverage \(C(\pi)=\Pr(D_i^\pi\ne\bot)\).
The population *selective wrong-release risk* is
\[
R(\pi)=\frac{\mathbb E[\mathbf1\{D_i^\pi\ne\bot\}\,
              (1-Y_i(D_i^\pi))]}
             {\Pr(D_i^\pi\ne\bot)}
\quad\text{for }C(\pi)>0.
\]
Report safety failures separately. Abstaining always is a **degenerate policy**, not a valid reliability victory. Pre-register a minimum acceptable coverage \(C_{\min}>0\) for risk-controlled policy comparison; compare both **full-task success** and risk–coverage.

Prospective constrained objective:
\[
\max_{\pi}\ S(\pi)
\quad \mathrm{s.t.}\quad
\forall j:\sum_tc_j(a_t)\le B_j,\quad
R(\pi)\le\alpha,\quad C(\pi)\ge C_{\min}.
\]
Optionally maximize the Pareto frontier across \(S\), coverage, measured security and normalized energy/latency rather than scalarizing all outcomes. The main RQ3 endpoint remains **task-paired independent verified success** at a registered budget, including abstentions in its denominator.

### Risk acceptance caveat

A threshold \(1-p_t(x)\le\alpha\) is a **predictor-based policy rule**, **not** a formal selective-risk guarantee. Model selection, adaptive verification and optional stopping can invalidate naive confidence bounds. Any finite-sample claim must calibrate/validate the **complete frozen policy** on exchangeable held-out task clusters (or justify another inference method), inspect conditional release coverage, and test shift. A conformal wrapper cannot be attached to any arbitrary adaptive policy and described as certified without proving the relevant loss monotonicity and exchangeability conditions. If these fail, report empirical risk intervals only.

## 4. Reference Bellman formulation and acquisition

Let \(V_0(h)\) be the best admissible terminal value: a preregistered, correctly dimensioned utility of releasing an eligible patch, or zero for abstaining. Introduce a bounded scalar utility for *planning only*; preserve raw multiobjective outcomes in scientific evaluation. At remaining budget \(\mathbf b\):
\[
V(h,\mathbf b)=\max\left\{
 V_0(h),
 \max_{a:\,c(a)\preceq\mathbf b}
 \left[
   -\lambda^\top c(a)
   +\mathbb E_{(o,h')\sim K_a(\cdot\mid h)}
       V(h',\mathbf b-c(a))
 \right]
 \right\}.
\]
This is the **formal optimal-control benchmark**, not a claim that the current software solves a general POMDP. The practical solver will be a finite-depth, calibration-driven approximation with explicit time/memory limits. Irreducible noise in \(\widehat K\) motivates model-uncertainty sensitivity and a refusal to use 'risk certified' language until earned.

One-step myopic evidence value for a **verification-only action**:
\[
\mathrm{EVSI}(a\mid h)
=\sum_o P(o\mid h,a)V_0(T(h,a,o))-V_0(h).
\]
Purchase \(a\) only when its expected benefit exceeds fixed measured, preregistered cost penalty and it fits all hard resource budgets. EVSI is generally **not** equal to hypervolume improvement: a test reveals information about existing candidates, whereas a new generated patch can enlarge the candidate set. For generation/repair, model the outcome-conditioned candidate additions, allowing future testing, before computing total expected terminal utility. Code that computes *one invented EHVI for every test/retrieval action* is conceptually wrong.

For multiobjective candidate generation (not evidence-only diagnostics), an optional auxiliary acquisition is
\[
\frac{\mathbb E[\Delta HV(\widehat{\mathcal F}_{t+1})\mid h_t,a]}
     {\lambda^\top c(a)}
\]
with precommitted reference point, consistent objective scales and an explicitly modeled joint distribution for correlated objectives; do not claim exact EHVI or calibrated outcomes when independent Gaussian marginals are arbitrarily assumed.

### Diagnostic example (pure mathematics, NOT measured data)

Current joint-acceptability belief \(p=0.5\). Set admissible max predicted release-failure threshold \(\alpha=0.1\), correct release utility +1, incorrect release utility -1 and abstention 0. The current policy abstains. A hypothetical *perfect* independent test reveals the true event: with probability 0.5, the posterior becomes 1 and a correct candidate can be released; with probability 0.5, posterior becomes 0 and the system abstains. Thus expected post-test terminal utility is 0.5, EVSI=0.5; if fixed test-cost penalty is 0.1, net gain=0.4. This is **a sanity-check example**, not evidence that such tests exist in any observed repository. An uninformative test with identical pass likelihood for correct and incorrect code has EVSI=0.

## 5. Closest-baseline contract (stop/go critical)

All policies must start with identical candidate/issue snapshots, seeds/model configurations, hidden oracle isolation and the **same vector budget**. Strong comparisons require:
1. **No-search**: single generated patch, fixed valid cost.
2. **Fixed verifier**: test every candidate or predetermined schedule.
3. **Random/cost-first**: choose feasible tool randomly or by minimal measured cost.
4. **Uncertainty-only**: thresholded generate/repair without any extra verification (negative control).
5. **Search, no uncertainty**: same controller and budget, with calibrated uncertainty replaced by non-informative or shuffled estimates.
6. **Search plus raw risk, no calibration**.
7. **Search plus calibrated risk, no online evidence-choice**.
8. **U-CODE full** (future only after implementation).
9. **MCTS/SWE-Search-style trajectory search**, resource permitting, with matched tool permissions.
10. **Selective verification/SWE-Verifier-style gate** with policy-construction/reproduction limitations honestly reported.
11. **Replay/reuse/SWE-Replay-style** baseline and **GA4GC-style offline configuration tuner** where feasible; if not feasible, expressly narrow the comparative claim.

Unit tests of an offline stochastic simulator, per-action classifier, or synthetic EHVI are **necessary engineering checks**, not empirical proof.

## 6. Falsifiable RQs and the required answers

| Research question | Null hypothesis / falsifier | Evidence |
|---|---|---|
| RQ1: what failures actually occur? | Most discovered PRs may be unusable or not independently attributable; merged != correct | screened-source denominator and rights/executability attrition, independent diagnostic taxonomy |
| RQ2: does predicted risk transfer? | token entropy and self-confidence may be uncalibrated or useless | Brier/log loss, AUROC, AURC, ECE sensitivity, repo/language/time shift |
| RQ3: does a calibrated acquisition policy improve independent verified success at matched cost? | an equal-budget search with no uncertainty may be just as strong | paired task/seed success difference with clustered CI, prespecified budget |
| RQ4: what evidence is worth buying? | fixed testing or indiscriminate generation may dominate | randomized policy ablations, qualified test VOI vs expected/actual intervention benefit, cost traces |
| RQ5: generalization to held-out projects/languages/models? | a controller can succeed on one family and fail outside it | by-group effects with denominator and failures, no forced 12-language statement |
| RQ6: what mechanism is causal? | any apparent gain may be search-budget growth, oracle contamination, reuse or abstention | shuffled-risk and sham-cost controls; remove calibration, VOI, frontier, testing, retrieval, repair, abstention individually |

**Primary design:** task/repo-lineage cluster random assignment or within-task paired seeds, pre-specified one primary budget and primary policy contrast. Include all attempts and failures/abstentions, with group-level uncertainty intervals. Calculate accepted-set conditional risks **with coverage and denominators**. No leakage from independent gold tests into action selection, early stopping or thresholds. Where impossible to randomize online actions, call it observational/mechanistic association only, not action causality.

## 7. Three senior reviewer attacks and the next decisive experiment

- **Reviewer A, SBSE:** The present \`search.py\` is a weighted heuristic and \`acquisition.py\` assumes each action creates a new point. *Required repair:* formally distinct stochastic transitions for diagnostic vs generative actions, with a no-uncertainty equal-search baseline and consistent cost units.
- **Reviewer B, empirical SE:** The 120 repositories are discovery hits, not trustworthy task units; the live audit checkpoint reports 84 attempts, 83 successful metadata retrievals, but 0 accepted/reproduced tasks. *Required repair:* independently traceable fixed-snapshot tasks, real build/test oracles and rights checks. Do not turn 39 preliminary source-path records into a code benchmark.
- **Reviewer C, stats/security:** High confidence and easy visible tests cannot certify true behavior. Allow abstention only with minimum coverage; cluster by repository/fork, validate risk after whole-policy selection, blind hidden oracles.

**Decisive minimal experiment once a safe executable task slice exists:** freeze 3 models, 40 *actual* tasks where independent oracles pass sandbox checks; compare fixed-test, uncertainty-only, equal-search/no-uncertainty and U-CODE with identical token/test/GPU/wall budgets. Record posterior shifts induced by diagnostic tests, the opportunity cost of those tests and true released-patch correctness. If U-CODE does not outperform no-uncertainty search, report the negative result and do not force a journal-method novelty claim.

## 8. Priority / deliverables

**Now, without GPU:** complete literature audit; implement/tests of exact Bayes evidence value on *hypothetical* binary diagnostics; update Springer LaTeX with equations and accurate citations; freeze regression criteria.  
**Next real-data gate:** 120-PR triage and trustworthy executable independent oracle, possibly seeded by *task cohort D* instead of wrongly treating naturalistic AI-PR metadata as runnable task labels.  
**Only after oracle isolation:** fit actual action-conditioned diagnostic likelihoods, use whole-policy calibration, budget-match search baselines, measure real RQ3 and RQ4 effects.

**Go/no-go:** GO for formal method, verified primary-source novelty documentation and toy regression tests. HOLD for assertions of a new verified algorithm, measured reliability improvement, certification under shift, model experiments or a publication-ready manuscript.