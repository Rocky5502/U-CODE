# MCEA finite diagnostic observability, frozen kernel identity, and limited-horizon identification bounds

**30 October 2026.** This is a mathematical/source-integrity research audit of authored synthetic likelihoods, **not** a real code-repair result, a risk guarantee, or proof of scientific firstness.

## Research question

MCEA represents both (1) patch acceptability `Y` and (2) the reliability hypothesis `theta` for diagnostic tools as **latent**. Two distinct latent atoms may disagree on code correctness while producing exactly the same observable diagnostics. If so, a coding policy cannot distinguish them just by purchasing more of the available, bounded tools.

This is a fundamental experiment-design constraint: a policy that *acts confident* after repeated observationally redundant checks is not learning the disputed predicate.

## New integrity safeguard: the evidence kernel cannot silently change

The existing `CoherentBeliefState` previously bound only a list of `scenario_id` strings to joint posterior masses. A caller could supply different likelihood rows under the same scenario name between evidence receipts. That violated the meaning of Bayesian belief propagation under a frozen model family.

Each state now carries the **versioned SHA256 digest of the complete frozen conditional likelihood table**, including action names, *ordered* visible histories and both class-conditional binary likelihoods. Deterministic JSON arrays and IEEE-754 `float.hex()` representations avoid the delimiter ambiguities present in prior research tools. Reordering the frozen row list cannot change the digest, while changing any likelihood value, observation history, or action name does.

Every planning and receipt update checks that each scenario ID is associated with the exact same digest, and each successor state carries those digests unchanged. SHA256 here proves only **input consistency within the repository's trusted runtime**, not authorship, independent review, provenance of a training set, third-party attestation, or that the hypothetical calibration probabilities are valid.

## Finite observational equivalence

For two source-model/truth atoms `z=(theta,y)` and `z'=(theta',y')`, and public history `h`, let

```text
p_z(a,h) := P(O_a=+ | theta,y,h).
p_z'(a,h) := P(O_a=+ | theta',y',h).
delta(a,h) := |p_z(a,h) - p_z'(a,h)|.
```

The auditor enumerates every feasible adaptive diagnostic purchase with at most `H<=4` steps, at most 6 globally single-use actions and hard five-resource caps. Its recursive search covers only histories reachable under **both** atoms. If either model lacks a likelihood row at a common reachable history it **fails closed**; it does not silently back off to independence. It accepts no real-task gold labels.

**Equivalence proposition (fixed modeled experiment only):** If `delta(a,h)=0` for *all* feasible actions at *all* shared reachable public histories, then every admissible adaptive policy produces the same public observation transcript distribution under `z` and `z'`. For every shared outcome, the posterior odds between `z` and `z'` remain unchanged. The proof is induction on the action/outcome sequence: policy action choice depends only on the shared public history, while Bayes multiplies each atom's weight by the **same** outcome likelihood. This does **not** imply that either atom's posterior mass individually remains unchanged in the presence of other models.

The implementation gives a first concrete `(action, history, p_z, p_z')` witness if strict equality fails. It does not use a floating tolerance to certify equality of different represented probabilities.

## Quantitative bound, even when atoms are not exactly equivalent

Let `epsilon_H` be the largest `delta(a,h)` among *shared reachable* action/history pairs within horizon `H`. For any adaptive policy constrained to those actions and budgets, sequential maximal coupling of the binary observations yields

```text
TV(P_z(transcript), P_z'(transcript))
    <= min(1, H * epsilon_H).
```

**Reason:** If the public histories have not yet diverged, their next actions are chosen by the same policy from the same history. A maximal coupling of their Bernoulli outcomes fails to agree with probability precisely `delta(a,h)<=epsilon_H`. By the union bound, at most `H` such opportunities can produce divergence. Thus the transcript distributions have total variation no larger than the bound. This is a deliberately *loose upper bound*, not an exact optimal adaptive TV calculation.

For a prior normalized **only within the two competing atoms**, let `pi_z=b(z)/(b(z)+b(z'))` and `pi_z'=1-pi_z`. If `y != y'`, then any estimator of their correctness class based solely on an admissible diagnostic transcript has conditional binary Bayes classification error at least

```text
P(error | Z in {z,z'}) >=
    min(pi_z,pi_z') * max(0, 1 - H * epsilon_H).
```

