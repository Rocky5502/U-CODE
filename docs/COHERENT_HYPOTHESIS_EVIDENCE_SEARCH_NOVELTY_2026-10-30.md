# U-CODE: hypothesis-coherent evidence acquisition under unknown diagnostic reliability

**30 October 2026. Status: a first-party mathematical prototype and independent exact-rational tests, not a trained LLM controller or a verified improvement on real code.**

## Why the previous one-step robustness reference is insufficient

Existing `scenario_robust_evidence.py` evaluates each hypothetical
diagnostic kernel `K^(k)` separately. For each kernel it conditions on
an outcome **as though that kernel's identity were known to the
downstream decision maker**, calculates the terminal release utility,
and takes the minimum gain across scenarios. This calculation is useful
as a sensitivity audit of possible **known-kernel policies**, but it
is not the expected value of deploying a policy whose diagnostic
likelihood model is *actually unknown*.

That distinction can change both the sign of evidence value and the
optimal diagnostic sequence. It is not a software exception or a proof
that all scenario-wise maximin estimators are invalid; it is a
**mismatched information-state comparison**.

## Proposed research direction: model-coherent evidence acquisition (MCEA)

For **one fixed, unchanged candidate** let the latent acceptability
be `Y in {0,1}` and the unknown, globally persistent diagnostic model
be `Theta in {1,...,M}`. The two-level policy belief is

```text
b_t(k,y) := P(Theta=k, Y=y | public visible history h_t).
```

Each hypothesis `K^k` is a prospectively frozen collection of
history-conditional likelihoods

```text
L^k_a(o | y,h) := P(O_a=o | Y=y, Theta=k, H=h).
```

Crucially, the SAME `Theta` generates both the first and second
observation. It is NOT re-sampled independently on every action.
For a visible probe `a` and binary observation `o`,

```text
P(o | b_t,a) = sum_{k,y} b_t(k,y) L^k_a(o | y,h_t)

b_{t+1}(k,y) =
    b_t(k,y) L^k_a(o | y,h_t) / P(o | b_t,a).
```

This maintains uncertainty **about code correctness** and uncertainty
**about what the diagnostic outcomes mean**, simultaneously.

### Two predeclared release choices (ablation)

**Mixture gate:** Let `p_t = sum_k b_t(k,1)`. Release only when
`1-p_t <= delta` and expected release utility is positive.

**All-surviving-model gate:** Release only when
`b_t(k,0)/(b_t(k,0)+b_t(k,1)) <= delta` for every hypothesis
with positive posterior mass. If eligible, score release using the
joint-mixture expected terminal payoff. Models that are strictly
impossible under the observed event are not given an artificial veto.
This is a **finite-list conservative policy preference**, not
frequentist certification, a simultaneous confidence bound, or
guaranteed coverage of the true observation distribution.

The initial constructor imposes independence
`P(Theta,Y)=P(Theta)P(Y)`. If model identity and patch correctness
are correlated initially, this is misspecified. Directly supplying a
reviewed alternate joint prior, training-derived scenario weights and
external validation is future work.

### Five-budget finite Bellman planner

With remaining resource vector `B_t` and all globally unused
diagnostic actions `A_t`, the implemented recursion is

```text
V_0(b_t,h_t,B_t) = U_release_or_abstain(b_t)

V_d(b_t,h_t,B_t) =
    max { U_release_or_abstain(b_t),
          max_{a in A_t: c(a)<=B_t} [
              -lambda^T c(a)
              +sum_{o in {+,-}} P(o|b_t,a)
                     V_{d-1}(b_{t+1},h_t+(a,o),B_t-c(a))
          ] }.
```

Actions currently include **diagnostic purchase only**:
`test`, `retrieve`, `static_analysis`; generation and repair
remain outside this model and are NOT silently treated as fully
model-robust. Each action is globally single-use and a resource must
be spent. The planner fails closed if any reachable model has a
missing history-specific likelihood, a visible event is impossible
under all hypotheses, any resource is exceeded, the model set
changes, or the state-expansion cap is reached.

This is **expected-value Bayes-adaptive planning under a given
prior on model identity**, NOT maximin robust dynamic programming.
It uses posterior model learning along each visible branch. The
finite model, exact enumeration, and conservative risk gate are
standard ideas in Bayesian sequential decision theory; our claim
to test is their *utility and failure avoidance in repository coding
agents*, not the invention of Bayesian inference.

## Exact constructive witness: one-step apparent value is spurious

Take `P(Y=1)=.5`, `P(Theta=A)=P(Theta=B)=.5`,
a release gate at predicted acceptability `>=.9`,
correct/incorrect release rewards `+1/-1`, and two actions,
each costing `0.01` (in distinct resource dimensions).

- `cal`: when `Theta=A`, always positive; when `Theta=B`,
  always negative, **irrespective of Y**. This is model
  identification, not a code-correctness test.
- `diag`: when `Theta=A`, positive iff `Y=1`; when
  `Theta=B`, positive iff `Y=0`. Thus `diag` is a
  perfect or perfectly inverted code diagnosis depending on the
  **unknown** calibration model.

