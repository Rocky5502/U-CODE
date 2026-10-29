# U-CODE datasets and provenance — catalog vs executable cohort

**Scientific rule:** A dataset link, source snippet, merged pull request, original GitHub issue or benchmark metadata entry is **not** an independently verified executable correctness task. The [canonical V2 dataset lead registry](../data/discovery/dataset_source_registry_v2_2026-10-24.csv) has **13 candidate sources** with different units and permissions. This is a *catalog*, not 13 datasets downloaded or used in experiments.

## Primary, first-party metadata discovery

| Asset | Evidence as of 29 Oct 2026 | Use and limits |
|---|---|---|
| [120-PR discovery list](../data/discovery/agent_pr_candidates_120.csv) | 120 unique GitHub PR/repository name leads in 12 query-language strata | Candidate discovery; not 120 executable repositories |
| [Completed read-only PR metadata audit](../data/audits/2026-10-24/) | 119 retrieved records, 62 source-path leads | Changed-path and Git SHA metadata; not proof of line-level AI authorship |
| [Frozen curated discovery frame](../data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv) | all 120 discovery rows; includes retrieval failure | No legitimate independent train/test split or real correctness outcomes |
| [Review dossiers](../data/admission/2026-10-25/pilot_dossiers.jsonl) | 12 pending review leads; PHP #104 and Go #43 investigated in more detail | **0** approved executable tasks, **0** sealed functional oracles |
| [SHA-checked metadata-only export](../scripts/audit_dataset_quality.py) | eight source-free files generated locally or via CI | Checks integrity and descriptive data quality, not source rights or software correctness |

The 12 *search* strata: **Python, JavaScript, TypeScript, Java, Go, Rust, C++, C, C#, Kotlin, PHP, Ruby.** These are **not validated changed-code-language coverage**. The 2–5 GB corpus idea is a goal contingent on attribution, rights and executable tasks; no such large corpus is asserted to exist.

## External candidate catalog (not downloaded or qualified)

**Naturalistic / source attribution — cannot be scored as independent software repair without reconstruction:**

| Dataset | Unit / prospective use | Key obstacle |
|---|---|---|
| [AIDev](https://huggingface.co/datasets/hao-li/AIDev) | agent PR/commit/session provenance | Merged bot PR does not prove correct AI-authored lines |
| [SWE-chat](https://huggingface.co/datasets/SALT-NLP/SWE-chat) | agent conversation/session traces | Gated terms, possible PII and lack of independent task oracle |
| [DroidCollection](https://huggingface.co/datasets/project-droid/DroidCollection) | code authorship/attribution snippets | No repository-level functional oracle |
| [CodeMirage](https://huggingface.co/datasets/HanxiGuo/CodeMirage) | AI/human attribution and paraphrase controls | Restrictive license indicated in dated registry; avoid unapproved reuse |
| [MultiAIGCD](https://link.springer.com/article/10.1007/s00521-026-12336-0) | AI-code detection candidate | Paper presence does not establish accessible dataset or executable oracle |

**Controlled-generation repository benchmarks — new generated patches, not naturalistic agent-written PRs:**

| Dataset | Prospectively relevant evaluation | Key obstacle |
|---|---|---|
| [SWE-rebench V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | multilingual issue repair | Dataset-card counts are unverified for local sample; per-repo rights, leakage and executable harness |
| [SWE-bench](https://www.swebench.com/) | repository repair | Oracles/builds require independent evaluation isolation and overlap checking |
| [Multi-SWE-bench](https://github.com/multi-swe-bench/multi-swe-bench) | multilingual issue repair | Edition pin, per-repo license and third-party build safety |
| [SWE-PolyBench](https://huggingface.co/datasets/AmazonScience/SWE-PolyBench) | multilingual repair transfer | Snapshot, data availability, harness and license verification |

**Auxiliary/secondary cohorts — never silently pool with repository-repair success:**

| Dataset | Unit / use | Key obstacle |
|---|---|---|
| [EffiBench-X](https://huggingface.co/datasets/EffiBench/effibench-x) | code efficiency and performance | Different oracle, runtime normalization and task grain |
| [NextCoderDataset-Conversational](https://huggingface.co/datasets/microsoft/NextCoderDataset-Conversational) | conversational code editing training | Not naturalistic PRs; training/held-out separation |
| [OpenCodeReasoning-2](https://huggingface.co/datasets/nvidia/OpenCodeReasoning-2) | synthetic code reasoning | Problem-level tasks; no repository oracle |
| [OpenCodeGeneticInstruct](https://huggingface.co/datasets/nvidia/OpenCodeGeneticInstruct) | synthetic instruction/code tasks | Not naturalistic commits or held-out repository correctness |

The v2 registry's access and license fields are **dated leads**, not licenses granted to U-CODE. In particular, each dataset can contain *upstream code with additional rights requirements*.

## Intake stages and strict splits

`DISCOVERED → METADATA_VALIDATED → ATTRIBUTION_REVIEWED → RIGHTS_CLEARED → INDEPENDENT_SPEC_ATTESTED → SEALED_ORACLE → ISOLATED_EXECUTION_VERIFIED → EXPERIMENT_ELIGIBLE`.

There is currently **no** `EXPERIMENT_ELIGIBLE` real task; stages must not be self-attested by edited JSON. A task card needs immutable pre-fix commit and task-era spec, attribution and file-level rights, source/toolchain snapshot, private independent functional tests, safety/metering signoff and lineage grouping. Naturalistic, reconstructed and controlled generation cohorts must have separate denominators.

- Never copy `patch`, `test_patch`, hidden gold or post-fix reviewer evidence into policy-visible input.
- Keep original task families and fork/near-duplicate repositories on the same split side, with chronological leakage checks.
- Preserve failures/timeouts/abstentions and infrastructure-unknown outcomes in *assigned-task* denominators.
- Store only license-reviewed derived metadata in Git; use ignored `data/raw/`, `data/derived/` and `dist/` for local artifacts.
- [SWE-rebench intake restrictions](../configs/external_multilingual_source_swe_rebench_v2_2026-10-27.json) are **projection-only** and were not run on a downloaded local dataset.

## Reproduce existing *metadata-only* release

```bash
python -m scripts.audit_dataset_quality --output-dir dist/ucode-pr-metadata-clean
python -m scripts.verify_dataset_release dist/ucode-pr-metadata-clean
python -m scripts.audit_lineage_risks --output-dir dist/ucode-lineage-review
python -m scripts.verify_lineage_review dist/ucode-lineage-review
```

See [curation source card](../data/curated/README.md), [data governance](DATA_GOVERNANCE.md), [admission policy](PILOT_ADMISSION_EVIDENCE_GATE_2026-10-25.md) and [external SWE-rebench intake](SWE_REBENCH_V2_SAFE_DATA_INTAKE_2026-10-27.md).
