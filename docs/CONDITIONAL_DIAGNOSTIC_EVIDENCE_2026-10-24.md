# U-CODE: history-conditioned diagnostic evidence and non-identifiability

**Date:** 2026-10-24. **Status:** first-party algorithm, mathematical counterexample and unit tests; **not** real-model calibration or empirical coding-agent performance.

Implementation: [conditional BES](../src/ucode/conditional_bes.py), [training-only kernel fitter](../src/ucode/conditional_fit.py), [synthetic independence-versus-redundancy example](../examples/conditional_dependence_smoke.py), and 36 first-party tests.

## Motivation and research role

The prior BES uses a conditional-independence assumption for multiple diagnostic channels. That can be wrong when several AI-written tests, code analyzers, or retrieval sources detect the same bug or repeat identical assertions. Repeated positive signals might add no information; independently diagnostic observations might add substantial value. Marginal sensitivity and specificity are inadequate to choose interventions unless the dependency structure is justified. This is a candidate research direction, not proof of algorithmic novelty.

## History-conditional Bayesian diagnostic action model

For a single unchanged candidate and visible, chronological history \(h=((a_1,o_1),\ldots,(a_t,o_t))\), the training-only frozen kernel stores:

\[
q_{a,y}(h)=P(O_a=+\mid Y=y,H=h,A=a),\quad y\in\{0,1\}.
\]

The pre-outcome belief \(p=P(Y=1\mid h)\) updates after a visible positive result using:

\[
r_+=p q_{a,1}(h)+(1-p)q_{a,0}(h),\quad
p^+=\frac{p q_{a,1}(h)}{r_+}.
\]

The negative branch uses complementary likelihoods. An outcome assigned probability zero by the frozen model is a model contradiction and fails closed; a missing history-specific likelihood is rejected instead of silently assuming independence. The finite-horizon dynamic program chooses tests, static analysis or evidence retrieval under all five resource constraints, with explicit terminal release/abstain. It does not model new candidate generation, patch archives or actual tool execution; those remain separate modules.

## Proposition: identical test marginals can imply different optimal first actions

Take a hypothetical candidate prior \(P(Y=1)=0.5\), a release gate requiring posterior \(p\ge0.9\), payoff +1 for correct release and -1 for wrong release, and a scalar price of 0.01 per test. Two possible probes A and B each have *marginal* sensitivity and specificity 0.8.

**Model I (conditionally independent probes).** Two positives yield posterior \(16/17\) and occur with unconditional probability 0.34. A policy buying A and then B only after A is positive gets expected release utility \(0.34(2(16/17)-1)=0.30\) and expected test price \(0.01+0.5(0.01)=0.015\), hence expected net \(0.285\). One positive alone cannot satisfy the release gate.

**Model R (perfectly redundant probes).** B is exactly equal to A on every candidate, even though both maintain identical *marginal* sensitivity and specificity 0.8. After seeing A, B adds zero posterior information. Since the posterior after one positive is at most 0.8, no release can occur, so every positive-cost test plan is dominated by immediate abstention with utility zero.

Thus the two models have equal per-test accuracy and costs, but different optimal first actions (buy A versus abstain). The marginals alone cannot determine multi-step evidence value. This is a basic constructive counterexample, **not a newly established general theorem or an observed improvement on code**.

## Leakage-aware training-only conditional likelihood fitting

The fitter accepts a full precommitted panel of 1–4 named probes on each task, with complete chronological observed outcomes, model identity, repository/fork lineage, and independent training-oracle label recorded later. It refuses unknown/validation/evaluation groups, duplicated task identifiers, different model checkpoints, incomplete or adaptively shortened panels, invalid timestamps, insufficient per-class support in observed contexts, and missing full diagnostic panels. Smoothed class-specific frequencies produce a frozen conditional kernel and input fingerprint.

These software schema gates cannot prove real data were collected under an independent, prospective, randomized test schedule, nor that the training oracle was hidden. Action-order assignment, file rights, provenance, timestamps and physical sandbox restrictions still need independent review. There is no support for imputing missing histories, learning a correct patch prior, generalizing to new repository families, or proving selective risk control.

## Reproducible synthetic demonstration

Run the first-party module named examples.conditional_dependence_smoke to compare two diagnostic systems with equal marginal test accuracy, including explicit synthetic-only warnings. GitHub Actions runs the example on supported Python versions; no external repository source is downloaded or executed.

## Scientific gates and next priority

1. Obtain at least one rights-cleared, independently executable task in a disposable nonroot network-disabled sandbox and seal a functional oracle inaccessible to agent policy.
2. Prospectively log a small fixed diagnostic panel and real tool costs on training repository/fork groups. Separate genuine conditional diagnostic likelihood fitting from evaluation labels.
3. Freeze a separately calibrated pre-outcome patch correctness prior. Evaluate conditional BES versus independence BES, uncertainty-free search, fixed testing and strong selective verifiers under identical vector budgets.
4. Measure wrong-release risk jointly with nontrivial coverage, paired independent success and repository-cluster uncertainty; preserve null findings.

**GO:** dependency-aware finite-horizon reference, synthetic falsifier, training-only data contract, CI. **HOLD:** real learned kernels, real task accuracy gains, source-rights-cleared benchmark, formal statistical risk guarantees, and a submission-ready journal manuscript.
