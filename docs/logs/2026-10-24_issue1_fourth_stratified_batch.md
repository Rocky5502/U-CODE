# U-CODE Issue #1 / G2 — fourth-candidate stratified metadata audit

**Date:** 2026-10-24 (Asia/Singapore). **Status:** IN PROGRESS.  
**Research roles:** R0 PI, R5 authorship forensics, R4 multilingual SE, R6 rights, R10 reproducibility, R14 empirical reviewer.  
**Issue:** https://github.com/Rocky5502/U-CODE/issues/1  
**Source:** data/discovery/agent_pr_candidates_120.csv

## Actual scope and evidence

Read-only screened exactly the **fourth discovery entry in each of 12 GitHub repository-primary-language search categories**: IDs **4, 14, 24, 34, 44, 54, 64, 74, 84, 94, 104, 114**. For each, inspected PR title/author/merge state, base/head/merge SHAs, all changed-file paths and repo SPDX/fork metadata, using the connected GitHub API. Four committed JSONL files preserve the returned identifiers and paths without redistributing external code:

- [IDs 4/14/24](../../data/audits/2026-10-24/stratified_offset3_ids04_14_24.jsonl)
- [IDs 34/44/54](../../data/audits/2026-10-24/stratified_offset3_ids34_44_54.jsonl)
- [IDs 64/74/84](../../data/audits/2026-10-24/stratified_offset3_ids64_74_84.jsonl)
- [IDs 94/104/114](../../data/audits/2026-10-24/stratified_offset3_ids94_104_114.jsonl)

All **12/12** were reachable and merged, with API author login **Copilot** and recorded nonmissing base/head/merge SHAs. No retrieval errors were observed. The audit did **not** verify individual AI-authored lines, file-level licenses or functional correctness.

## Batch outcomes (12)

| Path-screening class | Count | Candidate IDs |
|---|---:|---|
| Production-source path detected | **5** | 14, 24, 64, 104, 114 |
| Test-only source changes | **2** | 44, 84 |
| Non-source changes | **4** | 34, 54, 74, 94 |
| Empty changed-file list requiring review | **1** | 4 |
| Recognized repository SPDX | **7** | 4, 14, 34, 44, 54, 104, 114 |
| Missing/NOASSERTION SPDX | **5** | 24, 64, 74, 84, 94 |
| Fork | **1** | 24 |
| Query language vs changed production language mismatch | **1** | 14, JavaScript discovery / Python source |
| Independently verified AI lines, file rights, oracles, eligible units | **0** | All remain unverified |

**Corrected false-positive:** [monexi #1](https://github.com/ribollitiago/monexi/pull/1) changes the Kotlin Gradle build configuration file at app/build.gradle.kts, which should **not** count as application-source code. The classifier now excludes *.gradle.kts with regression tests. [Raks- #3](https://github.com/DicedPingu/Raks-/pull/3) was merged but returned zero changed-file paths and zero changed_files. Its record is now explicitly empty_file_list_needs_review rather than unsupported non-source classification.

### Read-only source-patch shape checks

No third-party build, model inference, agent traceback attribution, or test execution was attempted:

1. [php-spider #172](https://github.com/mvdbos/php-spider/pull/172): Cache prefetch source now uses FilePersistenceLayout::getResourceFilePath for path construction; source and PHPUnit test paths exist. Correctness and authorship unverified.
2. [forem #24047](https://github.com/forem/forem/pull/24047): Ruby role controller introduces a Community Leader Level 1 role-presence helper, with related source and spec paths. Repo metadata reports AGPL-3.0; this is not file-level redistribution clearance.
3. [onnx-light-viewer #120](https://github.com/xadupre/onnx-light-viewer/pull/120): Python example generator changes ONNX helper import calls, despite JavaScript discovery label. Example code is not necessarily runtime production code, so substantive eligibility review remains pending.

## Cumulative 48/120 metadata-screening flow

| Stage | Total |
|---|---:|
| Discovery candidate links | 120 |
| Metadata screened | **48** |
| Not yet screened | **72** |
| Source-bearing production-path candidates | **26** |
| Test-only source changes | **4** |
| Non-source changes | **17** |
| Empty file list / unresolved | **1** |
| Recognized repo SPDX | **26** |
| Missing / NOASSERTION repo SPDX | **22** |
| Repositories marked forks | **5** |
| Source-vs-discovery-language mismatches | **5** |
| AI-line verified / rights cleared / independently runnable / eligible | **0 / 0 / 0 / 0** |

These are deterministic convenience-screened repository PR links, **not** an unbiased population sample, validated corpus, model accuracy metric or scientific outcome. Repository SPDX and a merged Copilot PR do not prove per-file rights or AI ownership.

## Reproducibility

- Auditing logic fixed in src/ucode/audit.py with tests/test_audit.py regression tests for build-script and zero-file PR cases.
- A fail-closed reproducible aggregator in scripts/summarize_audit.py reads the canonical stratified JSONL files, rejects duplicate IDs, verifies manifest repository/PR links, excludes overlapping preliminary partial batches and reports exact counts without claiming eligibility.
- Matching tests in tests/test_screening_summary.py.

Suggested fresh checkout commands:

    python -m pip install -e .
    python -m unittest discover -s tests -v
    python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --manifest data/discovery/agent_pr_candidates_120.csv --output data/derived/screening_summary.json

Output under data/derived is gitignored. Check the newest GitHub Actions result for the exact test count; our internal unit tests do not validate external PR functionality.

## Gate and next step

**G2 GO for metadata screening only; HOLD for empirical corpus inclusion and execution.** Screen fifth candidate in each stratum next, IDs **5, 15, 25, ..., 115**. Then prioritize human trace attribution, per-file rights and independent executable oracle feasibility on promising genuine production changes. Do not download gated/paid models, run unsafe code or claim the target sample counts have been achieved.
