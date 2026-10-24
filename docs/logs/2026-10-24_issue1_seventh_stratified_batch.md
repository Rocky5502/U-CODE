# U-CODE — Seventh-Stratum Provenance Audit (Issue #1, G2)

**Audit date:** 2026-10-24 (UTC+08). **Status:** Issue #1 remains **IN PROGRESS**.  
**Source:** [120-candidate discovery manifest](../../data/discovery/agent_pr_candidates_120.csv)  
**Responsible research roles:** R0 PI; R4 multilingual code triage; R5 authorship/provenance; R6 licensing; R7 software security; R10 reproducibility; R14 adversarial empirical reviewer.

## Scope / actual execution

Read-only inspected **12 newly discovered GitHub PR candidates**, the seventh link in each of 12 *repository-primary-language* discovery strata: IDs **7, 17, 27, 37, 47, 57, 67, 77, 87, 97, 107, 117**. For each, inspected PR metadata, changed-file filenames and repository metadata through GitHub's connected API; obtained author login, merged state, immutable base/head/merge SHAs, actual changed paths, repository SPDX marker, fork/parent information.

**All 12 PRs were reachable, merged and reported API author `Copilot`.** This only establishes a PR account signal, not reliable authorship of every changed line or actual patch correctness. No third-party source was run, compiled, cloned or copied into this repository.

### Immutable metadata records

- [7/17/27](../../data/audits/2026-10-24/stratified_offset6_ids07_17_27.jsonl)
- [37/47/57](../../data/audits/2026-10-24/stratified_offset6_ids37_47_57.jsonl)
- [67/77/87](../../data/audits/2026-10-24/stratified_offset6_ids67_77_87.jsonl)
- [97/107/117](../../data/audits/2026-10-24/stratified_offset6_ids97_107_117.jsonl)
- [Next human-evidence review queue](../../data/audits/2026-10-24/seventh_batch_manual_review_queue.csv) — prioritized *leads only*.

## Seventh-batch results (12)

| Class | Observed | IDs |
|---|---:|---|
| Production-source `paths` detected | **6** | 7, 67, 77, 87, 107, 117 |
| Test-only source paths | **2** | 27, 47 |
| CI/docs/config/no eligible source | **4** | 17, 37, 57, 97 |
| GitHub 404 or other retrieval errors | **0** | None |
| Recognized repository-level SPDX metadata | **6** | 7, 17, 47, 57, 77, 117 |
| Unknown/NOASSERTION repo SPDX | **6** | Remaining |
| Forks | **1** | 37 |
| Source-language differs from discovery label | **1** | 67: C++ query, Python distribution script |
| Independently AI-line verified, rights-cleared, runnable or eligible | **0** | No final acceptance gate passed |

### Materially important discovery: bulk .NET artifacts

