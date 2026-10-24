# U-CODE execution checkpoint · 2026-10-24 SGT

## Verified GitHub starting point

- Repository: https://github.com/Rocky5502/U-CODE
- Dated master prompt:
  docs/UCODE_MASTER_SUPERPROMPT_2026-10-24.md
- Snapshot before this checkpoint: master research framework committed,
  120 discovery candidates, 10 source leads, four limited PR metadata triages.
- Most recently checked prior GitHub Actions result: 40 offline Python tests
  passing across Python 3.10 and 3.12.
- This planning update does NOT make the 120 candidate PRs verified, grant
  external data rights, launch hosted GPU jobs, or create a real Overleaf project.

## Additional verified 2026-10-24 session

- Issue #1 read-only Github audit progressed to **24/120 metadata screens**, two
  PRs from each of 12 original GitHub query-language discovery groups.
- Source-path triage: **13 production-source candidates**, **2 test-only**,
  **9 non-source**. These are NOT verified AI-line attribution or runnable tasks.
- Repository SPDX metadata: 12 recognized license identifiers, 12 missing or
  NOASSERTION; 3 forks. All file-level rights remain pending.
- Three PRs had production-code languages different from the discovery label.
- Full exact base/head/merge SHA snapshots and paths:
  data/audits/2026-10-24/stratified_24_verified_metadata_with_triage.jsonl
- Dated human-readable evidence:
  docs/logs/2026-10-24_issue1_stratified_pr_audit.md
- Source auditor fixed to classify production/test/config, detect changed-file
  languages, preserve fork metadata, require rights review, support deterministic
  strata and halt on HTTP 403/429.
- Overleaf sources remain tracked under paper/overleaf/; no authenticated
  Overleaf project edits have been performed. No GPU trials executed.
- CI must be rechecked for the very latest main commit before reporting tests.

## Resumption protocol

1. Read main SHA and Issues 1--6 (never assume frozen file is the latest).
2. Verify newest GitHub Actions result, exact test count and outstanding issues.
3. Pick issue #1 / G2, the 12--24 read-only GitHub PR audit pilot, as the
   first high-value unblocked task.
4. Log reachable/merged/source-bearing and manual-review statuses; inspect
   agent author alias. Never infer AI line ownership without evidence.
5. Protect research integrity, avoid GitHub API secondary-rate-limit bursts.
6. Check tests, commit dated evidence to docs/logs and update issue.
7. Record next actionable task, user approval needed, and go/no-go.

## Session ledger template

- Started (timezone):
- Main SHA before/after:
- Issue and gate:
- Chosen role/owner:
- Changes (file paths and evidence):
- Tests (local/CI, counts, URL):
- Provenance and data counts:
- Model runs and measured results (NONE when absent):
- Cost and rights approvals:
- Risks / exclusions / blockers:
- Next unblocked task:
- Stop/go:

**A 30-minute work block is a planning cycle, not independent ongoing
background work. Reminders only happen if a supported automation is created.**

## Follow-up 12-PR audit — 2026-10-24

- Another **12 distinct PRs** (third candidate in each discovery-language
  group; IDs 3, 13, ..., 113) were read-only screened and committed in four
  JSONL batches under `data/audits/2026-10-24/`.
- New batch: 12/12 reachable, merged with API login `Copilot`;
  **8 production-source-path**, **0 test-only**, **4 non-source**.
  Seven had recognized repository SPDX metadata; one was a fork; one
  had a changed-production-language mismatch. No rate-limit failures.
- Cumulative: **36/120 metadata-screened**, **21 production-source-path**,
  **2 test-only**, **13 non-source**, **19 recognized repository SPDX**,
  **4 forks**, **4 language mismatches**.
- **0** independently attributed AI-line patches, **0** file-rights-cleared,
  **0** independent safely runnable oracles and **0** eligible study units.
- [Detailed follow-up ledger](logs/2026-10-24_issue1_second_stratified_batch.md)
  records immutable SHAs, per-PR URLs, evidence, limits and CI.