The inequality follows from `int min(pi_z f_z,pi_z' f_z') >= min(pi_z,pi_z') * int min(f_z,f_z')`, and `int min(f_z,f_z')=1-TV(f_z,f_z')`. The bound is **conditional on the pair**, not the unconditional error rate across the whole dataset or a certified correctness error on real code. If both atoms agree on `Y`, this pairwise correctness error lower bound is inapplicable (`None`). If `H=0` or no actions are affordable, it reduces to the lesser normalized pair prior.

The auditor computes `maximum_shared_history_discrepancy`, `adaptive_transcript_tv_upper_bound`, and `conditional_two_atom_error_lower_bound`. The quantitative result is only as good as the **frozen hypothetical likelihoods**: it is not guaranteed to apply when the true diagnostic distribution is outside the model set, when action availability differs by hidden state, or if a policy receives additional information absent from the modeled public transcript.

## Independent exact-rational falsifiers

`tests/test_observability_coupling_bound.py` enumerates fixed-action transcript probabilities using Python's independent `Fraction` arithmetic and computes the exact binary total variation, **without using the audit's bound to construct its reference**.

Illustrative witness with two independent probes under hypothetical positive rates `p_z=5/8`, `p_z'=3/8`:

- One-step binary TV is `1/4`.
- The exact **two-step transcript TV is 1/4**, because the two-sample middle outcome mass is equal under both models.
- The union/coupling bound returns `min(1,2*(1/4))=1/2`.
- For equal conditional pair priors, the true two-class Bayes classification error is `3/8`, whereas the conservative lower bound is `1/4`.

We explicitly test that the upper bound is **not mislabeled as tight**. Other tests cover exact indistinguishability, a perfect calibrator, asymmetric pair priors, zero-horizon/no-budget cases, same-class atoms, context caps, and a full `3 x 3 x 3 = 27` point rational grid for exact TV versus the computed upper bound (three likelihoods on each atom and horizons 0/1/2). These are not 27 independently observed repair tasks.

The original `tests/test_finite_observability_audit.py` also checks a delayed witness that is invisible to one-step diagnostics but appears after a shared first-step observation; it guards against a misleading root-only observability check.

## Consequences for U-CODE experiment design

An empirically credible experiment must distinguish:

1. **Hypothesis identification:** Do calibration-like tests distinguish tool-origin, test-generator, or repository-dependent evidence interpretations?
2. **Correctness identification:** Do those distinctions actually improve an independently sealed full-task correctness decision?
3. **Cost:** Is identification possible within the *same* tokens, test calls, GPU seconds, CPU seconds and wall-clock limits as the comparators?
4. **Coverage:** Does conservative release merely abstain more, lowering the raw wrong-release numerator while leaving accuracy-at-coverage unchanged?
5. **Misspecification:** Do models fitted only on training/fork-separated repositories generalize to a held-out repository and genuinely different test-generation procedures?
6. **Control:** Does a calibrated multi-step controller improve against a strong fixed-kernel planner, uncertainty-free search, random/greedy diagnostic selection, and a no-calibration ablation?

The leading hypothesis is **decision-relevant calibration under costly, imperfect code diagnostics**. Basic POMDP model learning and active sensing are established literature, and the elementary likelihood-ratio/coupling arguments do not constitute a new fundamental theorem. The contribution must ultimately be demonstrated in rigorous **software-engineering decision outcomes**.

Background sources (independent literature, not proof of U-CODE success):

- Ross et al., *Bayes-Adaptive POMDPs*, NeurIPS 2007: https://mlanthology.org/neurips/2007/ross2007neurips-bayesadaptive/
- Ross et al., *A Bayesian Approach for Learning and Planning in POMDPs*, JMLR 2011: https://www.jmlr.org/papers/v12/ross11a.html
- Ceka et al., *Understanding Automated Program Repair Agents Through the Lens of Traceability*, ISSTA 2026: https://d3ccyth396mz21.cloudfront.net/publications/understanding-automated-program-repair-agents-through-the-lens-of-traceability-an-empirical-study

**Current study status:** no externally admitted executable code-repair task, no sealed independent functional oracle, no six-model matched experimental result, and no empirically measured calibration or code correctness improvement.
