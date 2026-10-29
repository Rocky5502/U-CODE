# Scientific core correction: incumbent-preserving conditional value of information

*29 October 2026 — U-CODE mathematical and algorithmic regression sprint.*

## Reproducible defect

The former per-patch `plan_conditional_archive` evaluated a diagnostic
against the candidate's standalone utility `plan_conditional(...)` and
then took `max(expected_candidate_utility, best_other_candidate)`
**outside** the predictive expectation. This is incorrect even when
the candidate's diagnostic does not affect any other patch.

A policy that buys a test keeps the ability to release an *untouched*
other patch after observing either diagnostic outcome. The correct
one-step Bellman action value, conditional on a fixed alternate
incumbent, is

```text
Q(test x) = - measured planning price(test)
            + Σ_{z ∈ {negative,positive}} P(z | history,x)
                max( U_release( posterior(x,z) ),
                     best_other_archived_patch_utility,
                     0 )
```

This `E[max(X, incumbent)]` **cannot** be replaced by
`max(E[X],incumbent)`. In fact, `E[max(X,c)] >= max(E[X],c)`;
the inequality can be strict when different branches favor different
candidates. Failure to preserve the outside option on *each branch*
underestimates the benefit of diagnostic switching.

### Independent rational counterexample (NOT real model evidence)

Two synthetic archived candidates A and B, symmetric release rewards
+1/-1, predicted failure threshold 0.1, one perfect diagnostic on A,
and a scalar diagnostic price 0.01:

- A prior acceptability: 0.50, currently not releasable.
- B prior acceptability: 0.92, releasable with utility 0.84.
- If A tests positive (probability 0.5): release A with value 1.
- If A tests negative (probability 0.5): release untouched B with
  value 0.84.
- Expected archive value **after buying test A**:
  `(1/2)*1 + (1/2)*0.84 - 0.01 = 0.91`.
- Best stop value: `0.84`. Expected gross improvement from A test
  over stopping, after price: `+0.07`.

The old independent candidate calculation used `0.5-0.01=0.49`,
then `max(0.49,0.84)=0.84`, and wrongly stopped.
These are **hypothetical exact-rational inputs**, not measurements of
U-CODE correctness or search performance. No new LLM run or evaluator.

## The code correction

1. `plan_conditional(..., *, outside_option=0)` now accepts an explicit
   finite nonnegative terminal fallback utility and applies it at
   *every leaf of the conditional Bayesian evidence tree*. The
   default is zero for backward-compatible one-candidate semantics.
2. `plan_conditional_archive` finds, for each candidate, the maximum
   frozen terminal utility over the **other** archived candidates
   and passes it into the conditional planner. It directly uses
   the corrected expected net utility, without a second, wrong
   `max()` across expectations.
3. The existing cross-candidate correlated belief planner
   (`correlated_archive_bes.py`) is **not** replaced. The corrected
   per-candidate adapter assumes diagnostic outcomes on the tested
   patch do not alter beliefs about siblings. If diagnostics are
   correlated, use the joint solver under its stated finite model.
4. A terminal action reported by the per-patch solver when its outside
   option dominates is not an instruction to release that patch.
   Only the archive controller selects an actual SHA for terminal
   release; the local solver reports no local intervention.

## Independent mathematical and integration checks

- `tests/test_conditional_bes.py` includes an independent
  `fractions.Fraction` derivation of the `0.91` value, budget-price
  sensitivity and invalid outside-option rejection.
- `tests/test_conditional_archive_incumbent.py` tests action
  selection, corrected expected proxy utility, **both** observed
  action outcomes, SHA-specific release choice, immutable action
  budgets, candidate-order invariance and a too-expensive probe.
- `tests/test_independent_archive_outside_math.py` independently
  enumerates **1,152 finite rational one-step Bayes instances**,
  including zero-probability evidence branches, using an oracle
  function that does **not** call U-CODE's mathematical helpers.
  It checks the corrected planner against Fraction values, not
  against itself. This is math regression coverage only.

## Reproduction

```bash
python -m unittest tests.test_conditional_bes
python -m unittest tests.test_conditional_archive_incumbent
python -m unittest tests.test_independent_archive_outside_math
python -m unittest discover -s tests -v
```

## Important scientific limits

The reference remains **partial**, not an optimal general multi-patch
POMDP. It does not update sibling beliefs under correlated
diagnostics, jointly choose future evidence across multiple patches,
learn a calibrated conditional kernel, establish a risk certificate,
run real tools against a PHP project, execute an external LLM or
validate hidden software-repair oracles. A test-suite passing proves
that the stated finite mathematical model is computed consistently
on the reviewed examples, not that U-CODE outperforms competitive
search or verification baselines.

No submitted paper Results claim should cite these synthetic checks
as measured repair success. The first admitted real external task
and independent review are still outstanding.
