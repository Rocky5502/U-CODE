# U-CODE: correlation-aware joint-truth archive search

**Checkpoint:** 27 October 2026 (Beijing local date)  
**Status:** exact bounded synthetic mathematical reference; **not** trained,
calibrated, physically metered, deployed or empirically evaluated.

## Scientific question

Does dependence between the acceptability of two generated patches alter
which diagnostic or repair should be purchased under the same budget?

The existing `joint_conditional_bes.py` plans across archived patches but
updates each patch's acceptability probability independently. That misses
shared-error structure: patches from the same generator, prompt, repository
issue or template may fail together or be mutually exclusive solutions.

New `src/ucode/correlated_archive_bes.py` instead represents a frozen
**joint probability distribution over all candidate acceptability bits**.
It uses the same policy-neutral `matched_opportunities.py` action-target
menu and `matched_session.py` ledger as the uncertainty-free comparator.
The private joint distribution is never given to that comparator.

## Exact mathematical model

For K real candidates in SHA256-sorted order, let
`Y=(Y_1,...,Y_K) in {0,1}^K` be **latent**, never an observed
evaluator verdict. A finite prior `q_0(Y)` must sum to one.

For a binary diagnostic on target i, with visible outcome z, a frozen
history-conditioned kernel provides `L(z|Y_i,h_i,action)`.
The update is:

```text
q_next(Y) = q_current(Y) * L(z|Y_i,h_i,action)
            / sum_Y' q_current(Y') * L(z|Y'_i,h_i,action)
p_j = sum_Y Y_j * q_next(Y)
```

Even if only i was tested, `p_j` may change for j != i because
`q_current` need not factorize. The planner replays **only visible**
diagnostic outcomes, in shared receipt chronology, using exact
candidate-specific history rows. Impossible observations fail closed.

For repair of parent i, the frozen model additionally specifies:

- `P(new patch produced | Y_i, h_i, repair)`
- `P(child acceptable | produced, Y_i, h_i, repair)`

On publicly visible production failure, the latent parent/sibling
distribution is reweighted by `P(not produced | Y_i, ...)`.
On production success, a **symbolic** child bit is appended and split
according to its conditional acceptability. The child correctness bit
is never observed; a real executor-produced SHA is required before
committing to the shared archive. Target-free generation is restricted
to a production forecast independent of the existing truth vector.

The finite Bellman recursion chooses among terminal release/abstain,
diagnostics, generation and repair, enforcing all five hard **nominal**
resource dimensions and charging preregistered scalar planning prices
exactly once. The reference limits initial candidates to 8, hypothesis
atoms to 512, horizon to 4 and expanded states to 100,000, failing
closed when caps or frozen model coverage are exceeded.

## Falsifiable synthetic policy reversal

A constructed three-patch example has **identical per-patch marginal
acceptability (0.5 each)** in two worlds:

1. **Independent world:** A, B and C correctness bits independent.
2. **Dependent world:** A and C exactly anti-correlated; B independent.

Two candidate-profile-specific tools are available to both policies:
`probe_a` (95% sensitivity, 95% specificity for A/C, uninformative
for B) and `probe_b` (perfect for B, uninformative for A/C).
Both action IDs may target any candidate; the menu is identical.

With one action, no scalar resource price, and a maximum predicted
failure gate of 10%, the stipulated finite model predicts:

| Prior | First action | Expected synthetic release utility |
|---|---|---:|
| Independent | `probe_b` on B | 0.50 |
| A/C anti-correlated | `probe_a` on A | 0.90 |

The dependent prior makes either sign of `probe_a` identify a
candidate with posterior acceptability 0.95 (A or C); under
independence, the negative sign identifies no releasable candidate.
This **analytical counterexample** shows why matching only marginals
is insufficient for optimal evidence acquisition. It is **not**
evidence that a real coding agent benefits from correlation modeling.

## Implementation and tests

- [Algorithm](../src/ucode/correlated_archive_bes.py)
- [Adversarial synthetic tests](../tests/test_correlated_archive_bes.py)
- [Original factorized joint planner](../src/ucode/joint_conditional_bes.py)
- [Common public action-target menu](../src/ucode/matched_opportunities.py)
- [Canonical manuscript](../paper/overleaf/main.tex)

Tests cover positive/negative correlation, independent priors, same-marginal
policy reversal, producer-conditioned failure information, correlated
child truth, symbolic generation before testing, replay of visible
diagnostics, missing kernels, zero-likelihood evidence, missing forecasts,
nonmatching real SHA archives, probability normalization, support caps,
state caps, target-free producer restrictions and off-policy receipt rejection.

## Critical limitations and next scientific gates

1. **No empirical joint prior or diagnostic kernel.** Estimate and
   validate these only from independent, rights-cleared training tasks,
   with reliability/calibration and shift diagnostics. Do not fit to
   held-out sealed evaluator labels.
2. **Dependence is limited.** The joint truth prior represents
   correlated patch acceptability, not residual correlation of tool
   errors conditional on all patch truths, mutable shared retrieval
   state, or unobserved task-level latent factors.
3. **No online producer reconciliation.** The finite planner correctly
   conditions hypothetical production branches, but an actual
   generation/repair receipt changes the real candidate roster.
   The implementation now rejects an unchanged input that lacks
   `conditioned_on_producer_receipts_sha256` after any real producer
   receipt. This digest covers **only public producer events** and
   binds a claimed reconditioned prior to the exact production history;
   it does **not** prove the external scorer actually updated the prior
   correctly. A separate frozen, pre-outcome joint scorer must construct
   the next joint prior, consistently conditioned on visible producer
   outcomes; no automatic real-run transition is claimed.
4. **No physical metering.** All five budgets in the current shared
   ledger are nominal reservations or caller-reported consumption.
   The planner's own CPU/wall cost is not independently enforced.
5. **No independent evaluation.** No third-party executable task has
   passed all admission gates; no six-checkpoint experiment, hidden
   oracle, empirical reliability result, or certified selective risk.
6. **Model misspecification may harm decisions.** A tuned
   uncertainty-free search may equal or outperform both Bayesian
   planners. Preserve that negative outcome and report abstentions.

The manuscript contains a dedicated sensitivity-analysis Methods
subsection. GitHub's `ucode-overleaf-sources` ZIP artifact packages
these sources; this is not proof of external live Overleaf synchronization
or publisher-template PDF compilation.
