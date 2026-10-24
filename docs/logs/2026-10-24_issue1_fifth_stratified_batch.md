# U-CODE / Issue #1 — Fifth Stratified GitHub PR Audit

**Date:** 2026-10-24 (Asia/Shanghai / Singapore UTC+08).  
**Status:** **G2 IN PROGRESS**, data eligibility **BLOCKED** pending stronger attribution, license and independent test evidence.  
**Roles applied:** R0 Principal Investigator; R4 multilingual SE; R5 provenance forensics; R6 rights/licensing; R7 security; R10 reproducibility; R14 empirical methods.  
**Issue:** https://github.com/Rocky5502/U-CODE/issues/1  
**Source manifest:** data/discovery/agent_pr_candidates_120.csv

## Method and exactly what was done

Performed a read-only Github API screen on **exactly 12 new candidate pull requests**, the fifth candidate within each original repository-primary-language query category: IDs **5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115**.

Collected merged PR status, account login, title, base/head/merge commit SHA, changed file paths, repository SPDX metadata and fork parent where available. Queried PR metadata and all changed filenames through the connected GitHub app, not a local code clone.

All 12 PRs resolved as **merged**, author API login **Copilot**, and had nonmissing base/head/merge SHAs. This is an account-level provenance clue **only**, not proof of attribution for every changed line. No functional tests, model inference, external source execution, licensing clearance, or dataset download was performed.

### Exact audit files

- [IDs 5, 15, 25](../../data/audits/2026-10-24/stratified_offset4_ids05_15_25.jsonl)
- [IDs 35, 45, 55](../../data/audits/2026-10-24/stratified_offset4_ids35_45_55.jsonl)
- [IDs 65, 75, 85](../../data/audits/2026-10-24/stratified_offset4_ids65_75_85.jsonl)
- [IDs 95, 105, 115](../../data/audits/2026-10-24/stratified_offset4_ids95_105_115.jsonl)

Each record contains the candidate ID, discovered-language label, raw path evidence, changed production path languages, actual SHA metadata and explicit false eligibility flags. The audit was run in small groups to avoid API bursts. Read-only file-level patch inspection was limited to a handful of paths.

## New 12-PR batch: observed path screen

