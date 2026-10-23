# U-CODE Issue #1 / G2 — second read-only provenance screening

**Audit date:** 2026-10-24 (China/Singapore local date).  
**Main before new batch:** `58f88ad6a5071bbb4c6f0e84ee667476a0bbe450`.  
**Issue:** https://github.com/Rocky5502/U-CODE/issues/1  
**Scope:** third discovery entry in each of the 12 original GitHub *repository-language search* strata (IDs 3, 13, 23, 33, 43, 53, 63, 73, 83, 93, 103, 113). This is deterministic convenience screening, not probability sampling.

## Evidence and exact execution

Read-only GitHub REST calls inspected each selected public PR's metadata, first page of changed-file metadata, and repository metadata. All 12 PRs had fewer than 100 changed files, so no additional file-list pages were required. For each, the four committed JSONL batches preserve the PR URL, bot-account login, merged flag, immutable base/head/merge SHAs, changed paths, repository SPDX metadata, fork/parent information, path-based production/test separation, changed production languages, and **explicit unverified authorship, rights, and execution fields**.

- [IDs 3/13/23](../../data/audits/2026-10-24/stratified_offset2_ids03_13_23.jsonl) — commit `77233d689fd84e1aa1a908efca889aff97a8e4de`.
- [IDs 33/43/53](../../data/audits/2026-10-24/stratified_offset2_ids33_43_53.jsonl) — commit `859fe3c659359b9b6475012a14cc2c3975c062b0`.
- [IDs 63/73/83](../../data/audits/2026-10-24/stratified_offset2_ids63_73_83.jsonl) — commit `574c8ad27f3f30d6f9e3edcf8f4bdf7581b86ddd`.
- [IDs 93/103/113](../../data/audits/2026-10-24/stratified_offset2_ids93_103_113.jsonl) — commit `a9c1cbb99e7b0c4f6a71af5e4599bb383dfc87d6`.

**Record validation performed:** re-read all four committed JSONL files through the connected GitHub API; parsed exactly 12 distinct records with the intended candidate IDs; checked all 12 have `dataset_eligible=false`, `rights_cleared=false`, and `agent_line_attribution=unverified`. All 12 API retrievals succeeded. This is metadata validation, **not** a new Python unit test or third-party code test.

## This batch: actual counts

| Stage / outcome | Number | Interpretation |
|---|---:|---|
| Selected and successfully resolved PRs | **12 / 12** | No retrieval failures or rate limits observed |
| API author login `Copilot` and merged | **12** | Account-level attribution only |
| PRs with production-source *paths* | **8** | Need substantive patch, authorship and rights review |
| Test-only source changes | **0** | No new test-only stratum |
| Non-source paths only | **4** | Not eligible for production-patch cohort |
| Recognized repository SPDX | **7** | Five MIT, two GPL-3.0; **not** file rights clearance |
| Missing / NOASSERTION repository SPDX | **5** | Rights unresolved |
| Repositories marked as forks | **1** | ID 3; parent `kernitus/beets-oldestdate` |
| Changed production language mismatches | **1** | ID 63: queried C++, changed Python |
| Independently verified agent-authored lines | **0** | PR author != all changed lines AI-generated |
| File-level rights cleared | **0** | No third-party code redistributed |
| Safely runnable independent oracles | **0** | No untrusted code executed |
| Fully eligible research units | **0** | G2 still gated |

**Per-candidate path triage:**  
`3` Python source; `13` JavaScript source; `23` TypeScript source; `33` Java + Dart source; `43` Go source; `53` workflow only; `63` Python source (C++ discovery category); `73` C source; `83` non-source; `93` non-source; `103` non-source; `113` Ruby source (version file; substance unresolved).

**Correct-PR patch spot checks:** read [beets-oldestdate #5](https://github.com/djhibee/beets-oldestdate/pull/5), [presenter #22](https://github.com/coreyboltamn/essentia-patient-journey-language-access-presenter/pull/22), and [eighty-point-huai-an #30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30) to check *code shape*. These include compatibility source/tests, an interactive JS dialog, and Go settlement logic/tests respectively. This is NOT independent agent-line attribution, functional verification, or permission to redistribute. The PR description's own test claims were not reproduced. Note that other PR numbers in those same repositories are **not** the selected samples.

## Cumulative screening state (first 24 + these 12)

| Stage | Cumulative |
|---|---:|
| Discovery pool | **120** distinct repositories / PR links |
| Read-only metadata screened | **36** |
| Unscreened | **84** |
| Merged PR with API author `Copilot` | **36** |
| Production-source-path candidates | **21** |
| Test-only source | **2** |
| Non-source only | **13** |
| Recognized repository SPDX | **19** |
| Missing/NOASSERTION SPDX | **17** |
| Forks | **4** |
| Production language differs from discovery language | **4** |
| Independently AI-line-attributed / rights-cleared / safely runnable / fully eligible | **0** |

Do not generalize 21/36 to the entire discovery pool. The `Copilot` account identity, merge status and path suffixes are preliminary filters. Fork ancestry, source significance, generated/vendor code, per-file license, mixed human edits, security/privacy and independent test oracles remain unresolved.

## Verification and costs

**Latest observed CI for the last data commit:** [offline-tests run 40002837559](https://github.com/Rocky5502/U-CODE/actions/runs/40002837559) at `a9c1cbb99e7b0c4f6a71af5e4599bb383dfc87d6`, completed **success** in Python **3.10 and 3.12**; decoded job logs each report **Ran 46 tests**. These are U-CODE's offline tests, **not** experiments on the third-party PRs. No local unit test was run in this block; no third-party code, paid compute, dataset corpus, model checkpoint or Overleaf project was executed/downloaded/modified.

**Next independent task:** read-only metadata screen the fourth candidate in each of the 12 discovery strata (IDs 4, 14, ..., 114), then prioritize independent patch/rights/manual attribution review of promising source-bearing PRs. Issue #1 remains **IN PROGRESS**; G2 is **GO for read-only metadata only, HOLD for dataset eligibility and code execution**.
