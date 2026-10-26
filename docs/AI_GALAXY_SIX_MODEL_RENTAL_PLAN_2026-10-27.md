# U-CODE — all-six model deployment plan for AI Galaxy rental GPUs

**Dated:** 27 October 2026. **Stage:** configuration and research hardware sizing;
**none** of the six checkpoints downloaded, pinned, license-reviewed or run.
No GPU instance rented by this commit, and no external code executed.

## Canonical references

- Immutable **model identities** and scientific roster:
  `configs/accepted_six_model_study_2026-10-25.json`.
- Proposed **all-six deployment profiles**:
  `configs/ai_galaxy_six_model_deployment_2026-10-27.json`.
- Read-only validator/preview:
  `python -m scripts.plan_ai_galaxy_six_models`,
  `python -m scripts.plan_ai_galaxy_six_models --profile simultaneous_six_gpu --json`.
- The original `src/ucode/model_readiness.py` remains the actual
  provenance/license/runtime gate: planning services does not pass it.

## How much VRAM?

These figures are **approximate decimal BF16 weight-only lower bounds**
derived from parameter count × two bytes. KV cache, prompt prefill,
framework allocations, CUDA graphs, MoE routing, concurrent requests and
long-context expansion **add substantial VRAM**. HF architecture/parameter
metadata were read 27 Oct 2026; numbers are not device measurements.

| Selected HF checkpoint | ~Parameters B | BF16 weights, GB | Initial GPU | Initial model context |
|---|---:|---:|---|---:|
| Qwen/Qwen2.5-Coder-7B-Instruct | 7.616 | 15.2 | A100 SXM4 80GB | 16K |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 30.532 total MoE | 61.1 | A100 SXM4 80GB | 8K |
| mistralai/Devstral-Small-2-24B-Instruct-2512 | 24.011 | 48.0 BF16 equivalent | H100 80GB preferred for native FP8 | 8K |
| deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | 15.707 total MoE | 31.4 | A100 SXM4 80GB | 8K |
| google/codegemma-1.1-7b-it | 8.538 | 17.1 | A100 SXM4 80GB | 16K |
| meta-llama/Llama-3.1-8B-Instruct | 8.030 | 16.1 | A100 SXM4 80GB | 16K |

**Qwen3 3B active and DeepSeek MoE active parameter counts DO NOT mean
only the active experts' weights need storage.** Model-native Devstral FP8
is not equivalent to a guaranteed A100-compatible FP8 kernel:
H100 is the conservative preference, subject to engine and image checks.
At 8K/16K initial context and one active sequence, 80GB per process is a
planning target, NOT proof no OOM will occur. Benchmark prompt length,
tokens/sec and peak allocated/reserved memory before any large batch.

## One GPU versus six

- **Sequential (recommended first):** rent one A100 80GB for most
  model-by-model preflights; if native Devstral FP8 kernel compatibility
  fails use an H100 80GB for that checkpoint. Prefer 128GB host RAM
  (64GB absolute staging floor), 16+ CPU cores, 500GB–1TB local NVMe,
  fast internet/cached models and 1 live inference engine at a time.
  The AI Galaxy public A100 base listing showing 8 CPU cores/16GB
  requires checking upgraded host RAM and CPU options before checkout.
- **True simultaneous six services:** reserve **six separate suitable
  80GB GPUs** (with H100 for native FP8 Devstral, or verified compatible
  alternative) to minimize multi-process OOM and policy interference.
  Different unique service ports 8100–8105 are registered, but no ports
  have been started. This is an initial reliable capacity plan;
  packing smaller models on fewer cards is an unverified optimization.
  Each instance should have a rights-approved model cache and adequate
  RAM; across multiple nodes use a private, authenticated network only.

**Do not mix the two meanings of 'configure all models at once':** all six
identities, hardware targets, initial contexts, endpoints and gates
can be registered in one config; this does not launch six processes,
download weights or grant gated model licenses.

## Public AI Galaxy price references (not a quote or live booking)

At time of this plan the [AI Galaxy public homepage](https://www.ai-galaxy.cn/)
advertised promotion-style rental prices **per GPU-hour**:
RTX 3090 24GB ¥1.10; RTX 4090 24GB ¥1.65; A40 48GB ¥2.20;
RTX A6000 48GB ¥2.40; and A100 80GB ¥8.00.
The [provider storefront](https://gpu.ai-galaxy.cn/store) is a
dynamic catalog; real checkout **availability, host-RAM upgrades,
duration pricing, storage, bandwidth and discount eligibility remain
unverified**. H100 pricing/availability was not established.
At the advertised A100 price, 50 charged A100-GPU-hours = ¥400,
100 = ¥800, 200 = ¥1,600, exclusive of all extras.
Six separately rented A100s at the same advertised rate cost
¥48 per concurrent hour (and six A100s for 100 clock-hours ¥4,800),
but this is not a recommendation to prepay and an H100 changes cost.

## Dataset and reproducibility are different gates

The repository's earlier 120-PR dataset screen is **metadata
discovery**, not 120 admissible real executable tasks. The latest
canonical admitted-task count remains ZERO, pending independent
file-level source rights, pre-fix specification, isolated runner,
sealed oracle and lineage screening. Having many PR links or a
large locally stored dataset does NOT validate the experimental
denominator. Record exact number of approved tasks and expected
pre/postfix data bytes before deciding on storage or GPU hours.
Load tasks by stream/shards and avoid loading all data into GPU VRAM.

For planning only, if `N` admissible tasks, `S` seeds, `P` policies
and all six checkpoints receive equal prospective opportunities,
there are `N * S * P * 6` experimental assignments.
GPU-hours are NOT derivable from this count without **measured**
tokens/sample latency, failed-run/timeout costs and actual tool costs.
Do not insert guessed GPU throughput in the journal Results.

## Experimental gates before compute

1. Approve exact model card and applicable full license for all six,
   including gated Google CodeGemma and Meta Llama access.
2. Freeze exact 40-hex HF weight and tokenizer revisions;
   review DeepSeek custom modeling code before enabling any
   `trust_remote_code` behavior.
3. Pin and review actual runtime container image, CUDA/driver,
   vLLM/Transformers/llama.cpp versions, compatible Mistral3/FP8
   backend, chat template, dtype/quantization, context and seed.
4. Measure real peak VRAM, throughput, initial latency, memory spikes,
   token accounting and five-vector cost for every checkpoint; freeze
   appropriate context caps per model (or report exclusions).
5. Prepare independent rights-cleared, fully admitted tasks and sealed
   evaluator, rootless network-off runner, trustworthy external
   five-resource measurement, and mutually comparable policy workloads.
6. Confirm GPU price/stock in authenticated provider checkout and
   authorize spending; the offline script does not transact or rent.
7. Preserve unqualified tasks as transparent exclusions and failed
   engine loads as failures, not as silent removal of large models.

A single rental GPU can serve six models one after another; the
scientific six-model study still remains **prospective**, and no
model-specific deployment is yet executable or measured.