| Candidate | Discovery label | PR | Preliminary disposition |
|---|---|---|---|
| 5 NIKNOLIG | Python | [#48](https://github.com/nikolausnold/NIKNOLIG/pull/48) | Non-source |
| 15 roadmap | JavaScript | [#333](https://github.com/pankosmia/roadmap/pull/333) | Non-source |
| 25 landing-clases-de-musica | TypeScript | [#1](https://github.com/ptorterolo/landing-clases-de-musica/pull/1) | Non-source |
| 35 boot-ui | Java | [#1549](https://github.com/jdubois/boot-ui/pull/1549) | Non-source / build configuration |
| 45 zoomies | Go | [#1232](https://github.com/eyupio/zoomies/pull/1232) | Non-source |
| 55 route_manager | Rust | [#56](https://github.com/tun-rs/route_manager/pull/56) | Production Rust source path |
| 65 libxcp | C++ | [#7](https://github.com/songjmcn/libxcp/pull/7) | Non-source |
| 75 MyPi-Hotspot | C | [#23](https://github.com/Bokbacken/MyPi-Hotspot/pull/23) | C/JS application source **plus upstream library** |
| 85 bmi2026lab | C# | [#1](https://github.com/tekwok/bmi2026lab/pull/1) | Non-source, fork |
| 95 Pokemon Explorer | Kotlin | [#3](https://github.com/Sheketli/OPSC6312-Final-POE-Pok-mon-Explorer/pull/3) | Non-source |
| 105 renderbit WordPress | PHP | [#54](https://github.com/renderbit-technologies/renderbit-faq-structured-data-wordpress-plugin/pull/54) | Non-source |
| 115 rolldown-ruby | Ruby | [#20](https://github.com/marcoroth/rolldown-ruby/pull/20) | Test-only Ruby source |

**New batch counts:** 2 source-bearing, 1 test-only, 9 non-source; 7 have recognized repository-level SPDX metadata; 5 missing/NOASSERTION; 1 fork; no new discovery-language/changed-production-language mismatch. 0 eligible experimental units.

### Read-only patch shape checks and important evidence

1. [route_manager #56](https://github.com/tun-rs/route_manager/pull/56) modifies \`src/unix/async_route/tokio.rs\`, replacing the registration of an AsyncFd with an unsafe register call accompanied by a safety explanation. This could be interesting for repair/compilation study but is **not independently verified** and may be narrow.
2. [MyPi-Hotspot #23](https://github.com/Bokbacken/MyPi-Hotspot/pull/23) modifies substantial project application C source in \`main/camera.c\`; partial patch inspection shows an update to ESP PSRAM photo storage logic. The same PR adds bundled files under \`components/quirc/lib/\`; \`quirc.c\` includes an explicit upstream **Daniel Beer copyright/license notice**. Six such library paths are flagged \`suspected_third_party_paths\` for manual source attribution and per-file licensing review. **Do not count these lines as agent-authored** based on PR author.
3. [rolldown-ruby #20](https://github.com/marcoroth/rolldown-ruby/pull/20) changes only test fixture expectations under \`test/\`. It is a candidate for a distinct *AI-modified tests* cohort, not a production-source patch.
4. Do not infer functional correctness, resource safety, or maliciousness from the above partial patches. Code was never executed, dependencies never installed, and hidden tests never run.

**Code change:** \`src/ucode/audit.py\` now exposes \`suspected_third_party_paths\` and \`third_party_attribution_review_required\`, conservatively keyed to the observed bundled quirc subtree. Added \`tests/test_audit.py\` regression for third-party origin warnings and rights gating.

## Cumulative exact metadata screen

| Status | First 48 | New 12 | Total |
|---|---:|---:|---:|
| Screened distinct PR candidates | 48 | 12 | **60** |
| Production-source *path* candidate | 26 | 2 | **28** |
| Test-only source | 4 | 1 | **5** |
| Non-source | 17 | 9 | **26** |
| Empty changed-file list / requires review | 1 | 0 | **1** |
| Recognized repo SPDX identifiers | 26 | 7 | **33** |
| Missing/NOASSERTION repo SPDX | 22 | 5 | **27** |
| Fork repository | 5 | 1 | **6** |
| Discovery-vs-source language mismatches | 5 | 0 | **5** |
| Independently AI-line-verified, file-rights-cleared, safely runnable, eligible | 0 | 0 | **0** |

**Unscreened:** 60 of 120. This is a deterministic convenience sample (first five links per discovery query-language category), not random; percentages are not scientifically valid population estimates.

Even the 28 source-bearing path candidates are **not** a release-ready AI-generated code dataset. Attributable agent lines, human modification, upstream/vendor code, per-file rights, no-PII review, post-merge provenance, build reproducibility and independent tests must all be checked.

## Reproducibility and validation

From a fresh checkout of this repository:

    python -m pip install -e .
    python -m unittest discover -s tests -v
    python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 \
      --manifest data/discovery/agent_pr_candidates_120.csv \
      --output data/derived/screening_summary.json

The aggregator loads canonical stratified JSONL records (skipping preliminary duplicate batches), verifies unique IDs and manifest PR URLs and reports the observed categories. The \`data/derived/\` directory is gitignored by design. Check actual most recent GitHub Actions results before making a test-pass claim; passing internal unit tests cannot demonstrate third-party correctness.

## Next gate and risk priority

1. Continue balanced read-only metadata triage for sixth candidates **IDs 6, 16, 26, ..., 116**; do not relabel links as verified code.
2. Start a separate, documented deeper manual provenance/rights review of the strongest source-bearing PRs. For MyPi-Hotspot explicitly separate third-party \`quirc\` material from project-specific code and check copyright notices for each file.
3. Plan safe, network-disabled, resource-capped independent oracle evaluation only after a rights/experiment approval gate.
4. Keep GitHub Issue #1 **OPEN** and log attrition honestly. No GPU/model or Overleaf manuscript results were generated by this audit.
