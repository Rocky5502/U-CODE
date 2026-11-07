# U-CODE: full 13-source dataset and code readiness review

**Review date:** 7 November 2026  
**Review scope:** frozen GitHub U-CODE metadata and source tree, first-party Python 3.10/3.12 CI, selective current publisher/Hugging Face dataset-card checks. **No external dataset payloads, code, images, models, sensitive reviewer forms or gold/test patches were downloaded or run.** This is *not* a scan of the student's local drives, and it cannot certify the external sources, legal rights, human decisions or entire research program as ready.

The executable, deterministic, source-only review is:

```bash
python -m scripts.audit_all_dataset_readiness --output-dir dist/ucode-all-datasets-readiness
python -m scripts.audit_all_dataset_readiness --require-runnable
# The strict command exits 2: there are no independently admitted real tasks.
python -m unittest discover -s tests -v
```

The exporter produces `ALL_DATASET_READINESS.json` (each source and code group), `ALL_DATASET_CODE_STATUS.md` and `ALL_DATASET_STATUS_SHA256.json`. The third file hashes the other two; SHA equality certifies *file consistency*, not genuine license, source authenticity or code execution.

## Summary: catalogued is not runnable

| Status unit | Current evidence | Not an authorization for |
|---|---|---|
| External source catalog | **13** entries, all `local_execution = not_executed` | 13 local datasets, 13 benchmark-ready cohorts |
| 120-link original discovery frame | **120** frozen links, **119** metadata records, **62** production-path leads | 120 real runnable tasks or verified authorship |
| Human-review shortlist | **12** candidate leads, reviewer forms are pending | Signed approvals or gold correctness |
| PHP/Go pilot | Two dossiers, **16/16** admission gates pending | Actual source-era task admission |
| Six LLMs | Six named/model-card choices; **0** qualified checkpoint revisions | Six model evaluations, licenses accepted, or measured VRAM |
| Policy study | Eight frozen named confirmatory slots; **0** faithfully validated on independent real tasks | Eight working, benchmark-matched agents |
| First-party code | Ten **representative component groups** have expected source/test scaffolds; CI checks Python contract tests | Entire codebase reviewed, real runtime, attack-resistant sandbox |
| Measured effects | **N/A** | Accuracy, calibration, risk, resource or novelty claims |

**Important:** Static code presence and synthetic CI pass are real engineering results, but they do not establish training/evaluation data readiness, independent test quality, model licensing, or agent correctness. No blanket completion percentage is meaningful.

## All 13 external sources: recommended roles and blocking evidence

