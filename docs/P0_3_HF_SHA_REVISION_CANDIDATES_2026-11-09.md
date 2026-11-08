# U-CODE P0-3: public Hub main-SHA candidate capture (not a model checkpoint approval)

**9 November 2026. Stage: PUBLIC COMMIT CANDIDATE / THIRD-PARTY MODEL WEIGHTS NOT DOWNLOADED.**

The six user-selected model IDs and October confirmatory study contract remain frozen. Public Hugging Face model metadata sometimes contains a full 40-hex Git commit SHA for the current moving `main` branch. That is a useful **candidate revision identifier** for reproducibility planning, but it is **not** a verified weight snapshot, a separately approved tokenizer/chat template, a signature, a license/terms decision, or evidence that model files were downloaded or loaded.

The previous [six-model public-card report](P0_3_PUBLIC_SIX_MODEL_CARD_AUDIT_2026-11-09.md) documented gated cards, model families, a DeepSeek license-label discrepancy and rough BF16 weight-only estimates. It did not pin Git revisions. This addition avoids inventing a SHA from a seven-character abbreviated web history or an undated snippet. Public Hub `main` may change **after observation**.

## Commands — default mode is completely offline

From a trusted U-CODE checkout:

```bash
python -m scripts.capture_public_hf_sha_candidates
python -m scripts.capture_public_hf_sha_candidates --output dist/six-model-SHA-PENDING-NO-APPROVAL.json
python -m scripts.capture_public_hf_sha_candidates --require-approved
# The final command MUST exit 2. None of the six models is licensed and qualified by a branch SHA.
```

Default mode **does not call the network**, and reports six pending candidate rows with null SHAs. It checks the exact six historical model IDs, the selected model registry, the protocol's unchanged pending status, and absence of experiments.

## Explicit optional operator capture — public metadata only

When the authorized human operator wants fresh **public** Hub branch metadata, and network policy permits:

```bash
python -m scripts.capture_public_hf_sha_candidates \
    --capture-public-heads \
    --output /private-study-metadata/six_model_hub_main_SHA_CANDIDATES.json
```

This uses `GET https://huggingface.co/api/models/<exact frozen model ID>?expand=sha` for each of **six** fixed repositories, with **no credentials**, no token from environment, no account operations, no git clone, no weight/README/tokenizer download, no model execution, and no paid inference. It disables HTTP proxies and redirects, caps response size to 32 KiB, enforces JSON content type and a strict lowercase full-40-hex SHA, and fails closed to **unavailable** when public access is blocked. Non-SHA metadata, HTTP errors and raw response bodies are neither stored nor printed.

The output contains only six known model IDs, fixed public URLs and optional branch-SHA candidates plus explicit **false** fields for rights, file checksums, signed provenance, model loading, and model use. A public SHA may be an actual Hub repository identifier but can still be stale at processing time. The CLI does **not** assert that `main` remains unchanged, that model card claims are trustworthy, or that any pinned model weights have been individually cryptographically checked.

**Security:** Never commit operator-specific credentials, signed rights notes, private gated-access evidence, license acceptance logs or downloaded model weight files to this repository. Public candidate SHA values may be reported in the metadata study with dates and separate trusted custody, but only after review.

## Authenticated revision and model-readiness exit requirements

After the authorized operator captures public candidate hashes, a separate review must:
1. Independently confirm the **exact full Git revision** and whether the same immutable revision contains the intended model configuration, tokenizer, special tokens and chat template. Freeze exact content digests for files as needed; do not assume a branch pointer commits the right execution behavior forever.
2. Inspect the full license text and account terms at the intended revision. CodeGemma and Llama public cards are gated; do not mistake visible metadata for access entitlement. Resolve historical `deepseek-license` versus Hub `other` metadata labels from the actual license.
3. Inspect file integrity and model weights, including Xet/LFS/safetensor identities and consistency with the expected architecture, without trusting a claimed SHA as a signed attestation.
4. Freeze the inference engine, tokenizer parser, generation/chat template, seed, batch size, context/precision and quantization strategy, and rights for any third-party custom code.
5. After approval, conduct a **separate, actual machine-level** canary for VRAM/load/timing on the intended GPU, with independent five-resource metering. Only then can a model be marked technically runnable; benchmark evaluation still needs an admitted task, sealed evaluator oracle and rootless network-off sandbox.

## Tests and immutable scientific boundary

- [Public-only SHA capture implementation](../src/ucode/hub_revision_preflight.py)
- [Offline-by-default CLI](../scripts/capture_public_hf_sha_candidates.py)
- [18 adversarial offline tests](../tests/test_hub_revision_preflight.py)

CI runs **only default offline mode** and asserts `--require-approved` exits 2; it does not call the Hugging Face API. A mocked SHA observed during an offline test is **invented test data**, not a real model revision. The repository's six frozen planned identities, eight policies, five illustrative resource caps and 0 real results are unchanged. No code or data in this PR should be read as independent external signoff.

Next practical operator action: use the opt-in metadata-only capture on an authorized network and request separately authenticated, reviewed license/checkpoint/tokenizer/engine/weight-integrity decisions. Model weights, real third-party source tasks and evaluator gold remain completely outside this audit.
