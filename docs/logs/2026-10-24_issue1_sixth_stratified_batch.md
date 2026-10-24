# U-CODE Issue #1 — Sixth stratified PR audit / provenance gate

**Date:** 2026-10-24 (UTC+08). **Stage:** G2 READ-ONLY METADATA SCREENING.  
**Status:** IN PROGRESS. **Issue:** https://github.com/Rocky5502/U-CODE/issues/1  
**Execution roles:** R0 PI, R4 multilingual software engineer, R5 bot-line provenance auditor, R6 rights review, R7 threat auditor, R8 study statistician, R10 replication engineer, R14 skeptical empirical reviewer.

## What was actually executed

Read-only GitHub connector calls inspected each PR's metadata, changed-file paths and repository metadata. Sixth discovery result in each of 12 original **repository-primary-language** search strata, IDs **6, 16, 26, 36, 46, 56, 66, 76, 86, 96, 106, 116**. Made no paid API calls, did not clone/run untrusted repository code, did not download model weights, and did not modify a real Overleaf project.

### Evidence files (immutable GitHub PR SHAs where accessible)

- [IDs 6/16/26](../../data/audits/2026-10-24/stratified_offset5_ids06_16_26.jsonl)
- [IDs 36/46/56](../../data/audits/2026-10-24/stratified_offset5_ids36_46_56.jsonl)
- [IDs 66/76/86](../../data/audits/2026-10-24/stratified_offset5_ids66_76_86.jsonl)
- [IDs 96/106/116](../../data/audits/2026-10-24/stratified_offset5_ids96_106_116.jsonl)

## Honest classification: 12 attempted, 11 retrieved

| Screening disposition | New batch | Cumulative across 72 attempts |
|---|---:|---:|
| Candidate links attempted | **12** | **72** |
| PR metadata successfully retrieved | **11** | **71** |
| GitHub repository/PR unavailable (404) | **1** | **1** |
| Production-source paths | **5** | **33** |
| Test-only source paths | **1** | **6** |
| Non-source changes | **5** | **31** |
| Empty changed-file list requiring investigation | **0** | **1** |
| Recognized repository SPDX metadata (retrieved only) | **4** | **37** |
| Unknown/NOASSERTION SPDX (retrieved only) | **7** | **34** |
| Forks flagged in retrieved PR repos | **2** | **8** |
| Primary-query-language vs changed-source-language mismatch | **0** | **5** |
| Unattempted discovery links | **48** | **48** |
| AI-line-verified / per-file-rights-cleared / independently runnable / study-eligible | **0** | **0** |

**IMPORTANT:** These are *convenience screening counts*, not an unbiased prevalence estimate, a validated research corpus or a correctness result. The 33 production-source-path PRs still contain unknown agent/human/third-party line attribution. A repository-level SPDX result is not per-file redistribution permission.

## Per-candidate screening evidence

| ID | Repository/PR | Metadata outcome | Paths, licensing or concerns |
|---:|---|---|---|
| 6 | [NIKNOLIG-Monorepo #154](https://github.com/nikolausnold/NIKNOLIG-Monorepo/pull/154) | Source paths detected | Kotlin/Python/Swift across 25 changed paths, including tests; rights unknown |
| 16 | [wa-gold-rush #71](https://github.com/JAVA-BT10/wa-gold-rush/pull/71) | Source paths detected | 2 JS production paths + JS test; rights unknown |
| 26 | [RythmnRootsRecords_Suburban-Kid #1](https://github.com/jonfolsetech-ctrl/RythmnRootsRecords_Suburban-Kid/pull/1) | **Retrieval failed** | Both repository and PR API endpoints returned **GitHub 404**; do not infer why |
| 36 | [zia-translation #62](https://github.com/CdC-SI/zia-translation/pull/62) | Source paths detected | 7 Java source + 4 Java tests; repository-level SPDX unavailable |
| 46 | [AKSFlexNode #405](https://github.com/Azure/AKSFlexNode/pull/405) | Non-source | GitHub Actions workflow only |
| 56 | [sccache_automotive #15](https://github.com/Joldiges/sccache_automotive/pull/15) | Non-source | CI/action YAML changes only; forked repository |
| 66 | [onnx-light-ort #38](https://github.com/xadupre/onnx-light-ort/pull/38) | Non-source | Coverage/build/docs/config paths only |
| 76 | [scrcpy #14](https://github.com/Research-Warrant/scrcpy/pull/14) | Non-source | CI release workflow only; forked repository |
| 86 | [fingvibe #33](https://github.com/iricigor/fingvibe/pull/33) | Source paths detected | 6 C# source + 2 tests; license unknown |
| 96 | [Periodic #17](https://github.com/eldon111/Periodic/pull/17) | Source paths detected | 5 Kotlin source + 2 Kotlin tests; license unknown |
| 106 | [projeto-pessoal-cadastro-paciente #4](https://github.com/HmmerHead/projeto-pessoal-cadastro-paciente/pull/4) | Non-source | Dependency/build documentation only |
| 116 | [fromthepage #5947](https://github.com/benwbrum/fromthepage/pull/5947) | Test-only | Ruby spec path; AGPL-3.0 repo metadata |

**Read-only patch inspections:** opened `ConfidenceCalculator.java` from zia-translation, `DailyNotificationWorker.kt` from Periodic, `AppearanceSettingsStore.cs` from fingvibe, and `shared/sharepoint-sync.js` from wa-gold-rush. These patches visibly modify substantive logic (parsing/token patterns, worker scheduling, persisted appearance settings, upload collision/hold logic, respectively), but correctness, source-line authorship, file-level license, security and independent test oracle feasibility **were not established**. Neither passing check badges nor original PR claims were used as a correctness oracle.

## Repair to screening accounting

Prior scripts used `screened=len(records)`, which incorrectly conflated attempted GitHub 404s with successfully retrieved metadata. `scripts/summarize_audit.py` now distinguishes:

- **discovery_links_recorded** (canonical records, including retrieval failures)
- **discovery_links_attempted** (retrieved + failed, not skipped due to rate limit)
- **metadata_retrieved** (actual successful GitHub metadata records)
- **metadata_retrieval_failed** (404/other failures, including rate limit)
- **unattempted_manifest_links**
- **retrieval_failure_candidate_ids**
- **screened** (legacy name: only metadata successfully retrieved)
- **not_screened** (120 - metadata successfully retrieved, includes retriable failures)

`tests/test_screening_summary.py` adds a regression ensuring HTTP 404 is **not** treated as successful screening and license completeness statistics omit missing metadata.

### Reproducible commands

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --manifest data/discovery/agent_pr_candidates_120.csv --output data/derived/screening_summary.json
```

GitHub Actions runs this summary as a separate metadata-only integrity gate. Tests on U-CODE's original Python modules **never** imply tests on these third-party PRs.

## Scientific and operational decisions

**GO:** Continue read-only provenance screening, beginning with seventh-position candidates **IDs 7, 17, 27, ..., 117**; separately retry/locate the 404 if an authorized stable replacement identity appears.  
**HOLD:** Do not label this as 72 verified AI-generated repositories. Do not release third-party source or attempt host execution. The 33 candidate PRs need full patch shape, suspected third-party/human-authored line screening, file rights, safe independent task oracle and reproducibility before any model RQ experiment.  
**Plan:** Given the high number of CI/docs/config-only PRs, the fixed original 120 pool alone may be insufficient for the target **80–120 truly eligible repositories**. Once audit completes, extend discovery with source-bearing PR filters and verify actual changed-file language rather than extrapolating a probability from these convenience-picked links.
