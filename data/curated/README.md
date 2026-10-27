# U-CODE compact, auditable 120-repository discovery dataset

**Version:** 2026-10-27. **Stage:** PR-metadata cleaning, **NOT an executable
benchmark**. **No AI model, third-party source, evaluation test or hidden
oracle was run** to generate these metadata files.

## What is included in GitHub

- [discovery_frame_120_NOT_EXECUTABLE.csv](2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv):
  frozen clean, minimal frame of **120 distinct repository names** and
  one PR per repository, with original query-language stratum,
  0 admitted tasks and no automatic train/test split.
- Original [120-candidate discovery CSV](../discovery/agent_pr_candidates_120.csv).
- [Canonical 120-item read-only metadata audit](../audits/2026-10-24/):
  immutable pre-fix/head/merge Git commit references and changed-file metadata
  where retrievable. Source-path classification is **not executable rights**.
- [Dataset cleaning implementation](../../src/ucode/dataset_curation.py)
  and [rebuild entrypoint](../../scripts/build_clean_pr_dataset.py).

The original GitHub candidate manifest is **12 search-language strata,
ten links each**, for Python, JavaScript, TypeScript, Java, Go, Rust,
C++, C, C#, Kotlin, PHP and Ruby. They are **search-language strata,
not necessarily languages actually modified by the PR**. Some PRs
are empty, configuration-only, test-only, IDE/build output or language
mismatches. For example, a Python-search result can actually change
Swift. No false language agreement is imputed.

## Derived curated dataset (four compact artifacts)

Run from checked-out repository root:

    python -m scripts.build_clean_pr_dataset --output-dir dist/datasets/ucode_pr_metadata_v1

The standard-library-only offline pipeline reads **all 120** canonical
IDs exactly once (including retrieval failure), fails closed on
duplicate/mismatched PR identities, tampered Git SHA, unknown
triage class, false task admission, fake independent oracle and source
rights promotion. It outputs:

1. **clean_metadata_120.csv:** one row per discovery PR, separately
   recording search and observed changed-production-path languages,
   counts of changed source/test paths, immutable commit IDs, conservative
   fork-group hint, review priority, explicit pending rights/oracle/sandbox,
   and no frozen leakage-safe train/test split.
2. **language_strata.csv:** actual discovered, retrieved, source-path,
   first-pass metadata and mismatch counts for each of 12 search strata.
   A candidate with a different production language remains in its
   original discovery stratum; it is not silently reassigned.
3. **manual_review_12_NOT_EXECUTABLE.csv:** a deterministic
   diversity-first shortlist of **at most 12** production-path metadata
   leads. It prioritizes source+test paths, known repository SPDX
   metadata, no obvious generated/IDE/build/sensitive code hints, and
   breadth over the existing 12 strata. This is **not** a 12-task
   executable or statistically representative sample.
4. **cleaning_report.json:** counts, transformed language evidence,
   reproducible original CSV SHA256, zero executable admissions,
   and a full attrition report.

Github CI exports those files as artifact
**ucode-pr-metadata-clean-v1**, separately from the manuscript ZIP.
All are tabular metadata, no downloaded repository code, binary,
dependencies, container images, model weights or hidden tests. That is
why the cleaned data is in kilobytes rather than many gigabytes.
Do not bundle unreviewed patches, source trees or executables into
a supposedly redistribution-cleared benchmark.

## Additional technical quality audit and release receipts

The stricter [offline quality audit](../../scripts/audit_dataset_quality.py)
is the **preferred release command**:

    python -m scripts.audit_dataset_quality \
      --output-dir dist/datasets/ucode_pr_metadata_v1

It produces the four cleaning files above **plus four quality and
reproducibility outputs** (eight total):

