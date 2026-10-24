# U-CODE G3/G4/G7 — dataset admission and leakage-safe diagnostic fitting

**Date:** 2026-10-24. **Status:** STATIC CONTRACTS AND TRAINING-ONLY REFERENCE IMPLEMENTED, NO EXTERNAL STUDY TASK EXECUTED OR ELIGIBLE.

This specification accompanies [task_gate.py](../src/ucode/task_gate.py), [diagnostic_fit.py](../src/ucode/diagnostic_fit.py) and their regression tests. A green unit-test result is not independent verification of generated software.

## A. Immutable task groups and train/evaluation isolation

The prediction unit is a candidate patch on an immutable pre-fix repository snapshot. The grouping unit is a repository/fork lineage (not PR ID). Maintain non-overlapping sets named train, validation and evaluation, with chronological boundaries and fork/near-duplicate collapse before splitting.

Train-label access is limited to train groups. Validation may be used for frozen-model selection, but then requires a separate untouched outer evaluation cohort. Evaluation outcomes remain sealed until all policies, budgets, estimators, thresholds and analyses have been frozen. The fitting API rejects nontrain lineage groups, unknown groups, duplicated task IDs, cross-model/action mixing and insufficient positive/negative training evidence.

Each training record explicitly includes a pre-outcome visible diagnostic timestamp and a later independent training-oracle timestamp, plus an oracle identifier. These metadata restrictions reduce accidental leakage but **cannot independently attest that the real diagnostic was executed before the oracle or lacked access to the gold patch**. Preserve independent execution and audit logs.

## B. Estimating one diagnostic channel

For diagnostic action \(a\), define \(Y_i=1\) as an independently acceptable patch and \(O_i=+\) as positive visible diagnostic evidence. On training records alone, estimate:

\[
\widehat{\mathrm{Se}}_a =
\frac{\#\{Y=1,O=+\}+\eta}{\#\{Y=1\}+2\eta},
\qquad
\widehat{\mathrm{Sp}}_a =
\frac{\#\{Y=0,O=-\}+\eta}{\#\{Y=0\}+2\eta}.
\]

Default symmetric smoothing is \(\eta=1\), with at least **five positive and five negative training tasks and two repository-lineage groups**. These minima are software sanity limits only, **not** a sample-size or power recommendation for journal experiments. Raise and preregister scientific thresholds before evaluating held-out outcomes.

The frozen fit stores specific action/model identity, class counts, group count, estimated sensitivity/specificity and a stable input fingerprint. It exposes a typed forecast for the existing budget-constrained controller. It does **not** calibrate the prior probability of patch success, guarantee selective risk or establish actual intervention value. Independently calibrate a base patch-success predictor before using this likelihood to drive real decisions.

Do not assume conditional independence between diagnostics or between multiple test outcomes. Action selection may also cause selection bias in observed tool results; prespecify randomization or justified propensity methods for causal claims. A confidence score and a posterior risk-threshold policy do not amount to a statistical risk guarantee, especially after policy selection or distribution shift.

## C. Fail-closed task-evidence gate

A task-admission record requests immutable base/patch revision hashes, repository/fork lineage, actual changed production-source paths and language, cohort type, review references for authorship or new-generation trace, source-file rights and independent oracle, a hash of the independent oracle and a pinned container image digest.

It requires declared evaluator-only oracle access, nonroot runtime, disabled network, no host mounts, and CPU/memory/time resource controls. The checker returns **blocked** with explicit reason codes or **declared_complete_requires_independent_verification**.

There is intentionally **no verified-eligible result**: static boolean fields or typed review IDs cannot prove that a human completed licensing review, that code was genuinely AI-authored, that the oracle is independent, or that sandbox restrictions actually work. A trusted human review, rights check, security test and isolated oracle replay remain external hard gates.

No arbitrary third-party repository code may run in U-CODE's normal GitHub Actions; its unit tests contain only invented, first-party fixture metadata.

## D. Integration plan / study gate

1. Complete read-only screening of the 120 discovered PR links and report honest attrition.
2. Obtain legally reviewed executable tasks; separate naturalistic AI-agent PRs from tasks on which our models generate entirely new patches.
3. Freeze repo/fork/time split and a hardened network-off, privilege-restricted sandbox with no credentials/host mounts.
4. Log diagnostic observations before evaluator-only hidden tests; keep raw immutable source identifiers.
5. Fit diagnostic kernels on labeled **training** tasks and a separately trained/calibrated patch-success prior. Freeze both before held-out evaluation.
6. Measure conditional diagnostic likelihood validity and cost in untouched validation groups; quantify shift and scarcity.
7. Compare no-uncertainty search, fixed testing, selective verification and full intervention selection on identical model/task/seed and vector budget.
8. Evaluate full-task independently verified success, accepted-set wrong-release risk, coverage, paired effects and cluster-level uncertainty, including all failures and null effects.

**GO:** reproducible software reference, provenance contract, split/temporal rejection checks. **HOLD:** any claim of a rights-cleared or executed third-party task, fitted real-model calibration, selective-risk certification or completed RQ1–RQ6.
