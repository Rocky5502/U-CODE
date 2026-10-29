# U-CODE — ten senior SE/AI research perspectives: code integrity sprint

**Review date:** 29 October 2026. **Scope:** first-party repository code,
source-only metadata, published-to-repository manuscript source, and existing
offline CI. **Reviewer identities:** ten *simulated disciplinary lenses* used
for a structured technical audit; not ten independent humans and not external
peer review.

**Prior verified baseline:** main commit `f58c36ceaf612f0d5bc4fbb2e6756939d3fbdace`,
1,188 offline unit tests on Python 3.10 and 3.12, no independently admitted
executable task. Every fix in this report is first-party/offline. CI evidence
for the review PR and final merged main commit must be inspected separately.

## Ten disciplinary reviews and actionable conclusions

| Perspective | Code or evidence examined | Finding, decision and outcome |
|---|---|---|
| 1. Senior empirical SE researcher | `evaluation.py`, `experiment_contract.py`, paired task/seed/budget comparisons | **Fixed, high:** same `task_id` could change repository lineage across seeds, models or budget groups and inflate bootstrap cluster count. Enforce one lineage per task throughout outcome accounting. |
| 2. Senior statistical ML researcher | `evaluation.py`, cluster bootstrap and missing-data estimands | **Fixed:** reject Boolean `bootstrap_samples=True` as invalid sample count. **Pending:** simulation-based CI coverage under strongly unbalanced lineage sizes and predeclared bootstrap unit. |
| 3. Dataset/provenance scientist | `external_dataset_intake.py`, 120-PR source catalog and 13-source crosswalk | **Fixed, medium:** two-pass validation consumed one-shot iterables, so malformed discovery identifiers could evade explicit review or crash with `AttributeError`. Validate materialized input first, including `.`/`..` path components. |
| 4. Formal methods and optimization theorist | `vector_policy.py`, hard budget and linear scalar prices | **Fixed:** individually finite per-component costs and prices could multiply/add into `inf` silently; require finite scalarized cost. **Pending:** numerical stability of large finite-horizon trees, plus independent conditional-kernel assumptions. |
| 5. Bayesian evidence modeling researcher | `voi.py`, Bayesian martingale and terminal gate | **Fixed:** per-diagnostic cost and rule penalty individually finite could overflow when multiplied, yielding invalid `-inf` net value. **Pending:** held-out calibration, adaptive-selection and correlated-test validation. |
| 6. Reliable agents and repair systems researcher | `joint_conditional_bes.py`, `conditional_archive.py`, shared action catalog | **Unblocked only for synthetic reference planners:** eight real policies are not yet faithful executable integrations; tool parity must be measured on approved tasks. |
| 7. Security and isolation researcher | `oci_sandbox_preflight.py`, `SECURITY.md`, trusted-executor boundary | **Pending, high:** OCI builder/inspect checks are a structural **dry-run**, not proof of nonroot/no-network execution, repository isolation or cap enforcement. Do not execute third-party source on the host. |
| 8. Reproducibility and systems researcher | `matched_session.py`, `metering_reconciliation.py` | **Fixed, high:** fixed `1e-7` absolute ledger tolerance could hide an entire microsecond-scale resource budget. Replace with resource-scale relative tolerance, zero free absolute slack and adversarial tests. **Pending:** independent source-authenticated physical metering. |
| 9. Multilingual software engineering benchmark designer | `data/discovery`, `data/curated`, `docs/DATASETS.md` | **Pending, high:** 12 GitHub search-language strata are not 12 independently runnable language cohorts; 119 metadata records and 62 source-path leads are not runnable tasks. Need source-era specification, rights and functional oracle. |
| 10. Springer ASE journal senior reviewer | `paper/overleaf/main.tex`, `scripts/audit_manuscript_equations.py`, novelty comparison | **Pending:** 33 equations are inventoried, only seven have limited exact/synthetic cross-checks, and most remain pending derivation. No licensed, independent, safe real-task outcomes: do not claim empirical improvement or statistical risk control. |

## Concrete regressions included in this sprint

1. **Cluster integrity across runs.** For one task, treatment and control
   may agree *within* each seed yet both relabel that task's repository lineage
   for a later seed or model. The previous pairwise consistency check would
   treat the forged lineage as a new independent bootstrap cluster.
   Regression: reject cross-run `task_id→lineage_group` inconsistencies in
   both single-arm and paired evaluation.
2. **One-shot dataset source iterators.** Accept valid generator inputs;
   reject `None`, numbers, malformed identities and path-like source
   names with a deterministic `ValueError`; never silently skip validation.
3. **Nonfinite price mathematics.** With finite
   `gpu_seconds=1e308` and finite `price=1e308`, the product is `inf`.
   Reject the derived nonfinite cost; also reject overflow from summing
   multiple individually finite prices, and from a scalar VOI action penalty.
4. **Microscopic budget fabrication.** An initial
   `gpu_seconds=1e-8` and no receipts may not claim a remaining budget
   `5e-9` without accounting for the gap, even though its absolute
   difference was below `1e-7`. Valid low-magnitude nonzero
   consumption still reconciles.

## Mathematical and implementation boundaries

- Relative ledger float tolerance is a **structural consistency check**,
  not a signed physical-meter attestation or formal proof of hard resource
  enforcement. The sandbox still requires independent external validation.
- The bounds on possible infrastructure outcomes are deterministic
  partial-identification intervals, not sampling confidence intervals.
- Synthetic planning tests and exact finite oracle checks do **not** prove
  model success, real code safety, complete equation correctness or
  calibrated selective-release risk.
- No task, corpus or model weights were downloaded, no hidden evaluator was
  run, no GPU was rented, and no external source-code execution was performed.
- The original MIT license applies only to original U-CODE software; each
  external model, dataset and source repository requires independent review.

## Next research priorities (not completed by this sprint)

**P0:** independently admit first original source-era executable task with
task/commit evidence, file-level code-use rights and oracle provenance;
provide a completely separate sealed evaluator and a rootless, no-network
disposable test runner with externally enforced five hard budgets.

**P1:** run lineage-held-out Monte Carlo calibration falsifiers, especially
miscalibration from correlated tests and missed calibration contexts;
confirm faithful eight-arm policy matching with exact task/model/seed/budget
assignments.

**P2:** validate case-level and cohort-level generalization for at least
two truly runnable programming languages and independent repository
lineages, then expand prospectively. Report failures, abstentions and missing
outcomes without dropping assigned tasks.

**P3:** compile and visually review the official Springer `sn-jnl` template
under a pinned TeX environment, resolve remaining 26 pending independent
equation derivations and verify novelty against faithful search/verification
baselines. No post hoc manuscript claims.

Use `python -m unittest discover -s tests -v`,
`python -m scripts.audit_overleaf_sources`,
`python -m scripts.audit_manuscript_equations`,
`python -m scripts.audit_dataset_cohort_crosswalk`, and
`python -m scripts.check_local_readiness` for offline first-party checks.
