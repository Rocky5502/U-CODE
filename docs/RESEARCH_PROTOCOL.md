# U-CODE pre-experimental protocol (2026-10-24)

**Title:** Uncertainty-Guided Search for Reliable AI-Generated Software

**Target:** Springer Automated Software Engineering, [special issue](https://link.springer.com/collections/jjcfecffai) on SBSE, LLMs and agents; deadline **January 30, 2027**.

## Hypothesis

An agent must spend scarce inference and verification resources on competing
actions: generate, retrieve, test, analyze, repair, or abstain. We hypothesize
that pre-outcome *calibrated* risk estimates integrated with **budget-constrained
multi-objective search** outperform equal-cost controls in independently
verified correctness and selective reliability. Negative results count.

## Research questions and estimands

1. **RQ1, failure landscape:** prevalence/type of correctness, security,
   efficiency, and maintainability failures in attributable agent-authored
   patches across programming languages, domains and repository sizes.
   Compare matched human PRs where feasible, with project/size adjustment.
2. **RQ2, calibration:** how do token entropy (when exposed), model
   disagreement, self-consistency, self-reported confidence, static warnings
   and context features predict *independent* pass/fail? Brier, ECE,
   reliability diagrams, AUROC/AUPRC, risk-coverage, grouped confidence
   intervals. Never peek at test labels during uncertainty estimation.
3. **RQ3, search effectiveness:** at matched inference and test budgets,
   does uncertainty-aware multi-objective search increase independent
   verified success relative to no-search, random, fixed-test, cost-first,
   quality-only, and an optimized search controller without uncertainty?
   Primary estimand: paired difference in independent verified success.
4. **RQ4, intervention:** when should an agent generate, retrieve, test,
   analyze, repair, ask, or abstain? Analyze action traces and randomized
   ablation arms; avoid causal claims from uncontrolled selections.
5. **RQ5, generality:** are gains robust on held-out repositories, projects,
   languages, model families and task complexity strata? Include group-level
   uncertainty and sample-size/attrition tables.
6. **RQ6, mechanism:** what is the effect of calibration, multiobjective
   frontier pruning, uncertainty bonus, execution feedback, retrieval,
   repair and abstention? Run prespecified component ablations and leakage
   sensitivity analysis.

## Distinct cohorts: no unsafe pooling

- Naturalistic **A**: linked agent-authored PR *patches* from the 120 candidate
  GitHub repositories, potentially supplemented by AIDev. Merge status is
  not functional correctness. Base/head SHA and independent verification matter.
- Naturalistic **B**: SWE-chat session/commit traces after gated access approval.
  Session-level data do not equal independent source files.
- Controlled attribution **C**: DroidCollection human/AI/mixed code labels,
  suitable for attribution studies, not repository execution outcomes.
- Evaluation **D**: AI generations run by our pinned models on tasks from
  SWE-rebench V2 and multilingual SWE benchmarks. These *tasks* were not
  necessarily originally AI-generated code.
- Efficiency **E**: EffiBench-X for performance and resource objectives.

Report cohort-specific denominators; don't sum sample counts across sources.

## Formal optimization and search formulation

Observable state at time t: S_t = (task context, generated candidates,
uncertainty estimates, publicly available test evidence, remaining budget,
search frontier, past actions). Available actions A = {generate, retrieve,
test, static_analysis, repair, abstain}. Let c(a) be measured, nonnegative
cost and total sum of c(a) be <= budget B.

Online policy chooses the next action using **only pre-outcome** predicted
gain/information/security-risk reduction. For verified candidate x, report
the multiobjective vector:
    Q(x) = (held-out test correctness ↑, security warnings ↓,
            runtime/memory ↓, inference and test cost ↓).

Target constrained optimum:
    maximize E[correctness(x_final)] - λ_r E[risk(x_final)]
             - λ_c E[compute_cost]
    subject to sum_t c(a_t) <= B, test_calls <= T, latency <= L,
    optionally P(failure | accepted) <= alpha.

The initial code has an explicit cost-constrained Pareto frontier and heuristic
controller. To claim an **algorithmic SBSE advance**, evaluate and refine an
actual exploration/exploitation objective such as risk-constrained expected
hypervolume improvement, with fixed reference point and learned/calibrated
acquisition utilities. No such advancement or empirical gain is yet claimed.

## Candidate audit gates

1. GitHub repository and PR resolve to immutable identifiers.
2. Agent author identity and merge status confirmed (bot name alone is weak).
3. Source-bearing changes confirmed, excluding pure docs/config/lockfiles.
4. Actual code ownership and attribution checked; do not treat entire repository
   as AI-authored. Record source edits by language, not only repo primary label.
5. Repository and file-level licenses, distribution rights, PII, secrets audited.
6. Base revision reconstructed; controlled reproducible build and independent
   tests available; no gold patch in model input.
7. Exclude forks/near-duplicates and keep time and repository groups isolated.
8. Record reason-coded rejection; target 80–120 passing repositories **only if**
   evidence supports them. 2–5 GB is a target, not an observed size.

## Experimental matrix: PROPOSED, not run

| Dimension | Proposed arms |
|---|---|
| Models | Qwen2.5-Coder-7B, Qwen3-8B, Llama-3.1-8B, Granite-3.3-8B, DeepSeek-Coder-6.7B, Gemma-3-4B |
| Programming languages | Python, JS, TS, Java, Go, Rust, C++, C, C#, Kotlin, PHP, Ruby |
| Agent policies | no-search, random, cost-first, fixed-test, quality-only, search without uncertainty, U-CODE |
| Uncertainty ablations | entropy, disagreement, self-consistency, metadata, confidence, calibrated fusion |
| Budgets | fixed token cap, test calls, normalized accelerator time, wall clock |
| Outcome | independent test pass, security warnings, risk-coverage, Brier, ECE, cost Pareto |
| Seeds | 3+ proposed per sample; power and compute plan after pilot |

Use task-paired comparisons and repository/fork-clustered bootstrap or hierarchical
models. Pre-register primary budget and primary endpoint before repeated runs;
avoid pseudo-replication; consider multiple-testing adjustments for secondary RQs.

## Security and inference integrity

Hidden tests and gold solutions are sealed from all model prompts, retrievers,
uncertainty estimators and policy selection. No unsafe code execution by default.
For vetted experiments, run any third-party source only in isolated, nonprivileged,
network-disabled containers with capped CPU/memory/wall time, no host mounts or
secrets, and pinned image digests. Archive prompts/seeds/model hashes/provenance
and annotate impossible-to-check artifacts, never fill blanks with fabricated
metrics.

## Scientific stage gates

- M0: repository bootstrap + 120 **discovery** records + offline agent scaffold.
- M1: perform read-only metadata triage for 12–24 PRs; manually inspect patch
  and licenses; report actual passing/removed counts.
- M2: one independently executable 3-model/40-task pilot including reliability
  diagrams and matched-budget controls; full setup and seeds archived.
- M3: implement/ablate an independently evaluated uncertainty-aware Pareto
  acquisition function (not just heuristic action scoring).
- M4: multilingual replication, security/performance analyses, paired statistics,
  paper and artifacts. Do not draft result numbers before experiments.

## Related research and source pages

- Journal call: https://link.springer.com/collections/jjcfecffai
- AIDev: https://huggingface.co/datasets/hao-li/AIDev
- SWE-chat: https://huggingface.co/datasets/SALT-NLP/SWE-chat
- DroidCollection: https://huggingface.co/datasets/project-droid/DroidCollection
- SWE-rebench V2: https://proceedings.mlr.press/v306/badertdinov26a.html
- EffiBench-X: https://huggingface.co/datasets/EffiBench/effibench-x
- Related 2026 code generation survey: https://link.springer.com/article/10.1007/s10489-026-07230-0
- Active learning / uncertainty governance (2026): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6770198
- Multi-agent Go code generation (2026): https://ieeexplore.ieee.org/document/11646569

Novelty must be reviewed against the actual paper methods, not presumed from titles.