| # | Source / primary catalog | Suitable U-CODE role | Biggest remaining constraints |
|---:|---|---|---|
| 1 | [AIDev](https://huggingface.co/datasets/hao-li/AIDev) | Real-world developer-agent PR **metadata/provenance only** | Its dataset card now describes v5/AIDev-7.6M; pin a specific immutable revision, author-level/task provenance, privacy, and reuse rights; not an oracle |
| 2 | [SWE-chat](https://huggingface.co/datasets/SALT-NLP/SWE-chat) | Naturalistic agent interactions, prompt/tool provenance | **Gated**; requires approved access, privacy/PII review and separation of source-code rights. No real downloaded local snapshot |
| 3 | [DroidCollection](https://huggingface.co/datasets/project-droid/DroidCollection) | Human/AI/mixed code attribution | Snippet labels do not give repository-level patch correctness; source rights/license review remains pending |
| 4 | [SWE-rebench V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | Potential task-candidate metadata for broader repair evaluation | Public dataset lists 32,079 tasks and includes gold patches/test patches and a `train` split; **do not** expose gold fields to policies or infer a valid independent split; pin dataset release, license per repo and independently revalidate oracles |
| 5 | [SWE-bench](https://www.swebench.com/) | Comparable issue-resolution task source after admission | Cross-benchmark contamination, repository lineage, reproducible environment and hidden-test independence |
| 6 | [Multi-SWE-bench](https://github.com/multi-swe-bench/multi-swe-bench) | Cross-language issue-resolution candidate tasks | Pin task edition, correct changed-language grain, per-repo rights, security and evaluator fidelity |
| 7 | [SWE-PolyBench](https://huggingface.co/datasets/AmazonScience/SWE-PolyBench) | Separate multilingual code-repair comparison after admission | Its published full benchmark covers **four** languages (JS, TS, Python, Java), **not all 12** U-CODE discovery search strata; verify edition/task overlap and sandbox |
| 8 | [EffiBench-X](https://huggingface.co/datasets/EffiBench/effibench-x) | **Efficiency-only secondary** analysis | Different outcome grain and runtime/tooling; no pooling with repository repair ITT |
| 9 | [CodeMirage](https://huggingface.co/datasets/HanxiGuo/CodeMirage) | Auxiliary authorship/detection research | Dataset card marks **CC-BY-NC-ND 4.0**; do not assume derivative redistribution, commercial or modifications permitted; no repo correctness oracle |
| 10 | [MultiAIGCD](https://link.springer.com/article/10.1007/s00521-026-12336-0) | AI code detection/attribution only | The 2026 publication links a [public dataset/code repository](https://github.com/BasakDemirok/MultiAIGCD); its actual contents, version, third-party CodeNet rights and suitability remain independently unreviewed |
| 11 | [NextCoderDataset-Conversational](https://huggingface.co/datasets/microsoft/NextCoderDataset-Conversational) | Auxiliary *synthetic* edit training only | Synthetic editing conversations; NOT real repository patches or test oracle; train/eval leakage and upstream code licensing review |
| 12 | [OpenCodeReasoning-2](https://huggingface.co/datasets/nvidia/OpenCodeReasoning-2) | Synthetic code reasoning / critique training | Mostly competitive-programming question units; not task-specific repo-level correctness |
| 13 | [OpenCodeGeneticInstruct](https://huggingface.co/datasets/nvidia/OpenCodeGeneticInstruct) | Synthetic instruction-finetuning | No independent executable project oracle and original-source licensing/overlap checks remain |

**Data provenance distinction:** The catalog URLs and card metadata are source discovery, not local downloads or independently inspected examples. Six current source-card checks above were supplemented with direct publisher/Hugging Face metadata (AIDev, SWE-chat, SWE-rebench V2, SWE-PolyBench, CodeMirage and NextCoder); other entries remain catalog-level and must be rechecked before an actual download or paper performance comparison.

**Sampling caveat:** SWE-rebench V2's published `train` label is a dataset-provider split name, **not** authorization to use those tasks as an independent U-CODE train or held-out test group. The current opt-in `external_dataset_intake.py` adapter correctly projects only seven non-oracle metadata fields from a **user-provided, version-pinned local Parquet**, and its fixtures are synthetic. Do not run external `install_config`, Dockerfiles, dataset scripts or test commands during catalog triage.

## Code readiness: ten representative integration groups

| Component checked | First-party entrypoint / test | What remains unproven |
|---|---|---|
| PR metadata quality | `scripts/audit_dataset_quality.py` / `tests/test_dataset_quality.py` | External source contents/rights and lineage correctness |
| 13-source identity crosswalk | `scripts/audit_dataset_cohort_crosswalk.py` / `tests/test_dataset_cohort_crosswalk.py` | Every remote card's current downloadability and schema |
| External projected intake | `src/ucode/external_dataset_intake.py` / `tests/test_external_dataset_intake.py` | User-supplied pinned Parquet snapshot, safe parser, physical storage |
| Source-era task admission | `src/ucode/pilot_preflight.py` / `tests/test_pilot_preflight.py` | Real independent spec/rights/functional oracle |
| Reviewer evidence integrity | `src/ucode/external_admission_receipt.py` / `tests/test_external_admission_receipt.py` | Real independently verified reviewer identities and claims |
| Evaluator isolation | `src/ucode/evaluator_boundary.py` / `tests/test_experiment_contract.py` | Real segregated evaluation environment |
| Model gate | `src/ucode/model_readiness.py` / `tests/test_model_readiness.py` | Six pinned validated weight/tokenizer/engine revisions |
| Conditional/multivariate acquisition | `src/ucode/conditional_bes.py`, `src/ucode/joint_frequency_controls.py` | Real labelled calibration, complete faithful policy implementations |
| Sandbox preflight | `src/ucode/oci_sandbox_preflight.py` | Actual rootless nonnetwork execution and five measured caps |
| Springer manuscript source | `paper/overleaf/main.tex` / `scripts/audit_overleaf_sources.py` | Real RQ outcomes, compiled publisher PDF and external live Overleaf sync |

This table is a **sampled architectural inventory, not a line-by-line audit of all Python modules**. The new code checks that each named source/test file still exists, while GitHub Actions executes its established full standard-library and optional-crypto test suite separately.

## Critical reproducibility defect found and quarantined

`configs/experiment_matrix.json` was an **older 7-arm / 4-budget** research sketch. The frozen scientific protocol `configs/confirmatory_sbse_protocol_2026-10-25.json` requires **8 registered arms** and **5 budget dimensions** (tokens, test calls, GPU seconds, CPU seconds, wall seconds), with the primary comparison **`ucode_conditional_bes` vs `no_uncertainty_search`**. Such parallel, contradictory configs would make a real reproducer choose the wrong experiment.

The historical sketch now contains a **machine-readable deprecation/quarantine notice** referencing the authoritative registration; it has NOT been replaced with invented experiment assignments. The new audit and tests fail closed if the deprecation is removed or if a report silently uses old arms, fake model runs or rights/oracle approvals.

## What to do next

1. **Reproduce and freeze metadata-only inventory:** inspect all 13 source cards, capture exact commit/release, license/version, available columns, actual programming-language granularity, local disk receipts and reviewer rights decisions. Avoid downloading large/private sources until access and privacy review are complete.
2. **Qualify one runnable task:** source-era PHP/Go spec, correct scope, licensing, separate sealed oracle, sandbox and real independent reviewers. The strict G5 pilot gate must still return blocked until this happens.
3. **Then pilot at a small independently admitted cohort:** validate the chosen six model/checkpoint/tokenizer combinations, resource meters and seven non-oracle intake fields against real tasks, record attrition without deleting failed cases.
4. **Only then evaluate matched policies:** eight registered arms and five-vector resource caps, separated repository families and blinded postterminal oracle joins, real calibration/coverage estimates. Do not treat source metadata, synthetic witnesses or CI passes as experiment results.

This review intentionally does not modify results tables or claim a new model/dataset evaluation. The canonical Overleaf sources remain prospective; a live Overleaf PDF or external task corpus has not been accessed.
