# U-CODE manuscript blueprint (NOT a completed paper)

**Candidate title:** U-CODE: Uncertainty-Guided Search for Reliable AI-Generated Software

**Venue:** Springer Automated Software Engineering special issue on search-based
software engineering, LLMs and agentic systems (deadline 2027-01-30).

**Four keywords:** AI-generated software; uncertainty calibration;
search-based software engineering; agentic code verification.

## Narrative spine

1. **Introduction and motivating failure.** An agent generating plausible
   code faces expensive, competing interventions. Self-confidence is not
   proof and every test call has an opportunity cost. State falsifiable
   research questions, contributions only when supported by evidence.
2. **Background and related work.** SBSE and multiobjective search;
   uncertainty quantification and calibration; generation/testing/repair;
   AI agent provenance datasets; verification and selective prediction;
   clarify differences from adjacent author works.
3. **Problem formulation.** Search over candidate patches and interventions
   with cost budget; state S_t; action A_t; objective vector reliability,
   security, execution and compute; uncertainty-aware acquisition and
   abstention. Define observed versus latent outcomes.
4. **U-CODE.** Components: candidate generator; uncertainty/risk estimator;
   acquisition engine (Pareto + Monte Carlo EHVI); independent verifier;
   provenance ledger; budget/controller trace and intervention policy.
   Explicitly distinguish prototype heuristic from trained/calibrated method.
5. **Dataset construction.** Naturalistic GitHub bot PR cohort, optional
   gated SWE-chat, controlled DroidCollection, executable generated-code
   task cohorts. Source-level licenses, base SHA, sampling/attrition, manual
   annotation, partitioning, validation of oracle independence.
6. **Experiment setup.** Pinned 4–6 models and 12 languages where coverage
   supports it. Compare random search, static-first, fixed test, search
   without uncertainty, confidence-only, quality-only and U-CODE. Equal
   inference/test budgets and repeated seeds. Security and efficiency
   verified separately.
7. **Results** — RESERVED; never add a numerical claim before actual runs.
   RQ1 failure taxonomy; RQ2 calibration; RQ3 equal-budget efficacy;
   RQ4 agent decisions; RQ5 OOD generality; RQ6 mechanism and ablations.
8. **Validity and ethics.** Authorship uncertainty, survivor bias, PR
   sampling, bot aliases, calibration drift, imperfect tests, repo forks,
   leakage, license restrictions and data privacy.
9. **Conclusion.** Only supported reproducible evidence, including nulls.

## Figures (only construct from completed data)

- **Figure 1:** U-CODE architecture and agent state/action/verification flow.
- **Figure 2:** Dataset provenance and attrition flow by cohort and language.
- **Figure 3:** Calibration diagrams / risk–coverage (with uncertainty bands).
- **Figure 4:** Budget-success curves and multiobjective Pareto frontier.
- **Figure 5:** Cross-language and model-family effects / failure taxonomy.

## Tables (placeholders, NOT results)

- T1: Dataset cohorts with independent unit, status, size, access, license.
- T2: Model setup: family, revision, tokenizer, quantization, hardware, seeds.
- T3: Verified success/cost for all policies, with paired confidence intervals.
- T4: Per-language and held-out repo robustness and sample counts.
- T5: Mechanistic ablations and failure case review.

## Minimum evidence before a journal draft is scientific

At least one real failing code example with oracle provenance; runnable test
suite; calibration fitted only on training data; same-budget controls; a
quantified attrition table; independent split; and interpretable negative
cases. The present synthetic smoke test and 120 links alone do not qualify.

## Roles / responsibilities

- **Research lead:** falsifiable novelty and scientific integrity
- **Dataset curator:** sample frame, metadata, licenses, immutable snapshots
- **Provenance auditor:** bot login/PR diff, patch and manual attribution
- **Uncertainty scientist:** proper scoring, calibration, ablations
- **SBSE scientist:** Pareto acquisition, exploration/exploitation, baseline parity
- **Systems engineer:** isolation, tracing, budgets, deterministic builds
- **Statistician:** pairing, cluster-aware inference, confidence intervals
- **Replication lead:** reproducible images, manifests and scripts
- **Adversarial reviewers:** novelty, oracle leakage, generality, null results

These are conceptual workstreams, not claims that separate researchers have
been appointed or experiments completed.