- \`dataset_schema.json\`: machine-readable column types, unit of
  analysis, required fields and the meaning of changed-file versus
  GitHub search language.
- \`quality_report.json\`: exact raw-to-clean join coverage, primary
  key uniqueness, original 12-stratum preservation, field-level
  missingness, candidate owner/fork/shared-commit collision **flags**,
  and explicit blocked downstream split/task-readiness checks.
- \`manual_lineage_and_rights_flags.json\`: per-PR metadata-only
  manual review reasons; **no certification** that any PR is
  AI-authored, rights-cleared or executable. There are 107
  records with one or more additional screening flags in the
  tested 2026-10-27 snapshot; **all 120** still need independent
  file-rights/oracle and task qualification.
- \`release_integrity.json\`: SHA256 and byte count for each of
  the preceding seven files and digest of each canonical
  *input* audit/manifest file, with repository-relative
  paths independent of the machine used to produce the release.

Exact commit SHA consistency with the original PR audit is checked:
an attacker cannot alter a 40-character SHA in the cleaned table and
have it pass merely because it is syntactically valid. All seven
output hashes can be verified after artifact extraction.
A matching SHA256 is **integrity of these files**, not a
cryptographic proof of legitimate GitHub authorship, source code
permission, independent held-out test quality or reproducible builds.

The accompanying [Scientific Data readiness assessment](../../docs/SCIENTIFIC_DATA_READINESS_2026-10-27.md)
distinguishes a small reusable PR **metadata** snapshot from
a fully curated multilingual executable software repair dataset.
The latter needs independent annotation and task re-execution,
lineage-safe splits, license review, and an archived DOI release.

## Companion metadata-only lineage review graph

Reproduce the conservative [lineage graph](../../src/ucode/lineage_risk_graph.py)
using:

```bash
python -m scripts.audit_lineage_risks --output-dir dist/ucode-lineage-review
python -m scripts.verify_lineage_review dist/ucode-lineage-review
```

It generates a **separate** four-file reviewer-warning artifact, not
an extension of the eight-file cleaned dataset. The fixed source
snapshot produces 120 provisional single-record ancestry
components and nine owner-only warning links, with no
matching cross-record fork-parent/commit SHA links.
Cross-role matches (one PR head equals another PR base)
are explicitly supported by the algorithm.
These findings are NOT evidence of source-content
uniqueness or a leakage-free train/test split.
All split and runnable-task approval flags remain blocked.
See the [formal review ledger](../../docs/PR_LINEAGE_REVIEW_2026-10-27.md).

## What the pipeline CANNOT claim

1. Bot-authored/merged PR metadata is not evidence of line-level AI
   authorship or a valid pre-existing engineering specification.
2. Repository-level SPDX metadata does not grant permission to republish
   particular files; review license texts and attribution per task.
3. A changed test file is not a held-out independent correctness oracle.
4. Root repository aliases, forks, vendoring or duplicated tasks may
   require further **manual cross-repository** lineage review. The
   group key in the clean metadata is a provisional hint, not a
   certified fork-family split.
5. The full 120-PR discovery screen has 119 retrievable and 1 failed
   PR, with only 62 production-source-path leads, not 120 executable
   tasks. The curation pipeline's automatic **experiment eligible
   count remains 0**, even for the 12-item manual-review shortlist.
6. All six selected LLMs still lack frozen verified inference, and
   trusted five-resource sandbox/independent evaluator remain blocked.
   A compact PR dataset cannot itself finish experiments in a week.

## Realistic seven-day *gated* pilot workflow (NOT a promise)

- **Days 1–2:** reproduce the 120-link curation and audit its 12
  language strata; freeze file hashes, provenance, and shortlist.
- **Days 2–4:** manually triage up to 12 shortlisted source-path
  leads for licensing, authorship, independent pre-fix issue/spec,
  build environment, repository-family overlap and held-out oracle.
  Reject or hold incomplete candidates; never invent eligible tasks
  to meet a schedule.
- **Days 4–5:** independently inspect/approve the runner, GPU metering,
  hidden oracle separation and actual model checkpoint revisions;
  *only after authorization* run bounded six-model A100 preflight.
- **Days 5–7:** if sufficient tasks **actually pass** admission, run a
  small, balanced matched-seed two-policy feasibility pilot and
  analyze cost/failures/attrition. The number of usable tasks may
  legitimately remain zero; then publish a screening-only
  engineering progress report, not an effectiveness result.

The larger preregistered **six-model × eight-policy × three-seed**
experiment is not presumed executable within seven days on one
A100. A few different strata cannot support a universal 12-language
generalization claim without a sufficient independent, qualified
sample in each language. Do not transfer labels across train/test
repos, issue duplicates, or shared hidden oracle assets.

**Source reproducibility:** run
\`python -m unittest discover -s tests -v\` and
\`python -m scripts.build_clean_pr_dataset\`.
The dataset card and GitHub Overleaf source must cite exact
CI-confirmed summary counts and distinguish metadata results from
software reliability results.
