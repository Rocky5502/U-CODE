# U-CODE Research Execution Ledger — Issue #1 / G2

**Date:** 2026-10-24 (Singapore/China time)  
**Lead roles:** R0 Principal Investigator; R5 AI authorship forensics; R6 data-rights audit; R4 multilingual SE; R10 reproducibility; R14 empirical-methodology reviewer  
**Baseline SHA:** `0204ead14f1fde796cfd233849a171ad5742a20f`  
**Issue:** https://github.com/Rocky5502/U-CODE/issues/1  
**Source manifest:** [120 raw discovery candidates](../../data/discovery/agent_pr_candidates_120.csv)  
**API-derived audit records:** [2026-10-24 aggregated JSONL](../../data/audits/2026-10-24/stratified_24_verified_metadata_with_triage.jsonl)

## Actual work performed

Performed read-only GitHub metadata/changed-file screens on exactly **24 distinct PRs**,
the first **two** discovery entries in each of 12 GitHub repository-primary-language
categories, and fetched per-repository SPDX/license/fork metadata. The six
immutable partial API result files are under `data/audits/2026-10-24/batch_01.jsonl`
through `batch_06.jsonl`. Each result records the GitHub PR author, merged
status, source repository, PR URL, full changed-file path list, base/head/merge
SHAs, detected repository SPDX and fork metadata.

Four illustrative production patches were opened for *code-shape* review:
[Trading-Web #468](https://github.com/DSTech-876/Trading-Web/pull/468),
[Cindy #2](https://github.com/ijug-ev/cindy/pull/2),
[AIESEC #4](https://github.com/ghaith-ben-amor/aiesec/pull/4),
[dependabot-core #16665](https://github.com/dependabot/dependabot-core/pull/16665).
Reading a patch is **not** independent proof of AI ownership, license clearance
or functional correctness.

## Observed 24-PR metadata flow

| Sequential filter | Observed count | Meaning |
|---|---:|---|
| 120 candidate links in original manifest | 120 | Discovery pool, **not** analyzed exhaustively |
| Stratifed sample from original links | 24 | 2 per GitHub query language, first in search order |
| GitHub PR metadata/paths reachable | 24 | No retrieval errors in this batch |
| Merged with API author `Copilot` | 24 | Author identity is a PR/account signal, not line-level authorship |
| PR with at least one production-source path | **13** | Potential sample pending attribution and execution |
| Changed source confined to test files | **2** | Exclude from production-code stratum; may form a test-writing cohort |
| No conventional executable source changes | **9** | Documentation/CI/build/resources/metadata only |
| Repository has recognized SPDX metadata | **12** | This does NOT establish file-level rights |
| Repository SPDX missing or NOASSERTION | **12** | Rights unclear; null/NOASSERTION not assumed permissive |
| Repositories flagged as forks | **3** | Fork lineage and parent licensing need special review |
| Production-code PRs with different changed language from discovery label | **3** | Strong warning against using GitHub primary language |
| Source/AI-line provenance independently verified | **0** | Need human/trace attribution checks |
| File-level redistribution rights cleared | **0** | Never assume rights solely from SPDX |
| Isolated build/test oracle verified | **0** | No third-party code executed |
| Fully eligible research samples | **0** | Gate remains open |

### False language labels demonstrated

- [NIKNOLIG-iOS- #14](https://github.com/nikolausnold/NIKNOLIG-iOS-/pull/14): GitHub discovery category `Python`; changed executable language `Swift`.
- [meridian #939](https://github.com/Achi1984/meridian/pull/939): discovery category `JavaScript`; production changes in `Python` (JavaScript changed only in tests).
- [aiesec #4](https://github.com/ghaith-ben-amor/aiesec/pull/4): discovery category `PHP`; production change in `TypeScript`.
- [muse-gadget-sdk #4](https://github.com/rongxike/muse-gadget-sdk/pull/4): changed source spans `C` and `C#`, despite GitHub category `C`.

### Exclusion examples

- Docs only: `github/gh-aw #71451`, `djezzzl/database_consistency #332`.
- CI/workflow only: `Quantinuum/zixy #270`, `kankangain/figcraft #1`, `gb-web-de/editorial-flow #19`.
- Config/build/resources: `megseymour79/shiftedtones #31`,
  `Azure/AgentBaker #9884`, `jddcef/scantailor-advanced #6`,
  `Adv-Nishant/CNAP-Capture- #3`.
- Test-only: `coryelliott2016-eng/harboriq #152`,
  `teggr/awesome-java-ui #98`.

### Scientific limitations

This is a **deterministic convenience/stratified screening sample**, NOT a
probability sample. The ratio 13/24 must **not** be generalized into a
population prevalence estimate for all 120. No prompt/agent trace was reviewed
to prove line authorship. An SDK/Rust/C++ code repository might contain a
Copilot PR affecting only YAML or prose; such PRs cannot be silently retained
in production code strata.

`SPDX` summarizes repository metadata only; `null` or `NOASSERTION`
must be treated as unknown, not as an open-source license grant.
Every retained source file still requires licensing review, independent
authorship provenance and a safe runnable oracle. An open-source model
checkpoint has not been run; there are no uncertainty, calibration or
search-efficiency results in this block.

## Changes to audit methodology

The read-only auditor now explicitly separates production-source paths,
test-only source paths and non-source changes. It assigns language from each
**changed file**, records fork/parent metadata when supplied, and always
requires independent file-level license assessment. Regression tests were added.
Latest CI result and commit must be checked before this record is called green.

## Issue #1 status: IN PROGRESS, not completed

**G2 discovery audit progress: 24/120 PR metadata checks.**  
**Rights and runnable sample acceptance: 0**, as no file-level rights or
independent execution gates are satisfied. No 2–5 GB corpus has been downloaded.

### Next unblocked research task

Continue read-only triage in a *second balanced batch* of candidate IDs 3–4,
13–14, ... 113–114 (24 new PRs), or manually resolve licenses and fork
lineage for selected production-source candidates with recognized SPDX
metadata. The better immediate evidence-per-effort priority is to manually
verify line provenance and test feasibility of `dependabot/dependabot-core #16665`
and `xadupre/onnx-light-cpu #1005` without executing third-party code.

### Parallel manuscript status

`paper/overleaf/main.tex`, `references.bib` and `README.md` remain
versioned in the repository. Springer `sn-jnl` skeleton exists but requires
the official class files and an actual Overleaf account/project before a
compiler-based Overleaf verification. The Results section remains empty.

**Final go/no-go:** GO for further read-only auditing and safe method tests;
HOLD for declaring dataset eligibility, GPU experiments or journal results.
