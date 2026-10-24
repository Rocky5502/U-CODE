# U-CODE 2026-10-24 continuation — admission, diagnostic calibration and authorship forensics

**User-requested next block**, 2026-10-24. Not background execution.  
**Baseline main SHA:** `443678841e72762e82708036738223054a07c6f1`  
**Latest independently verified CI before this ledger:** [40076482611](https://github.com/Rocky5502/U-CODE/actions/runs/40076482611), **124 tests on both Python 3.10 and Python 3.12**, successful, with `ucode-overleaf-sources` (13,043-byte Actions artifact).  
**Target gates:** G2 provenance; G3/G4 task admission; G7 pre-outcome diagnostic likelihoods; G11 manuscript.

## Executed work and artifacts

1. [src/ucode/diagnostic_fit.py](../../src/ucode/diagnostic_fit.py): training-only smoothed binary action-conditioned diagnostic likelihood, immutable train/validation/eval repository/fork-group contract, pre-oracle evidence order, model/action-specific record checks, fingerprint and typed forecast interface for the five-budget controller. This uses no real task measurements yet.
2. [tests/test_diagnostic_fit.py](../../tests/test_diagnostic_fit.py): 16 offline tests, including an end-to-end test from a frozen **invented synthetic** diagnostic training set into the one-step vector planner. Does not establish model calibration.
3. [src/ucode/task_gate.py](../../src/ucode/task_gate.py): fail-closed metadata contract for source and actual changed language, immutable revisions, evidence refs, rootless/no-network/no-host-mount/resource-constrained sandbox and sealed oracle declarations. A passing result says *declared complete, requires human verification*, never *verified safe*.
4. [tests/test_task_gate.py](../../tests/test_task_gate.py): 13 first-party metadata tests for rights, lineage, source significance, oracle and container constraints. Does not run third-party code.
5. [docs/CALIBRATION_AND_TASK_ADMISSION_PROTOCOL_2026-10-24.md](../CALIBRATION_AND_TASK_ADMISSION_PROTOCOL_2026-10-24.md): sample units, time/fork disjoint split, smoothed conditional likelihood equations, calibration caveats and admission policy.
6. Read-only GitHub investigation of [dependabot-core #16665](https://github.com/dependabot/dependabot-core/pull/16665) and [onnx-light-cpu #1005](https://github.com/xadupre/onnx-light-cpu/pull/1005) to distinguish PR API authorship, actual commit authors, human/agent co-author trailers, real changed production paths and versioned root-license blobs. Immutable evidence in [two-PR case ledger](../../data/audits/2026-10-24/two_pr_commit_and_license_deep_check.jsonl). **No line-level AI ownership or runtime correctness verified.**
7. [tests/test_provenance_cases.py](../../tests/test_provenance_cases.py): 4 fixed offline metadata checks preventing silent promotion into the eligible corpus or dropping mixed-authorship indicators.
8. [paper/overleaf/main.tex](../../paper/overleaf/main.tex): added task-admission rationale, fitting equations, disjoint groups, posterior/oracle limitations and the two observed mixed-attribution cases. No fabricated RQ results. GitHub CI source-only export stays active; no authenticated live Overleaf account was updated.

**Engineering suite:** 91 existing tests + 16 diagnostic-fitting + 13 task-gate + 4 authorship-case tests = **124 tests** (earlier 91-run baseline). Latest CI checked at commit `5aceda789e68e3a2c0aff244ffc8bc12ee372554`.

## Genuine descriptive observation: commit metadata differs from PR attribution

- dependabot-core #16665: GitHub PR author **Copilot**, but all 3 commit author accounts are **human**, each with Copilot co-author trailer; one human approval review, Ruby source and specs, root MIT LICENSE.
- onnx-light-cpu #1005: GitHub PR author **Copilot**, all 3 commit author accounts **Copilot/coding agent**, 2 commits with human co-author trailers; C++ source, benchmark and unit-test paths, root Apache-2.0 LICENSE.
- Root license files and commit metadata are real evidence, but neither establishes rights for every file, a precise AI-authored-line share, causal autonomy, or independent runnable correctness.

**Study admission stays 0** pending human attribution/rights review, approved isolated sandbox, clean before-fix restoration and qualified held-out oracles. The repository's already recorded 84 attempted/83 retrieved discovery screens remain a separate *path-level* cohort and must not be silently equated with executable task count.

## Outstanding blockers and next highest-value task

1. Complete the remaining candidate PR discovery audit while retaining all exclusion reasons, then select a modest licensed source-containing subset with honest attribution scope.
2. On authorized disposable, nonprivileged, network-disabled infrastructure (NOT ordinary CI), reconstruct a pre-fix task and independently check a sealed functional oracle, with hashes and no golden patch exposure.
3. Collect genuine pre-oracle diagnostic traces; fit conditional likelihoods and a **separate** patch-success prior on train lineages only.
4. Pre-register budget-equalized controls including fixed testing, uncertainty-free search, selective verification and full U-CODE. Preserve null effects and coverage/abstention denominators.

**GO:** safe metadata evidence, fail-closed admission design, time/group-checking code and manuscript source consistency.  
**HOLD:** real calibrated AI diagnostic estimates, runnable third-party code, independent oracle validation, claims of new algorithmic effectiveness and journal submission.

No paid service, gated data access, GPU rental or untrusted source code execution was initiated.
