# U-CODE exploratory novelty track — Dependence-Robust Pareto Acquisition (DRPA)

**Date:** 6 November 2026. **Evidence class:** first-party bounded mathematical reference and synthetic tests ONLY. No real repo task was admitted, no model inference or independent held-out evaluation was performed. This is not a modification to the registered six-model/eight-policy confirmatory study.

## Exact modeling problem

The current \`src/ucode/acquisition.py\` pilot uses independent truncated-normal marginal quality forecasts. But a generated patch that is functionally correct may be less secure, or failures may be correlated across the two objectives. **Correctness/reliability and safety/security are NOT interchangeable**, and the two marginals do not identify the joint outcome distribution. A high independence-based EHVI may be an artifact of an unvalidated dependence assumption.

To make one limited source-only question falsifiable, DRPA models a candidate-generating action \`a\` with **two specified objective outcomes each**:

- Reliability \`R in {r0, r1}\` with \`P(R=r1)=p\`, \`r0<=r1\`.
- Safety \`S in {s0, s1}\` with \`P(S=s1)=q\`, \`s0<=s1\`.
- \`t = P(R=r1, S=s1)\` is *unknown*, with the exact Fréchet interval:
  \`max(0,p+q-1) <= t <= min(p,q)\`.

Let \`g_ij = HV(archive U {(r_i,s_j)};reference) - HV(archive;reference)\`. The four atom probabilities are \`(1-p-q+t, q-t, p-t, t)\` for \`(00,01,10,11)\`, so

\`\`\`text
E_t[Delta HV] = (1-p-q+t)g00 + (q-t)g01
                + (p-t)g10 + t*g11.
\`\`\`

This is **affine in t**. Its minimum and maximum over all compatible two-by-two joint distributions occur at the two Fréchet endpoints. The method therefore gets **exact coupling-robust lower and upper HVI values with four actual Pareto computations**, without Monte Carlo or a fitted correlation model.

A *separately specified, outcome-independent* validity probability \`v\` multiplies each bound. If validity correlates with reliability or safety, **the displayed bound is not justified**; a larger joint ambiguity set is needed. This restrictive assumption must not be hidden. For each action, the five-resource cost \`c(a)\` is a hard cap, and the separately priced planning cost is \`lambda^T c(a)\`:

\`\`\`text
lower_net(a) = v * min_t E_t[Delta HV(a)] - lambda^T c(a)
upper_net(a) = v * max_t E_t[Delta HV(a)] - lambda^T c(a)
DRPA           = argmax_{a: c(a)<=b, lower_net(a)>0} lower_net(a)
                 otherwise STOP.
\`\`\`

Diagnostic-only test/retrieve/analyze actions do not create candidate Pareto points and are deliberately **excluded**; value-of-information belongs in the existing evidence controllers. Tie-break lexicographically by action ID. The conditional *ranking-stability flag* is true only when the chosen action's lower net gain strictly exceeds the upper gain of **every other feasible candidate-producing action** and the STOP option. It is a deterministic model-conditional inequality, **not a calibrated risk certificate**.

## A falsifying synthetic example (not benchmark effectiveness)

With empty archive and zero reference, proposal \`risky\` has \`R,S in {.1,1}\`, each high with probability \`.7\`, generation cost 1 token, token price \`.01\`. Its independence-based gross HVI is **0.5329**, while the exact dependence-robust range is **[0.46,0.703]** (before cost). A deterministic \`stable\` proposal gives \`R=.5,S=.96\` (gross HVI \`0.48\`) and costs 2 tokens. Independence selects \`risky\` (\`0.5229>0.46\` net), while worst-case dependence selects \`stable\` (\`0.46>0.45\` net). **Neither policy has demonstrated greater real code correctness**. This constructed ranking reversal falsifies the claim that independence does not matter mathematically.

## Executable reference and tests

- \`src/ucode/dependence_robust_acquisition.py\`: \`bound_candidate_hvi\`, \`choose_dependence_robust_action\` and cost-matched \`choose_independence_baseline\`.
- \`tests/test_dependence_robust_acquisition.py\`: 75 independent crosschecks from a \`fractions.Fraction\` grid-union area reference (three archives times 25 marginal pairs), ordering/ties, five independent budget limits, no false Pareto points for diagnostics, stable-winner and adversarial ranking reversal.
- No third-party dependencies, LLMs, benchmark code, GPU, external runner, gold labels, observed risk reduction, or calibration.

## Prospective (not confirmed) research advance

**Hypothesis:** Relative to independent-marginal EHVI and a calibrated joint-correlated acquisition baseline, a dependency-robust acquisition score could avoid wasting scarce generation/test budgets when the cross-objective dependence is weakly identified by training data. The challenge is not proposing a known Fréchet inequality as novel; it is demonstrating that task-conditioned *dependence ambiguity* affects which **repository patch-producing intervention** an agent purchases, and that addressing it improves independently verified task success/cost/coverage under matched action opportunities and five hard budgets.

**Alternative/null:** robust lower-bound search may be excessively conservative, increase abstention, reduce patch diversity, or be dominated by well-fit joint models. In that case the useful result would be a characterization of *when dependence robustness hurts*, not a positive improvement claim.

## Necessary experiment and extension gates

1. **Distribution fit:** on *lineage-disjoint training data only*, fit reliability, safety and validity marginal probabilities; estimate and validate two-point discretization loss versus full continuous support; include both correlated and anticorrelated cases. It is unsafe to treat predicted security warnings as proven security correctness.
2. **Matched controls:** existing independent EHVI, a well-specified learned joint/correlated EHVI (e.g., multivariate prediction), deterministic mean-only Pareto and uncertainty-free search; compare **same candidate opportunities** and exact five hard budgets. Predefine the reference point and scalar price scheme.
3. **Metrics:** independently sealed full-task success ITT (PRIMARY existing contrast unchanged), empirical realized hypervolume, wrong-release risk, release coverage, calibration Brier/ECE, shadow objective correlation, budget use, policy disagreement and decision regret under held-out truth; report nulls.
4. **Novelty disambiguation:** established Bayesian control for coding agents, CATS budget-aware scaling, agentic verifiers, standard EHVI, multivariate joint MOBO and distributionally robust decision theory mean *none* of those primitives may be claimed invented by U-CODE.
5. **Scientific prerequisite:** zero currently independently admitted executable tasks and zero project model checkpoint revisions/real outcomes. This module is an **exploratory M4 methodological ablation**. An explicit versioned amendment is required to add a ninth confirmatory policy arm.

See [novelty comparison matrix](../literature/DRPA_NOVELTY_MATRIX_2026-11-06.md), [issue #4](https://github.com/Rocky5502/U-CODE/issues/4), [issue #2](https://github.com/Rocky5502/U-CODE/issues/2) and the [registered prospective protocol](../configs/confirmatory_sbse_protocol_2026-10-25.json).
