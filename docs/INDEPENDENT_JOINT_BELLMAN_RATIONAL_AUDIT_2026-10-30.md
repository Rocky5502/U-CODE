# Independent exact-rational verification of U-CODE's joint Bayesian archive solvers

**30 October 2026 — mathematical code validation, NOT an empirical result.**

## Scientific question

The factorized whole-archive planner and the correlated latent-truth
planner both claim exact finite-horizon Bellman evaluation *under their
supplied hypothetical probability models*. That is a restricted
mathematical claim that can be **falsified** with an independent oracle
rather than only tests written against the same implementation.

The new reference is
`tests/test_joint_archive_exact_rational_oracle.py`. Its reference
calculations use Python's `fractions.Fraction`, enumerate every
possible latent truth assignment and visible binary diagnostic
outcome, and **never call either U-CODE planner, Bayes helper or
terminal-utility helper inside the exact oracle**. It compares
complete optimal expected net utility and (when nonterminal) the
initial target-bound choice.

## Exact mathematical specification

Let the candidate acceptability bits be
`(Y_A,Y_B) in {0,1}^2` and let `q(Y_A,Y_B)` be an explicitly
specified rational joint prior. The reference has two binary
diagnostics `a` and `b`, each globally usable at most once and
each applicable to **either** candidate. Conditioned on a target
truth bit, each diagnostic has a rational sensitivity and
specificity, and observations are independent across diagnostics
given the truth assignment.

A feasible probe at target `i` has outcome probability and
posterior obtained by **direct enumeration of the four truth atoms**:

```text
P(z | action, i) = Σ_Y q(Y) P(z | Y_i, action)
q(Y | z, action, i) =
    q(Y) P(z | Y_i, action) / P(z | action, i)
```

At depth `d` the independent reference maximizes:

```text
V_0(q) = max(0, max_i U_release(P_q(Y_i=1)))
V_d(q,used) = max(V_0(q),
    max_{action not in used, target in {A,B}}
       [ - price(action)
         + Σ_z P(z|q,action,target)
             V_{d-1}(q_z,used U {action}) ])
```

The terminal release rule has a *predicted* failure ceiling 0.1,
correct release reward +1, wrong release penalty -1 and
abstention utility zero. This is a policy rule, **not a statistical
certificate**. The action vector has separate test-call and CPU
constraints (each one unit), with fixed scalar prices for planning.

## Audited hypothetical configurations

| Mathematically independent check | Cases | Tested solver(s) |
|---|---:|---|
| Independent two-candidate truth priors: 4 A priors × 4 B priors × 3 action-a strengths × 3 action-b strengths | **144** | Factorized + correlated |
| Four different joint truth structures × 3 strengths × 3 strengths | **36** | Correlated |
| Impossible positive-evidence branches with a deterministic false prior | **1** | Factorized + correlated |
| Target-free generation, possible production failure, and then optional verification, with and without an unchanged incumbent: 4 production probabilities × 3 new-patch priors × 2 incumbent conditions | **24** | Factorized + correlated |
| **Total parameterized configurations** | **205** | Complete Bellman value |

This is 205 fixed **toy model configurations**, not 205 executable
tasks, not 205 external LLM results and not 205 statistically
independent samples. Some model configurations overlap conceptually;
the tally is coverage for mathematical regression only.

### Further independent producer calculation

When a generator succeeds with probability `q`, proposes a patch
with acceptability prior `p`, has nominal cost `c_g`,
and a perfect follow-up test costs `c_t`, an existing unaffected
candidate may still have terminal value `u`.

For a horizon of two, provided the tester can use the same candidate
after generation, the exact expected release value is

```text
V = max(u, -c_g + (1-q)*u
             + q*max(u, p*1 + (1-p)*u - c_t))
```

This explicitly charges generation cost on **both production success
and failure**, but charges the test only on a successful branch where
verification is worthwhile. An unused unchanged incumbent survives
both diagnostic outcomes. This rational expression is independent
of the implementation's candidate-archive internals.

The test evaluates `c_g=0.01`, `c_t=0.02`, plus different
`q,p` and `u=0` or `u=0.84`. It does not model parent-truth
dependent repair or the full multiobjective Pareto frontier.

## Reproduce

```bash
python -m unittest discover -s tests -p 'test_joint_archive_exact_rational_oracle.py' -v
python -m unittest discover -s tests -v
```

A passing check establishes **consistency with these precisely
defined finite probability models only**. It cannot establish:
calibration of `q` or diagnostic likelihoods on held-out
repository groups; model identifiability under biased action
selection; oracle independence or physical metering; production
runtime safety; risk guarantees; or empirical superiority over
uncertainty-removed search.

The candidate-factorized planner and joint truth planner are not
universally interchangeable: they should agree on independent
priors and correctly modeled independent evidence, but can select
different actions under genuinely correlated candidate truths.
The strict finite model, correlated error assumptions and their
possible misspecification remain central research risks.

**No new real-task U-CODE outcome is claimed.**
