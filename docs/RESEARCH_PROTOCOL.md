# U-CODE pre-experimental protocol (2026-10-24)

**Title:** Uncertainty-Guided Search for Reliable AI-Generated Software

**Target:** Springer Automated Software Engineering, [special issue](https://link.springer.com/collections/jjcfecffai) on SBSE, LLMs and agents; announced deadline **January 30, 2027**, subject to publisher updates.

**Current registration crosswalk (3 November 2026):** this document began as the 24 October exploratory plan. The [25 October eight-arm confirmatory contract](../configs/confirmatory_sbse_protocol_2026-10-25.json) and [accepted six-checkpoint manifest](../configs/accepted_six_model_study_2026-10-25.json) supersede earlier example model/baseline lists below. The study is still **prospective**, with **zero** independently qualified executable tasks, model runs, or measured treatment effects.

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
   verified success relative to the prospectively registered equal-budget no-uncertainty
   search control, with other frozen arms as secondary comparisons?
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

- Naturalistic **A**: linked agent-authored PR *patches* from the 120 discovery
  PR-link/repository-name leads (not 120 executable repositories), potentially supplemented by AIDev. Merge status is
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

## Experimental matrix: PROPOSED, not run (canonical crosswalk 3 November 2026)

| Dimension | Prospective design (not observed execution) |
|---|---|
| Models | Exactly **6** selected open-weight checkpoint IDs in the accepted manifest; full revision, tokenizer, license, inference-engine and hardware gates still pending |
| Languages | Twelve **discovery-query strata**: Python, JS, TS, Java, Go, Rust, C++, C, C#, Kotlin, PHP, Ruby; independently runnable changed-language coverage **not established** |
| Agent policies | Exactly **8** registered slots listed below; fidelity to original baselines and real-task integration **not yet established** |
| Primary comparison | `ucode_conditional_bes` versus `no_uncertainty_search`; same assigned task/model/seed/public proposal opportunities and five hard budget caps |
| Uncertainty | Calibrated correctness risk on training-only lineage groups is a hypothesis, not a measured score or guarantee |
| Budgets | Five resource axes: tokens, test_calls, gpu_seconds, cpu_seconds, wall_seconds; illustrative caps are **not frozen** |
| Primary outcome | Independent full-task verified success per *assigned* cell, intention-to-treat (abstention/timeouts included) |
| Secondary outcomes | Coverage; wrong-release risk; risk–coverage; calibration (when labelled); paired effect; five-dimensional realized cost |
| Seeds | Three illustrative values in contract; final seeds, budgets and preregistration still **unfrozen** |

**Selected model IDs (exact immutable-for-planning identity; weights not loaded):**

- `Qwen/Qwen2.5-Coder-7B-Instruct`
- `Qwen/Qwen3-Coder-30B-A3B-Instruct`
- `mistralai/Devstral-Small-2-24B-Instruct-2512`
- `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- `google/codegemma-1.1-7b-it`
- `meta-llama/Llama-3.1-8B-Instruct`

**Registered policy IDs (planning only; not eight real completed integrations):**

- `ucode_conditional_bes`
- `ucode_unconditional_bes`
- `no_uncertainty_search`
- `uncertainty_only`
- `fixed_testing`
- `selective_verification`
- `mcts_search`
- `replay_search`

Do **not** silently reinstate earlier exploratory lists (e.g., Qwen3-8B, Granite-3.3-8B, Gemma-3-4B, or the seven-item baseline sketch) as the canonical confirmatory matrix. New arms require an explicit versioned protocol amendment. The present first-party references cannot support an empirical performance effect.

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

## Scientific stage gates (updated issue tracker; not a completion claim)

The 24 October sketch used an exploratory M0–M4 naming scheme. The current [research issue tracker](https://github.com/Rocky5502/U-CODE/issues) defines the actionable labels and **all listed acceptance gates remain open**:

- **M1 / issue #1:** read-only PR metadata screening plus independently reviewed patch, rights and attribution checks; leads are not accepted executable tasks.
- **M2 / issue #2:** independently reproducible, safely executable, rights-cleared and lineage-disjoint task benchmark; a small pilot precedes any forty-task study.
- **M3 / issue #3:** train-only, held-out calibration and failure-risk estimates with independent oracle labels.
- **M4 / issue #4:** real budget-aware multiobjective acquisition, paired equal-budget controls and uncertainty-mechanism ablations.
- **M5 / issue #5:** six chosen checkpoints with immutable revision and license/runtime/hardware approval.
- **M6 / issue #6:** evidence-grounded Springer manuscript and independently inspectable replication artifact.
- **G5 / issue #7:** separate PHP/Go source-era independent-oracle and human admission gate, which currently blocks the first externally runnable task.

Offline synthetic references, mathematical crosschecks and a first-party canary are useful groundwork **but close none of these real-world scientific gates on their own**. The [3 November verified checkpoint](UCODE_RESEARCH_PROGRESS_2026-11-03.md) gives a dated, source-audited progress denominator.

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
