# U-CODE — Deep Research synthesis and research decisions

**Date:** 2026-10-24. **Target:** Springer *Automated Software Engineering*, special issue on SBSE and agentic systems, submission target 2027-01-30.
**Status:** related work and offline engineering advanced; **no empirically measured U-CODE improvement**.

## Reconcile the Deep Research report with current source evidence

The Deep Research report correctly discusses the original first 24-PR audit but its statement that only 24 candidates have been metadata-screened is **out of date**. At the latest canonical repository audit, **84/120 PR links had been attempted, 83 retrieved** and one returned 404. Among the 83 retrieved: **39** preliminary production-source-path candidates, **8** test-only, **35** non-source, and **1** empty changed-file list. Zero are fully admitted to independent runnable study. Another two source-bearing PRs received deeper real commit-level authorship/rights inspection, but neither has independent oracle evidence. Sources: root README and data/audits/2026-10-24. Do not substitute an older convenience-sample denominator for the newer aggregate.

The external Deep Research work package did **not** itself commit GitHub files or update a live Overleaf project. The downloadable ZIP cited in its own report was not mounted in this runtime; rather, the results were critically reconciled and newly authored/committed using our connected GitHub tools.

## Most relevant original literature and novelty threats

New primary-source citations (both October 2026 preprints) now in manuscript and bib:
- [Teaching Agents to Code Reliably](https://arxiv.org/abs/2610.03984) highlights training search/verification behaviors and false acceptance from self-written tests.
- [SWE-Critix](https://arxiv.org/abs/2610.13356) trains trajectory-level completion verifiers. It limits novelty claims about verification and policy critics.
- The prior 23-source matrix already included [SWE-Search](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html) (search), [SWE-Verifier](https://arxiv.org/abs/2610.30284) (selective action verification), [GA4GC](https://discovery.ucl.ac.uk/id/eprint/10216996/) (agent multiobjective optimization), [SWE-Replay](https://arxiv.org/abs/2601.22129) (cost-effective trajectory reuse), and [negative self-correction findings](https://arxiv.org/abs/2608.14659).

The current matrix has **24 entries**. It is a relevant primary-reference literature audit, **not a systematic search proving no closer work exists**. We must not claim first multiobjective coding-agent search or first selective verification.

**Falsifiable U-CODE claim:** A calibrated policy allocating scarce resources between heterogeneous evidence-only tests/analysis/retrieval and actual candidate-producing generation/repair, with independently enforced budget components and a nontrivial release/abstain coverage requirement, may improve independent success versus equal-budget uncertainty-free search and selective verification. It could fail; negative results must remain visible.

## Two separate empirical cohorts

Naturalistic evidence: GitHub/AIDev PR metadata and SWE-chat, requiring line/commit attribution, full file rights, and reliable independent tests. Bot PR account does not identify which patch lines are agent-generated.

Controlled generation: immutable pre-fix benchmark tasks on which **our pinned open-weight models generate new candidate patches**. Source leads include [SWE-rebench V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) and [Multi-SWE-bench](https://github.com/multi-swe-bench/multi-swe-bench). SWE-rebench V2 card currently describes 32,079 tasks and 20 programming languages, warns about possible overlap with non-SWE-bench benchmarks and lists licenses per source repository. Those are **dataset-card claims, not U-CODE observed executable results**. Auxiliary snippet/efficiency datasets must not be pooled with repository-resolution task outcomes.

The [v2 dataset candidate registry](../data/discovery/dataset_source_registry_v2_2026-10-24.csv) records 13 cohort leads with access, licensing and oracle status. No source download or third-party program execution was performed here.

## Six model candidates, no model-weight or license freeze

The [v2 model candidate registry](../configs/models_v2_2026-10-24.json) lists Qwen2.5-Coder-7B, Qwen3-Coder-30B-A3B, Devstral-Small-2-24B, DeepSeek-Coder-V2-Lite, CodeGemma-1.1-7B and Llama-3.1-8B. The original v1 model configuration remains unchanged for transparency.

**No** immutable model revision, tokenizer revision, official license-text approval, runtime compatibility, quantization selection, downloaded weights or model inference has been established for the new candidates. Qwen3 MoE uses more stored parameters than active inference parameters; do not assume its total 30B weight set fits a 16GB VRAM card. Pilot choice of three *feasible* families depends on measured memory/runtime/access and consent for any additional compute.

## Conditional study design, not preregistration or experimental results

Primary contrast: U-CODE full versus search-with-identical-budget-without-learned-uncertainty. Primary endpoint: **independent full-task success**, including abstention as non-success. Secondary: wrong-release risk, release coverage, calibration (proper scores and binning sensitivity), paired action costs and independent security/efficiency when qualified.

Controls: no search, fixed test, random, cost-first, uncertainty-only correction, calibrated selective verification, generative-only, evidence-only and search/replay or MCTS-style when faithfully reproduced. Compare identical tasks, model, seed, prompt permissions, pre-fix snapshot and **all** measured token/test/GPU/CPU/wall budget components.

Freeze train, validation and independent evaluation by repository/fork lineage and time. Estimate diagnostic likelihoods and base patch-success risks using **training** outcome labels only. Hold hidden tests/gold patch completely outside controller/retriever/risk estimator. Evaluation-only code computes full-task success, wrong-release risk and release coverage; an always-abstaining policy has zero successes and undefined conditional error risk. All results and aborted/failed runs count in denominators.

A pilot of roughly **40–60 genuinely runnable tasks**, across three model families and feasible languages, is a *conditional plan* to estimate runtime, task-paired discordance, attrition and cluster dependence. **250–400 distinct tasks** is the external work package's *illustrative* confirmatory range, not a power calculation or fixed final N. Select a primary measured budget after the pilot, then freeze sample size and analysis before reading held-out results. Do not inflate independent N by counting repeated model seeds.

Canonical RQ1–RQ6 numbering remains the same as in [RESEARCH_PROTOCOL](RESEARCH_PROTOCOL.md). The external work package renumbers RQs (starting with calibration instead of failure landscape); silently changing their labels would break issue and paper traceability.

## Changes integrated in this version

- Springer LaTeX Related Work expanded; two bib entries metadata-verified from arXiv original pages.
- New v2 model and dataset candidate registries without silently replacing the existing versions.
- New evaluator-only [evaluation.py](../src/ucode/evaluation.py) for independent full-task success, selective risk/coverage and task-model-seed-budget-matched group bootstrap; synthetic unit tests do not establish empirical effectiveness.
- Springer manuscript now specifies the paired primary contrast and prospective sample-size/measurement requirements.

**Next scientific gate**: independently rights-cleared and executable tasks, original-patch provenance and a genuinely sealed functional oracle, in an approved disposable nonprivileged network-disabled sandbox. Never run untrusted third-party code in ordinary CI.

**GO:** manuscript-level literature synthesis, source and model registries, evaluator-only software/accounting tests.
**HOLD:** independent benchmark results, trained calibration, statistical guarantee under shift, compiled/live-overleaf manuscript and journal submission claims.
