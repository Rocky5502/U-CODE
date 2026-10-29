# U-CODE scientific audit: train-only diagnostic likelihood confounding

**29 October 2026 — synthetic and code-level validation only**

## Why the existing estimator was insufficient

U-CODE's two train-only diagnostic estimators previously required a minimum
number of independent repository/fork lineages **globally**, plus task counts
from both acceptability classes. Those conditions do NOT ensure the
class-conditional estimands can be distinguished from repository shift.

Constructive failure case:

- Six labelled acceptable patches all come from repository group A.
- Six labelled unacceptable patches all come from repository group B.
- The original estimator sees 12 labelled tasks, two global groups, and
  both response classes. It can produce a seemingly well-supported
  sensitivity and specificity.
- Neither class has cross-lineage support. Learned likelihoods could
  encode repository identity instead of diagnostic validity.

The problem is more severe with **history-conditioned** observations:
the global training panel may have dozens of lineages, while a
particular action / visible-history / acceptability-class cell only
contains one repository. Its smoothed conditional likelihood can then
be a single-project artifact.

## New fail-closed prerequisites

For the unconditional binary diagnostic fit, define training lineage
sets `G_1={g_i:Y_i=1}` and `G_0={g_i:Y_i=0}`.
The estimator now requires each set to contain at least
`minimum_class_lineages=2` distinct independently assigned groups,
**in addition** to the previous minimum per-class sample counts.

For every observed conditional row `(a,h)` and class `y`,
define `G_{a,h,y}={g_i : a_i=a, h_i=h, Y_i=y}`.
The conditional estimator now requires
`|G_{a,h,y}| >= minimum_lineages_per_context_class=2`
for both classes. Insufficient class/lineage support raises a
`ValueError`; it is never imputed by unconditional likelihoods,
independence assumptions or silently borrowing another history cell.

Both criteria only bound support. **Two lineages do not prove
calibration, independence, sufficient effective sample size, external
validity, correctly grouped forks, unbiased diagnostic assignment,
class balance or independently sealed source labels.** A full study
still needs preregistered order allocation, groupwise uncertainty,
held-out validation, audit of oracle provenance and sensitivity to
selection bias.

## Training input integrity

The old fingerprints concatenated metadata with delimiters:
tabs in `diagnostic_fit.py` and pipes in `conditional_fit.py`.
If an identifier itself contained the separator, two distinct typed
metadata rows could serialize to identical strings and produce
identical SHA256 fingerprints without any cryptographic collision.

Both paths now use **versioned canonical JSON arrays** with explicit
typed fields, deterministic ordering and domain identifiers
`ucode-diagnostic-fit-v2` and `ucode-conditional-fit-v2`.
This changes historical fingerprint digests. Prior fingerprints
should not be compared against V2 as though the schema is unchanged.
These hashes are immutable-input change indicators, **not signatures,
independent evidence of collection, source licenses or trusted time**.

## Reproduction

```bash
python -m unittest tests.test_diagnostic_fit tests.test_conditional_fit -v
python -m unittest discover -s tests -v
python -m scripts.audit_overleaf_sources
```

New adversarial cases explicitly cover:

- global multi-lineage but perfect repository/label confounding;
- a single-lineage `(action, history, acceptability class)` row
  inside an otherwise multi-lineage full-panel training corpus;
- ambiguous historical tab/pipe delimited identifiers;
- deterministic and order-invariant new fingerprints;
- unchanged Beta-Binomial smoothing on supported synthetic fixtures;
- no held-out group labels used in fitting.

These are **engineering / mathematical falsifiers**; there are
still **zero admitted externally executable code-repair tasks**, no
independent sealed correctness oracle, no matched six-model runs,
and no measured cross-repository calibration gain.

## Next stronger scientific checks

1. Independently certify repository/fork lineage clustering in
   train, validation and held-out evaluation.
2. Freeze a randomized full-panel diagnostic collection protocol,
   recording actual inclusion and missingness. A code-set flag saying
   `precommitted_full_panel` is not independent evidence of randomization.
3. Report within-lineage and held-out-lineage sensitivity/specificity,
   class support, calibration uncertainty and selective coverage.
4. Predeclare how sparse histories will cause abstention or excluded
   inference rather than data-dependent post-hoc backoff.
5. Run the complete candidate-targeted controller with sealed,
   independently verified executable software tasks and authenticated
   five-resource accounting **before** claiming an ASE result.

Code: `src/ucode/diagnostic_fit.py`,
`src/ucode/conditional_fit.py`.
Manuscript: `paper/overleaf/main.tex`, training-data restriction.