- Last CI observed after the four new data commits:
  [run 40002837559](https://github.com/Rocky5502/U-CODE/actions/runs/40002837559)
  passed **46 offline tests** on each of Python 3.10 and 3.12.
  Recheck CI for any newer documentation commit before calling the newest head green.
- Next read-only stratum: fourth entry in each discovery-language group
  (IDs 4, 14, ..., 114). Issue #1 stays open; no external code execution.


## Fourth-stratum resumption update — 2026-10-24

- Continued Issue #1: screened 12 additional actual PRs, one fourth-position
  candidate in each of 12 discovery-language groups (IDs 4, 14, ..., 114).
- **Cumulative 48/120 metadata-screened**. Categories: **26 production source
  paths**, **4 test-only source**, **17 non-source**, **1 empty-file-list needs
  review**. **72 candidates remain**.
- 26 recognized repository SPDX tags, 22 unknown/NOASSERTION; five forks and
  five source-language/primary-language mismatches. None is rights-cleared,
  independently AI-line-attributed, runnable with an independent oracle, or
  approved as an experimental dataset unit.
- Fixed false positive: app/build.gradle.kts must not be treated as Kotlin
  application source. PR #3 of DicedPingu/Raks- reports zero changed paths
  and requires review, not automatic config-only classification.
- Performed limited read-only single-file diff shape checks of php-spider #172
  (PHP), forem #24047 (Ruby), and onnx-light-viewer #120 (Python example).
  No external code executed; no model trials.
- Full log: docs/logs/2026-10-24_issue1_fourth_stratified_batch.md
- Four stratified JSONL files:
  data/audits/2026-10-24/stratified_offset3_ids*.jsonl
- Reproducible, fail-closed rollup:
  python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24
- New tests in tests/test_screening_summary.py and tests/test_audit.py;
  check latest GitHub Actions before reporting final test count.
- Next: screen 12 fifth-position candidates IDs 5, 15, ..., 115, then
  manually inspect trace provenance, file-level licenses and executable oracle
  feasibility for actual source-bearing candidates. Keep Issue #1 OPEN.


## Fifth-stratum continuation checkpoint — 2026-10-24

**GitHub Issue #1 G2:** 12 fifth-position PRs read-only screened (IDs 5, 15, ..., 115). All 12 returned merged with API account "Copilot" and base/head/merge commit SHAs. Canonical snapshots:
data/audits/2026-10-24/stratified_offset4_ids*.jsonl.

**New 12:** 2 production-source-path PRs, 1 test-only, 9 non-source, 7 recognized repo SPDX, 1 fork. No retrieval failures.

**Cumulative:** **60/120** screened, **60 remain**; **28** production-source-path candidates, **5** test-only, **26** non-source, **1** unresolved empty file list; **33** recognized repo SPDX and **27** missing/NOASSERTION, **6** forks, **5** discovery-vs-actual-source language mismatches. **0** AI-line-verified, rights-cleared, independently runnable, fully eligible units.

**Critical research-integrity finding:** Bokbacken/MyPi-Hotspot PR #23 includes six bundled quirc QR-library files; read-only patch inspection of quirc.c found upstream Daniel Beer copyright/license text. These files are marked suspected third-party to avoid falsely counting as AI-generated patch lines. Read-only patch-shape inspections also covered Rust route_manager PR #56 and Ruby test-only rolldown-ruby PR #20. No external code executed.

**Engineering:** Added suspected-third-party audit fields and regression test in src/ucode/audit.py and tests/test_audit.py; added GitHub Actions step invoking scripts/summarize_audit.py as a manifest/duplicate/PR consistency gate. Full issue ledger:
docs/logs/2026-10-24_issue1_fifth_stratified_batch.md. The summary tool's output is generated dynamically; historical GitHub Actions test counts must not be mistaken for external test results.

**Next:** balanced read-only sixth-position PR screen (IDs 6, 16, ..., 116); continue human/trace authorship provenance, file-level rights and independent oracle review. Keep issue #1 OPEN. This block did not run GPU models, download 2–5 GB of sources, validate any empirical correctness metrics or edit an authenticated Overleaf project.

## Sixth-stratum continuation — 2026-10-24 UTC+08

- **72/120 discovery links attempted; 71 PR metadata records verified; 1 GitHub 404** (candidate 26). **48 links unattempted**.
- Cumulative successfully retrieved PRs: **33 source-bearing production-path**, **6 test-only**, **31 non-source**, **1 empty-file-list unresolved**. Recognized repository-level SPDX: **37**, unknown/NOASSERTION: **34**. **8 forks**; **5 production-language mismatches**.
- **0 independently verified AI-authored-line sets, file-level license clearances, reproducible independent software oracles, or approved experimental samples**.
- Sixth cohort canonical files: data/audits/2026-10-24/stratified_offset5_ids*.jsonl; report: docs/logs/2026-10-24_issue1_sixth_stratified_batch.md.
- Confirmed GitHub 404 separately at the candidate 26 repository and PR API URLs, without inferring deletion/private status.
- Read-only spot checks inspected Java ConfidenceCalculator, Kotlin daily scheduling worker, C# appearance settings store and JavaScript SharePoint conflict control patches. All correctness, code authorship and rights remain unverified.
- Repaired scripts/summarize_audit.py so discovery links **attempted** are distinct from metadata **successfully retrieved**; tests/test_screening_summary.py guards against inflating screening counts on 404.
- **Next:** read-only seventh-position candidates IDs 7,17,...,117; prioritize vetted open-source patches for actual independent build/test feasibility. Confirm latest CI for active main SHA.
