# U-CODE dated block — vector-budget planning and Overleaf source export

**Date:** 2026-10-24  
**Scope:** R1 senior SBSE / R2 calibrated evidence scientist / R10 release/reproducibility / R12 Springer editor  
**Before:** main `83144190da9ab9a5a0a4aa3a64dc4f276648a577` (69 prior offline tests).  
**Gate:** G5 reference intervention policy and G11 paper-only source release.  
**Canonical GitHub project:** https://github.com/Rocky5502/U-CODE.

## Changes

1. Added `src/ucode/vector_policy.py` with five-dimensional token, test-call,
   GPU, CPU and wall-time accounting. Two distinct forecast types represent
   diagnostics (test/static analysis/retrieve, updating current-patch beliefs)
   and generative transitions (generate/repair, adding/changing candidates).
   All forecasts are **pre-outcome external hypothetical inputs**, not trained
   estimators. Expected diagnostic value derives from the reference binary
   Bayes model; generative forecasts supply expected *terminal* utility. Both
   are compared in the same utility units before charging preregistered
   resource prices exactly once. All hard resource budgets are respected;
   a policy returns release/abstain when further action does not pay.
2. Added `tests/test_vector_policy.py`, 16 tests for independent budget
   constraints, refusal of invalid or free tools, posterior-risk gating,
   deterministic tie behavior, and decision/terminal logic.
3. Updated `paper/overleaf/main.tex` to describe the one-step decision
   approximation, the mutually exclusive diagnostic/candidate distinction,
   release/abstain semantics, hard vector budgets and honest limitations.
4. Updated `paper/overleaf/README.md` with official-template import, corrected
   six-keyword count, and precise Git vs GitHub synchronization limitations.
5. Added deterministic allowlisted `scripts/export_overleaf.py` and three
   offline exporter regressions. The emitted ZIP includes only main.tex,
   references.bib, README.md and source SHA-256 checksums; no model/data,
   credentials or unlicensed third-party code.
6. Extended the GitHub Actions CI workflow (Python 3.12 job) to build and
   attach `ucode-overleaf-sources` as a downloadable workflow artifact.
7. Updated top-level README instructions.

## Independent checks

- CI run: https://github.com/Rocky5502/U-CODE/actions/runs/40074972900
- Python 3.10 and 3.12 offline unit suite: **91 tests passing** at commit
  `f1cb54eb9195b511bb74bba148a5812d8eb9d15f`.
- Artifact verified: **ucode-overleaf-sources** (11,548-byte Actions artifact ZIP
  containing the compact source bundle).
- Source-only artifact is **not** the Springer publisher template and was
  **not compiled in Overleaf**.

## Gating and next priority

There is no connected Overleaf write tool or authorized Overleaf project in this
session. GitHub commits do not automatically update a real Overleaf editor,
and Overleaf GitHub synchronization itself requires an eligible authenticated
project and user-side sync actions. The GitHub file is the canonical source;
use the per-commit workflow artifact to import into official Springer
`sn-jnl` template (without overwriting collaborator changes).

**Go:** offline decision-model reference, publication-safe manuscript source
export, deterministic artifact verification.

**Hold:** no externally validated action likelihoods, actual learned policy,
safe task execution, true calibration or RQ results. No premium resources or
paid APIs were used; no scientific performance gain is claimed.

**Next independent task:** isolate a licensed executable task subset and train
pre-outcome diagnostic probability models without hidden-oracle access. Then
compare budget-matched no-uncertainty search with adaptive evidence selection.
