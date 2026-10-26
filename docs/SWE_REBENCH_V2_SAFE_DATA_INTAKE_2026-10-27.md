# Controlled multilingual dataset expansion: SWE-rebench V2

**27 October 2026. Phase:** potential *external* input source,
**NOT downloaded, not split, not independently admitted**.

The official [SWE-rebench V2 dataset card](https://huggingface.co/datasets/nebius/SWE-rebench-V2)
describes **32,079 rows and 20 repository-language categories**. This
is a separate benchmark published by other authors, not a U-CODE
dataset creation claim. It includes gold solution patches,
test patches, FAIL_TO_PASS / PASS_TO_PASS oracles and untrusted
installation/container fields. The card explicitly says to respect each
repository's license and warns that other benchmark overlap may exist.
The displayed HF split is called \`train\`, but that is NOT a U-CODE
train/calibration/evaluation isolation guarantee. Its full Parquet snapshot
has NOT been downloaded by U-CODE.

## Safe opt-in metadata screening on the local CPU

The new [intake module](../src/ucode/external_dataset_intake.py)
reads **only seven projected fields** from existing, locally staged
Parquet files: \`instance_id\`, \`repo\`, \`base_commit\`, \`language\`,
\`license\`, \`created_at\` and \`image_name\`.
No issue text, patch, PR patch description, gold test identifiers, image
commands, environment setup or LLM-generated labels are imported.
This avoids accidental leakage of solution/evaluator-only content
into the candidate discovery table.

To use after independently verifying an exact HF 40-character dataset
snapshot commit and staging its Parquet shards in an approved
**offline** environment:

    python -m scripts.screen_swe_rebench_v2 \
      --parquet /approved/local/snapshot/data/*.parquet \
      --revision YOUR_ACTUAL_VERIFIED_40_HEX_DATASET_COMMIT \
      --output-dir dist/datasets/swe_rebench_v2_metadata_only

Requirements for that opt-in path: \`pyarrow\`, installed and pinned
in a separately reviewed environment (not a default CI dependency).
No remote download, model call, sandbox test, code execution,
model weights or GPU rental is performed by this script.

The output is a source-only candidate CSV, an explicit exclusion
record, a per-language/count report and SHA256 for local source
Parquet files. It normalizes aliases (\`py\`, \`ts\`, \`js\`,
\`cpp\`, \`cs\`, etc.) against U-CODE's **original 12 queried
categories**, rejects malformed IDs/SHAs and missing per-row
license metadata, and marks overlapping repository names or shared
(repo, base SHA) pairs for **manual** review. Do not interpret
casefolded repository-name matches as conclusive patch overlap.

All rows remain \`experiment_eligible=FALSE\`,
\`independent_oracle_verified=FALSE\`, \`split_verified=FALSE\` and
\`NOT_RUN\`. Their upstream existence does not certify that
they can be run safely, are legally reusable, or are unexposed to
a selected LLM's training data. The independent evaluator should
consume oracle metadata only in a separate sealed service and must
validate gold tests independently of the agent.

## Why this helps the one-week goal without fabricating data

- The original 120 public PR discovery sample remains a distinct
  naturalistic-source metadata screen (12 search languages,
  62 production-path leads, zero admitted executables).
- The upstream **32k-row multilingual benchmark source** is a
  *potential task acquisition accelerator*: if rights, image safety,
  independent oracles and actual task build replay are approved,
  a bounded, registered subset could supply better paired
  experimental tasks than weak PR metadata.
- The first safe step is CPU-only **projection** and dedup/overlap
  audits, not loading a full dataset into GPU VRAM or using its
  gold patch as a model prompt.
- For real A100 experiments, allocate a small task set
  *after* re-running an isolated evaluator and freezing six model
  revisions; do not assume all 32,079 published records are admissible.
- Potential publication of a U-CODE-enhanced derivative dataset
  must include genuine new annotation and validation, adhere to
  per-repository license terms, formally cite the source and
  avoid claiming the existing SWE-rebench V2 records as original.

Scientific citation: Ibragim Badertdinov, Maksim Nekrashevich,
Anton Shevtsov & Alexander Golubev (2026), *SWE-rebench V2:
Language-Agnostic SWE Task Collection at Scale*,
https://arxiv.org/abs/2602.23866 .
The official source card and implementation are
https://huggingface.co/datasets/nebius/SWE-rebench-V2
and https://github.com/SWE-rebench/SWE-rebench-V2 .

**Current stage: source identified; no Parquet screening executed
against actual upstream rows; no external benchmark outcome measured.**
