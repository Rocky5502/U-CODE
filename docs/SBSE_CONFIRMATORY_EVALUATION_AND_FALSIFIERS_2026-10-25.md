# U-CODE — Rigorous SBSE confirmatory protocol and falsification gates

**Date:** 25 October 2026. **Target:** Springer *Automated Software Engineering* special issue *Search-Based Software Engineering in the Era of LLMs and Agentic Systems*, official deadline 30 January 2027. **Stage:** prospective protocols and tested first-party evaluator-side code, not empirical efficacy.

## Novelty boundary: choose evidence vs merely verify a patch

**Primary scientific question:** Does jointly choosing coding-agent generation, testing, retrieval, repair and release/abstain actions under *identical five-dimensional resource ceilings* improve independent **full-task correctness at useful release coverage** compared with budget-matched search that is not informed by calibrated uncertainty?

U-CODE does **not** invent independent patch verification, Monte Carlo tree search, Bayesian look-ahead, multiobjective search or risk-controlled selection. Basic Bellman recursion is established mathematics; the current BES implementation tracks one active candidate, while its history-conditional evidence extension handles diagnostics only. It does NOT implement a complete fitted coding agent, learned candidate transitions or a multi-candidate Pareto archive. Any final originality claim requires genuinely new empirically demonstrated search *decision behavior* beyond known methods, not merely a new acronym.

### Three close contemporary sources added to the manuscript

1. [RETRACE: Independent Patch Verification for Coding Agents with a Bidirectional Reconstruct-and-Verify Framework](https://arxiv.org/abs/2608.08950), Li et al. (2026 **preprint**) independently reconstructs and reconciles patch descriptions; prospective close verification comparator, not a U-CODE result.
2. [Dockerless: Environment-Free Program Verifier for Coding Agents](https://aclanthology.org/2026.emnlp-main.640/), Zeng et al. (EMNLP 2026) performs verifier reasoning without running per-repository tests; prospective alternative that may change the cost of evidence.
3. [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://arxiv.org/abs/2609.08149), Zheng et al. (2026 **preprint**) documents misleading hidden tests and gold-answer leakage risks.

These original sources are cited from the Springer BibTeX; do not claim first-of-kind verifier or safe benchmark.

## Eight-policy, six-model prospective comparison

The [machine-readable confirmatory protocol](../configs/confirmatory_sbse_protocol_2026-10-25.json) retains ALL SIX user-selected LLM checkpoints from five publisher families. There are eight planned policies, *not eight currently implemented external agents*:

| Planned role | Policy ID |
|---|---|
| Primary U-CODE treatment | ucode_conditional_bes |
| Primary comparison: identical search/actions, no calibration | no_uncertainty_search |
| Unconditional diagnostic independence ablation | ucode_unconditional_bes |
| Uncertainty-triggered control without explicit search optimization | uncertainty_only |
| Fixed allocated testing control | fixed_testing |
| Selective verifier controller | selective_verification |
| Monte Carlo tree search | mcts_search |
| Trajectory replay search | replay_search |

**Additional important prospective comparators:** faithful RETRACE-style independent verification, Dockerless-style environment-free verification, and SWE-Verifier-style step verification. The current code does **not** reproduce these faithfully; none has been benchmarked. Actual model weights, provider terms, runtime and source task rights are still unverified. The protocol records an *illustrative* budget only, never claims it is a frozen or paid allocation.

## What the evaluator-only implementation checks

[experiment_contract.py](../src/ucode/experiment_contract.py) uses separate **policy-visible run receipts** and **evaluator-only gold verdicts**. The policy receipt contains no oracle outcome. A released patch requires a SHA256 digest and must match the digest evaluated by the independent oracle; abstentions cannot have gold labels. The evaluator-side checker requires a full task × model × seed × budget × policy matrix and refuses:
- missing/duplicated paired cells, invented seed/model or policy substitutions;
- changed pre-fix Git base, model-checkpoint revision, permitted toolset or environment across purportedly matched policies;
- unmeasured/forecast resource costs and violation of *any* token/test/GPU/CPU/wall cap;
- released patches with missing evaluator verdicts, gold verdicts for abstained or failed runs, or wrong patch hash;
- silent exclusion of timeout, safety-stop or infrastructure-failed runs.

**Equal budget means equal assigned upper bounds and allowed tools, NOT identical realized resource expenditure.** Budget savings can be a genuine outcome. All five realized resources must be measured and reported in their own units, separately from any preregistered scalar accounting price. This pure-Python checker cannot prove external oracle independence, task rights or OS-level sandbox isolation.

## Missingness: bounded paired effect rather than biased complete cases

Let s_lower and s_upper be the admissible verified full-task success for an assigned run: both equal its independent 0/1 correctness for a released patch; both equal 0 after abstain, timeout or safety stop with no release; after *external infrastructure failure with unknown outcome*, the conservative interval is [0,1]. If U and B share assigned task/model/seed/budget cells, the effect lies within:

    lower = mean_i(s_lower[U,i] - s_upper[B,i])
    upper = mean_i(s_upper[U,i] - s_lower[B,i])

[attrition_bounds.py](../src/ucode/attrition_bounds.py) reports these **worst/best-case partial-identification bounds** and retains the number of infrastructure failures, timeouts and safety blocks. They are **NOT confidence intervals, risk certificates, causal guarantees or measured treatment effects**. Once independently collected real results exist, separate cluster-aware inferential uncertainty must be reported.

The broader [evaluation.py](../src/ucode/evaluation.py) already supports exact policy success/release/conditional wrong-release summaries and repository-group cluster bootstrap of paired verified success. A policy with **zero releases** has wrong-release conditional risk **undefined**, not zero; any claimed risk improvement must accompany nontrivial coverage.

## Sample size and cost: purely prospective calculation

In an unclustered paired-binary setting, if we *hypothetically* assume discordance probability q=0.25, desired success contrast d=0.10, two-sided alpha=0.05 and power=0.80, a rough normal approximation gives N ≈ (1.96+0.84)^2 × (q-d^2)/d^2 ≈ 188 independent **pairs**. This is an illustrative computation, not an empirical dataset size or final power analysis. Repeated seeds within the same repo/fork **do not create independent repository units**. Cluster effects, multiple models, heterogeneity, released-patch risk and cost constraints could increase the needed study. Therefore the task and model allocation must be frozen *after* a source-separated feasibility pilot and before held-out evidence, without guessing that six models × eight policies × multiple seeds is financially viable.

## Falsification and paper go/no-go

A positive U-CODE claim fails if matched uncertainty-free search achieves comparable verified success; if higher apparent reliability results only from zero release coverage; if correlated self-written tests increase wrong releases; if extra tools/budget explain the result; if repository fork leakage or gold-answer contamination occurs; if benchmark tests are circular or weak; or if simplified competitors are presented as faithful original algorithms. Publish negative findings and audit exclusions.

**Current reality:** 120/120 real PR links metadata-screened, 62 source-path leads, 14 metadata-prioritized manual leads, 2 true pinned admission dossiers, zero independently admitted executable tasks, zero learned real diagnostic likelihoods, zero six-model inference, zero measured advantage. No external third-party programs, paid resources or hidden-oracle labels were executed/used by the current CI.

**Next empirical dependency:** independent file-level rights, frozen pre-fix specification, evaluator-only sealed oracle, approved rootless network-disabled resource-limited runner, frozen model/engine versions, then a small paired pilot on genuine repository tasks. Do not turn research preparation into fictitious Results.

Run `python -m scripts.validate_sbse_protocol` and `python -m unittest discover -s tests -v` locally for first-party offline integrity checks.