The **existing scenario-by-scenario one-step audit** sees a perfect
test in both possible worlds and reports a positive marginal net
gain of `0.49`. But without observing `Theta`, neither sign of
`diag` changes the mixture acceptability from `0.5`: its
**actual one-step deployable value is zero**, so spending `0.01`
is dominated by abstention. `cal` alone identifies model but also
cannot release; it too has zero one-step value after costs.

A **two-step** policy can buy `cal`, then interpret `diag`
under the now-known model. It releases exactly when `Y=1`,
which occurs with probability `0.5`. The net expected utility is

```text
0.5*(+1) + 0.5*(0) - 0.01 - 0.01 = 0.48.
```

Therefore:
- One-step scenario-known audit: apparently valuable `diag`, 0.49.
- One-step coherent unknown-model policy: **abstain**.
- Two-step coherent unknown-model policy: **cal**, then `diag`,
  expected synthetic net utility **0.48**.

This is a fully reproducible **counterexample to conflating
known-kernel scenario values with deployable unknown-model values**,
and to assuming the best one-step action always starts the best
two-step policy. It is not an empirical software-repair effect.

## Independent reference and falsifiers

`tests/test_coherent_hypothesis_search.py` contains a
**separately written `fractions.Fraction` exact-rational Bellman
enumerator**, intentionally independent of the new planner's
Bayes update, release helper, and dynamic-programming recursion.

Test coverage includes 20 parameterized unknown-calibration model
pairs checked against rational expected values, posterior
martingales, model-identification signals, a correct/incorrect
test-sign reversal, zero-probability outcomes, missing rows,
non-repurchasable actions, hard budget constraints, model order,
model identity/digest constraints, and the difference between
mixture and all-surviving-model release rules. The tests also
explicitly contrast the former one-step scenario reference.

Source: `src/ucode/coherent_hypothesis_search.py`.

## Proposed experiment plan, NOT results

Candidate exploratory analysis `RQ7`, explicitly OUTSIDE the
existing frozen six confirmatory RQs unless preregistration changes:

> When diagnostic reliability can shift across repository lineage,
> model family, test origin and issue type, does coherent learning
> of latent evidence reliability improve equal-budget independently
> verified task correctness and selective risk, compared with
> a fixed-calibration search and the uncertainty-free baseline?

Preregister these **matched same-budget** ablations:

1. Existing one-step independent-scenario maximin sensitivity audit.
2. Fixed single fitted kernel (nominal conditional BES).
3. Kernel-averaged one-step diagnostic selector.
4. Multi-step coherent posterior with pooled-only release.
5. Multi-step coherent posterior with all-surviving-model veto.
6. Oracle-known scenario ID **synthetic ceiling only** (never as
   a deployable real-task comparator).
7. No-uncertainty matched action-search baseline.
8. Uncertainty-free, cost-only and fixed-test controls.

Keep identical candidate pool, public action menu, tool backend,
seeds, resources and externally sealed full-task evaluation. Freeze
all scenario weights and likelihoods on **independent training
repository lineages**. Validate held-out log predictive probability,
Brier scores, risk--coverage curves, intervention spending,
wrong-release rate, accuracy at fixed coverage and error under
scenario misspecification; use repository-group bootstrap or
hierarchical uncertainty.

Preregister **negative results** as admissible. A kernel-mixture
planner can be worse if its model family is misspecified, if the
scenario prior is wrong, if calibration probes consume too much
resource, if all-model veto causes pathological abstention, or if
the training panel violates action-selection ignorability.

No true-world confidence set, execution-ready code task, real
LLM outcome, hidden oracle, or physically attested 5-resource
runner has been produced by this module.

## Conservative research positioning (sources checked 2026-10-30)

Related research includes:
- Antoniades et al., SWE-Search (ICLR 2025),
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html :
  MCTS and iterative coding-agent search, not an exclusivity claim
  over search or verification.
- Zou et al., SWE-Verifier (arXiv, 2026-10-21),
  https://arxiv.org/abs/2610.30284 :
  selective verification of candidate coding actions.
- Chen et al., Rethinking the Value of Agent-Generated Tests
  (arXiv, February 2026), https://arxiv.org/abs/2602.07900 :
  generated test frequency is not sufficient as a value claim.
- Adeleke et al., Uncertainty-Aware Self-Correction for Coding Agents
  (AIWILD @ ICLR 2026), https://openreview.net/forum?id=KgQphSXJj4 :
  trajectory uncertainty and selective correction are existing ideas.
- Estévez et al., Timely Clinical Diagnosis through Active Test
  Selection (NeurIPS 2025),
  https://papers.nips.cc/paper_files/paper/2025/hash/7c42e8a9eb471d225a4abec5e79d0153-Abstract-Conference.html :
  model-based sequential test selection predates this project,
  though its context is different.

**Novelty hypothesis:** the combination of **model-aware evidence
meaning**, **decision-based diagnostic spending**, **hard code-agent
resource vectors**, **selective release**, **history-dependent
code diagnostics**, and **independently verified full-repository
repair endpoints**, provided the controlled experiment actually
establishes a meaningful advantage. We do NOT assert that Bayesian
model averaging or sequential information acquisition is novel
in isolation, or that the whole combination is globally first.
