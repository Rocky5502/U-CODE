# U-CODE S03 — matched six-objective Pareto and five-resource hypervolume

**Date:** 9 November 2026. **Evidence class: FIRST-PARTY SYNTHETIC STRUCTURAL VALIDATION.** This is a prospective, evaluator-only quality/cost diagnostic, NOT evidence that U-CODE has run any third-party code-repair task or measured any model's performance.

Related issue: [S03 #63](https://github.com/Rocky5502/U-CODE/issues/63).

## Science: six separate objectives, not one scalar budget

The five mandatory U-CODE resource limits are **tokens, test calls, GPU seconds, CPU seconds and wall-clock seconds**. Those five are never merged into a single feasibility constraint. A scalar resource price used for pre-outcome acquisition planning cannot be used as a substitute for independent postterminal five-vector hard caps.

For a selected **frozen model** and **one frozen budget level**, compare every registered policy on exactly the same original task × seed assignments (`N` per policy). Let `s_p` be the number of released patches that a **caller-declared** evaluator says passed the complete task oracle, and `C_{p,j}` be the sum of the **caller-reported** consumed amount of resource `j` over those same `N` attempts. Declare the per-assignment fixed cap `B_j`.

We use the six-coordinate maximization vector:

```text
z_p = (
    s_p / N,                         # evaluator-claimed full-task success
    1 - C_p,tokens       / (N*B_tokens),
    1 - C_p,test_calls   / (N*B_test_calls),
    1 - C_p,gpu_seconds  / (N*B_gpu_seconds),
    1 - C_p,cpu_seconds  / (N*B_cpu_seconds),
    1 - C_p,wall_seconds / (N*B_wall_seconds),
)
```

All five `B_j` must be **strictly positive** to define this normalized six-objective hypervolume; otherwise we **reject the calculation rather than divide by zero, omit the resource, or invent a reference length**. Every assigned run must separately satisfy all five fixed caps. Costs that exactly exhaust one cap give zero savings on that coordinate and may yield zero six-dimensional hypervolume even if the policy is Pareto-nondominated.

Policy `a` dominates `b` only when `a` is at least as successful, uses no more of **each of the five resources**, and is strictly better on at least one of the six axes. Identical quality and costs are reported as ties, not secretly removed or counted twice. The function reports the complete nondominated set, the policy-specific dominators, identical tradeoff ties, and marginal hypervolume contributions.

## Exact fixed-cap union hypervolume

For a point `z_p` in the six-dimensional unit cube, define the origin-anchored rectangle `[0, z_p]`. The reported normalized hypervolume is **the volume of the UNION of these rectangles**, not a sum of their individual volumes (which would double-count intersections).

The implementation uses deterministic recursive coordinate slicing across all six axes, bounded to **at most eight** policies, which matches the prospective U-CODE factorial design. It is *algorithmically exact for the supplied floating-point coordinates* up to ordinary float arithmetic rounding; it is neither symbolic rational proof nor a statistical uncertainty interval. Policy ordering is canonicalized by stable policy IDs; permutations cannot change the answer. An additional exhaustive subset-based inclusion–exclusion implementation in adversarial tests checks the same volume without reusing the production slicing algorithm.

This score **depends on the fixed reference budget and task denominator**. Do not compare absolute hypervolumes across different model families, budget regimes or assignment sets and call them causal treatment effects. In particular, a normalized hypervolume of zero does not imply that every candidate was incorrect: consuming a full cap in any one resource forces a zero-volume rectangle in the six-dimensional score.

### Difference from the pre-outcome DRPA reference

The repository already contains [dependence-robust Pareto acquisition](../src/ucode/dependence_robust_acquisition.py), a **two-objective, pre-outcome candidate-production planning** reference whose reliability/safety outcomes are hypothetical. S03 does **not** replace that controller or suggest that Pareto optimization is newly introduced. It is a distinct **postterminal six-objective audit**: one axis is task success joined from separate evaluator verdicts only after policy completion and five axes are resource consumption, not forecasted risk/quality. Neither technique constitutes empirical validation before independent benchmark/runner admission.

## Evaluator-only structural admission and no false performance

The [source module](../src/ucode/matched_pareto_audit.py) exposes two distinct entry points:

- `audit_resource_quality_frontier(...)`: a pure finite-geometry structural reference over caller-supplied synthetic or declared points.
- `audit_matched_postterminal_pareto(...)`: uses the existing frozen matrix/oracle-join validator before calculating per-model/per-budget policy statistics. It requires every assigned model × task × seed × budget × policy cell, matching original pre-fix SHA, frozen model checkpoint reference, tool-access identity, released patch/evaluator digest and five-vector cap. It **refuses** an incomplete, timed-out, safety-stopped or infrastructure-failed registered matrix instead of fabricating a definitive correctness score. Separate missingness sensitivity remains the job of S02.

All outputs keep **false** flags for independent telemetry, hidden-oracle authentication, executable task/model qualification and approved real trials. SHA strings, Boolean verifier verdicts and `actual_costs_measured=true` in source-controlled input are *not* independent signatures or trustworthy physical metering. No hidden test artifact, patch content or evaluator log digest is exported.

The original 6-model × 8-policy study has **zero** independently admitted executable tasks and **zero** qualified six-model runs; PHP #104 and Go #43 have 16/16 independent admission gates pending.

## Reproducible first-party regressions

```bash
python -m unittest discover -s tests -p 'test_matched_pareto_audit.py' -v
python -m unittest discover -s tests -p 'test_experiment_contract.py' -v
python -m unittest discover -s tests -v
```

The [27 S03 adversarial cases](../tests/test_matched_pareto_audit.py) cover:

- Each individual five-resource cap overrun and all possible zero-cap dimensions.
- Strong six-axis domination, Pareto tradeoffs, equal policies/ties and independence from catalog order.
- Exact overlapping-box union volume versus an **independent** inclusion–exclusion calculation over deterministic synthetic 2–4-arm instances.
- All-zero quality; policies which exhaust one cap; benefit/resource correlations; nonfinite quality; budget and policy identity drift.
- Fractional **means** for integer token/test counters handled via integer **totals** across matched assignments.
- Original matched assignment denominator preserved, missing or mismatched evaluator verdicts rejected, altered checkpoint identity rejected, and nonterminal attrition blocking definitive success hypervolume.

**Not tested or claimed:** physically measured GPU seconds, external task rights, a real oracle, independently accepted model licenses, model weight checksums, successful model inference, or significance/generalization of a Pareto frontier. The Springer's manuscript source is edited in GitHub only and is not proof of live Overleaf synchronization.

## Work remaining for science, not code ceremony

Actual scientific evaluation requires an independently rights-approved source-era task and sealed functional oracle; rootless isolated runner and independently authenticated physical five-resource meters; six real pinned model checkpoints with rights, tokenizer, weights and measured load; all eight faithful policy comparators; preregistered independent group splits; and matched real outcomes. Until then, present S03 only as an inspectable **prospective method and first-party source validation**.