[RodriguesCesar/Ats #5](https://github.com/RodriguesCesar/Ats/pull/5) changed **1,538 GitHub file paths** in a PR titled *Standardize project directories and remove tracked build artifacts*. Among them **1,339 paths were under `obj/`, `bin/`, or `.vs/`** and must not be counted as novel C# software written by an AI agent. The original naive path classifier had misleadingly included 124 C# production source paths. After fixing `src/ucode/audit.py` to exclude known build and IDE directory artifacts and recomputing from the immutable changed filename list, **97 remaining C# production-source paths and 35 test paths** remain, with `bulk_reorganization_or_generated_artifact_risk=true`. Some or many of these may be *moved pre-existing code*. No new AI-generated-line claim can be made without examining rename status, patch diffs and contributor/agent traces.

This finding justifies treating *production source path present* as a **very weak inclusion signal**. PR author identity plus source file extension is not line-level provenance.

### Read-only source-patch shape checks — never correctness experiments

Five single-file patches were opened without running them:

- [framecover #5](https://github.com/fgagarin/framecover/pull/5), `src/framecover/core/update_checker.py`: changes HTTPS certificate-store/TLS update logic; Python source and test paths exist; MIT repository-level metadata. Candidate for separate provenance and sandbox feasibility assessment.
- [Z3 #11287](https://github.com/Z3Prover/z3/pull/11287), `scripts/mk_unix_dist.py`: adds distribution static-library build helper, not necessarily application-runtime logic; discovery label was C++. Repo SPDX metadata is NOASSERTION. Consider a *tooling* cohort rather than ordinary generated application code.
- [botnav #190](https://github.com/chompehh/botnav/pull/190), `codemp/game/ai_main.c`: modifies game-agent combat tuning logic; C source and test path(s); GPL-2.0 repo metadata.
- [we-have-oidc-at-home #1](https://github.com/unhookd/we-have-oidc-at-home/pull/1), `saml.rb`: introduces substantial SAML authentication logic with a test path. MIT repository metadata but **security-sensitive**, requiring careful adversarial review and constrained execution before inclusion.
- [extracted #137](https://github.com/ticketsupport-spec/extracted/pull/137), `membership-manager-qr/includes/shortcodes.php`: changed inline **JavaScript** event/picker logic inside a `.php` file. Path-based language attribution alone is not enough for line-language analysis; license metadata missing.

None of these reviews established API/test correctness, AI lineage, rights, or an independently sealed oracle. The original PR's own self-reported checks are not independent verification.

## Cumulative screening after this batch

| Stage | Total |
|---|---:|
| Original discovery pool | 120 |
| GitHub links attempted | **84** |
| Successfully fetched PR metadata | **83** |
| Retrieval failure (previous TypeScript repo returned GitHub 404) | **1** |
| Unattempted links | **36** |
| Production-source-path candidates | **39** |
| Test-only source | **8** |
| Non-source changes | **35** |
| Empty changed-file list needs review | **1** |
| Recognized repo SPDX (among retrieved only) | **43** |
| Unknown/NOASSERTION repo SPDX (among retrieved only) | **40** |
| Forks among retrieved | **9** |
| Changed-production-language vs discovery label mismatches | **6** |
| Independently AI-line-attributed, file-level rights-cleared, safely runnable, fully eligible | **0** |

**Methodological caution:** These are deterministically selected first-seven results per GitHub query-language stratum, a convenience screening set. These are not random samples of agent outputs and do not support population-prevalence or model-reliability claims. The target of 80–120 truly eligible repositories cannot be inferred from 39 path-only candidates.

## Code, tests and reproducibility

1. Fixed `src/ucode/audit.py` to exclude standard .NET generated outputs (`obj/`, `bin/`) and tracked IDE caches (`.vs/`, `.idea/`, `.gradle/`) before source counting.
2. Added two regression tests to `tests/test_audit.py` verifying these generated paths are ignored while real `backend/src/Api/Program.cs` remains source.
3. Recomputed **candidate 87** in the canonical seventh-batch JSONL, preserved all original changed paths and immutable PR SHAs, and explicitly recorded bulk-reorganization risk.
4. Created a 6-row human validation queue, including copyright/license, embedded-language, manual code attribution, build-versus-runtime and independent oracle acceptance checkpoints.

Run locally from project root (no third-party code execution):

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m scripts.summarize_audit \
  --audit-dir data/audits/2026-10-24 \
  --manifest data/discovery/agent_pr_candidates_120.csv \
  --output data/derived/screening_summary.json
```

GitHub Actions executes the same original-project tests and metadata-summary validation on Python 3.10 and 3.12; the latest main run must pass before declaring the checkpoint green. These are **not external PR functional tests**.

## Next independent research decisions

- **GO:** Eighth candidate in each original discovery stratum: IDs **8, 18, 28, ..., 118**, using API-efficient metadata-only triage.
- **HIGH PRIORITY:** Review actual human/agent code lineage, per-file rights and oracle feasibility for shortlisted framecover, botnav, SAML Ruby, and similar source-bearing PRs.
- **HOLD:** The massive .NET code move should not be enrolled as an AI-generation example without rename analysis. Do not publish unlicensed third-party code, run untrusted source in normal CI, rent GPU or claim experimental improvements from metadata screening.
- Keep [Issue #1](https://github.com/Rocky5502/U-CODE/issues/1) **OPEN**, and preserve all negative/ambiguous results.

**Next scientific gate:** verify whether genuinely independent and safely runnable source changes can be retained, *not merely* whether another PR can be read.
