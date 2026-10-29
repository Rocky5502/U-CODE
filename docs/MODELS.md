# U-CODE model matrix — planning, licenses, and readiness

**Authority:** [selected six models](../configs/accepted_six_model_study_2026-10-25.json), [confirmatory study](../configs/confirmatory_sbse_protocol_2026-10-25.json), [A100 deployment profile](../configs/ai_galaxy_six_model_deployment_2026-10-27.json). This document does not override the exact selected IDs. Current stage: **no six-model inference completed**.

## Exact research roster

| # | Model (Hugging Face card) | Family | Advertised card license¹ | Planned preliminary deployment | Current status |
|---|---|---|---|---|---|
| 1 | [Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) | Qwen | Apache-2.0 | 16GB quantized feasibility first; proposed A100 sequential | Not downloaded/pinned or verified |
| 2 | [Qwen/Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) | Qwen MoE | Apache-2.0 | high memory/A100 preflight only | Not downloaded/pinned or verified |
| 3 | [mistralai/Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512) | Mistral | Apache-2.0 | A100 80GB, kernel/dtype test required | Not downloaded/pinned or verified |
| 4 | [deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) | DeepSeek MoE | deepseek-license | A100 high-memory + **custom-code security review** | Not downloaded/pinned or verified |
| 5 | [google/codegemma-1.1-7b-it](https://huggingface.co/google/codegemma-1.1-7b-it) | Gemma | gemma | 16GB quantized feasibility; gated/terms review | Not downloaded/pinned or verified |
| 6 | [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) | Llama | llama3.1 | 16GB quantized feasibility; gated/terms review | Not downloaded/pinned or verified |

¹ These strings reproduce the **dated model-card metadata in the canonical manifest**; they are not a present-day independent license audit, consent to terms, proof of redistribution rights or a declaration that all repositories remain available.

**MoE warning:** the A3B/active parameter count is *not* the resident total weight footprint. BF16 weight-size estimates omit KV cache, workspace, context length, batching and other overhead. No six-model simultaneous A100 fit is asserted.

## Freeze each model before any real run

For every exact model ID, separately record:

1. Full HF **40-hex commit SHA** for weight and tokenizer snapshots; SHA256 of chat template and downloaded shard receipts.
2. Model-card and full license/terms snapshot; account authorization and geographic/usage restrictions as applicable; no gated weight redistribution.
3. Inference engine exact version/commit, PyTorch/CUDA/driver version when used; execution backend, precision and quantization artifact; explicit permission to run remote code only after review.
4. Verified chat/instruction formatting, context/window limits, sampling temperature/top-p/max tokens/seed, prompt code commit and hash.
5. An actual small local load and inference preflight **after** review: measured peak VRAM, throughput, memory margin and failure logs; do not infer resource feasibility from weight sizes.
6. Experiment receipts: task ID/family, policy ID, seed, five *actual* resources (tokens, test calls, GPU/CPU/wall seconds), public evidence trail and separately sealed evaluator verdict.

**Never substitute:** `configs/models.json` and `configs/models_v2_2026-10-24.json` are historic candidate inventories, not the six-study authority. The selected six are fixed unless a documented *prospective* justified amendment is approved before outcomes.

## Runtime tiers and honest limits

- **Offline verification:** `python -m scripts.audit_six_model_crosswalk`, `python -m scripts.plan_ai_galaxy_six_models` and `python -m scripts.check_local_readiness`. These perform configuration checking, not downloads or inference.
- **Local 16 GB GPU:** potential quantized feasibility for selected 7B/8B-class models; **not guaranteed**. Record exact hardware/quantization and compare with full precision or a matched reference where appropriate.
- **External A100 80 GB:** the existing configuration proposes *one model at a time*, with its own fit test. This document **does not authorize a rental or claim completed model inference**. Devstral-specific FP8/Ampere fallback must be tested with the exact checkpoint and engine. Do not enable `trust_remote_code` indiscriminately.
- **Model serving:** only local-loopback endpoints until reviewed; no real code/task text sent to external APIs without documented privacy, budget and research approvals.

See [local preflight](LOCAL_EXPERIMENTS.md), [SECURITY](../SECURITY.md) and [upstream license boundary](DATA_GOVERNANCE.md).
