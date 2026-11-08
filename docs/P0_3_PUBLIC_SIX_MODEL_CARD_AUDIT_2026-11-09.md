# P0-3: six-model public Hub-card audit and BF16 storage sanity check

**9 November 2026 · PUBLIC, OBSERVATIONAL, NOT LEGAL APPROVAL OR RUNTIME ATTESTATION**

U-CODE's **exact six planned model identifiers remain unchanged**. This read-only provenance audit compares a public Hugging Face model-card metadata observation against the October frozen planning manifests. It does not freeze a real checkpoint or alter the registered primary evaluation contrast. No private account permission was queried, gated model was accessed, weight downloaded, code executed, model inference run, or GPU memory measured.

## Public metadata observations

Hugging Face Hub repository details were inspected on 9 November 2026. The values below represent **public card labels as observed**, not authenticated, signed, timestamped Hub responses or a legal reading of a license file. Parameter counts are rounded public reported totals, not a measured inventory of weights.

| Exact model and public model card | Reported parameters | Public Hub license tag | Card reports gated? | Approximate BF16 weights-only GiB |
|---|---:|---|---|---:|
| [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) | 7.616B | apache-2.0 | No | 14.19 |
| [Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) | 30.532B total (MoE) | apache-2.0 | No | 56.87 |
| [Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512) | 24.011B | apache-2.0 | No | 44.72 |
| [DeepSeek-Coder-V2-Lite-Instruct](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) | 15.707B total | other | No | 29.26 |
| [CodeGemma-1.1-7b-it](https://huggingface.co/google/codegemma-1.1-7b-it) | 8.538B | gemma | **Yes** | 15.90 |
| [Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) | 8.030B | llama3.1 | **Yes** | 14.96 |

The approximate BF16 calculation is (reported total parameters × 2 bytes) / 2^30. It assumes all counted parameters are BF16 and excludes model runtime, tokenizer, dequantization buffers, CUDA kernels, KV cache, activation memory, non-weight tensors, memory fragmentation, batching, context length, offloading, driver reservations and any quantization. These are **storage-only rough scenarios**, not strict verified lower bounds from weight files, not model startup/peak VRAM measurements, and not predictions of throughput or rental cost. Qwen3's **3B activated** experts do *not* imply 3B total stored weights.

Against a **hypothetical** 16 GiB physical memory capacity, the 30.5B, 24B and 15.7B BF16 storage estimates exceed it before any runtime overhead. Qwen2.5, CodeGemma and Llama have rough BF16 storage below 16 GiB, but that provides **no evidence they actually load or run** on a 16 GiB GPU. An 80 GiB host may clear the abstract weight storage scenario for all six one-at-a-time, yet engine/precision/quantization, KV-cache and compatibility must still be verified. These estimates do not authorize compute rental.

## Material metadata discrepancy: do not silently edit the frozen plan

The October selected manifest historically labels DeepSeek-Coder-V2-Lite-Instruct with card_license = deepseek-license, while the public Hub metadata observed here is other. **Neither label is a reviewed license text, a snapshot of the license grant, or proof that the legal terms changed.** The audit records both and raises a human-review flag. Preserve the original October manifest as a historical planning artifact; do not automatically replace the license and call the changed value approved. Require a reviewed version-pinned full license with explicit use and redistribution suitability.

Google CodeGemma and Meta Llama display gated public model cards. That is not evidence that the authorized study account has accepted terms or can download either model. The other four public card labels are likewise not independently authenticated rights decisions.

## What the new audit verifies and explicitly does not

Files:
- [Bounded public observation snapshot](../data/admission/2026-11-09/six_model_public_hub_cards_OBSERVATION_ONLY.json) — no checkpoint SHAs, account tokens, acceptance artifacts, weight hashes or VRAM measurements.
- [Cross-manifest validator](../src/ucode/public_model_card_audit.py) — compares all six exact IDs with the original study registration and source inventory, calculates decimal approximate weight-only storage and reports license-card label discrepancies.
- [Zero-network CLI](../scripts/audit_six_public_model_cards.py) and [adversarial tests](../tests/test_public_model_card_audit.py).

Reproduce locally:

    python -m scripts.audit_six_public_model_cards --output dist/ucode-six-model-public-card-observation-NO-APPROVAL.json
    python -m scripts.audit_six_public_model_cards --hypothetical-gpu-gib 80
    python -m scripts.audit_six_public_model_cards --require-six-ready
    # Last command MUST exit 2; public card labels cannot grant readiness.
    python -m unittest discover -s tests -p 'test_public_model_card_audit.py' -v

The tests are **first-party synthetic/metadata consistency checks**, not an independent model safety assessment. A valid-looking public card URL, file digest or model SHA is not proof of source authenticity, authorized access or reproducible inference. The public observation file has no authenticated retrieval-time commitment, so these labels are **not** called immutable verified Hub revisions. CI only replays local snapshot data and rejects false claims of rights, checkpoint pinning, model loads and memory measurements.

## Operator-ready P0-3 exit checklist — still open

1. Independently inspect **each exact model's complete terms text** at the version intended for use; record approved use/redistribution/derivative constraints. Treat card license *tags* as discovery hints, not approvals. Resolve DeepSeek other versus deepseek-license in the reviewed rights memo.
2. Verify explicitly whether the authorized account can access Google CodeGemma and Meta Llama; keep credentials/acceptance records outside GitHub and Overleaf.
3. Freeze full 40-hex Hugging Face commit revisions for weights **and tokenizer**, exact chat-template bytes/hash, actual safetensor file identities/hashes, engine version and precision/quantization.
4. After explicit authorization, run **first-party model-load canaries** on the trusted intended machine, one model at a time, recording actual peak VRAM, time-to-first-token, decode speed and output token accounting. Report offload separately; do not fabricate fit or speed.
5. Independently review runtime sandbox/dependency rights and six-model licensing. For real *coding* experiments, also require an independently admitted task, a sealed evaluator-only oracle, faithful matched policy implementations and all **five enforced** resource caps.

The frozen scientific treatment, comparator and endpoints remain unchanged. **Zero** independently qualified model checkpoints, real inferences, admitted Go/PHP tasks, independent evaluator oracles, or measured confirmatory outcomes are created by this audit. The Springer manuscript source on GitHub is not a live Overleaf editor. See [phase-0 operator runbook](REAL_EXPERIMENT_PHASE0_OPERATOR_RUNBOOK_2026-11-08.md) and [critical-path status](UCODE_PROGRESS_CRITICAL_PATH_2026-11-07.md).
