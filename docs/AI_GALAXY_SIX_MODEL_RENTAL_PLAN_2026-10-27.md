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
- **Scenario GPU-days and cost** (`--minutes-per-assignment` is a required
  explicitly assumed or later measured value):
  `python -m scripts.estimate_ai_galaxy_rental --tasks 40 --policies 2 --seeds 1 --minutes-per-assignment 5`.
  This example is not a runtime benchmark or proof of qualified tasks.
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
| Qwen/Qwen2.5-Coder-7B-Instruct | 7.616 | 15.2 | A100 80GB | 16K |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 30.532 total MoE | 61.1 | A100 80GB | 8K |
| mistralai/Devstral-Small-2-24B-Instruct-2512 | 24.011 | 48.0 BF16 equivalent | A100 80GB with tested Marlin W8A16 or BF16 | 8K |
| deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | 15.707 total MoE | 31.4 | A100 80GB | 8K |
| google/codegemma-1.1-7b-it | 8.538 | 17.1 | A100 80GB | 16K |
| meta-llama/Llama-3.1-8B-Instruct | 8.030 | 16.1 | A100 80GB | 16K |

**Vendor-SKU verification:** the AI Galaxy public homepage lists
`NVIDIA A100 80G`, not a guaranteed PCIe-vs-SXM4 variant.
Either A100 80GB variant is compatible with the one-GPU-family
deployment plan in principle; record the actual GPU name,
PCIe/SXM4 interconnect, driver, CUDA runtime, and measured
prefill/decode tokens/sec before costing the study. No
specific speed is assumed from the storefront entry.

**Qwen3 3B active and DeepSeek MoE active parameter counts DO NOT mean
only the active experts' weights need storage.** Model-native Devstral FP8
has an A100 path: the official Mistral documentation
lists H100 **or A100** for Devstral Small 2; vLLM supports
FP8 *weight-only* W8A16 on Ampere via Marlin kernels.
A100 does not natively accelerate FP8 W8A8. The exact Mistral3
architecture, pinned vLLM build, startup and token behavior
still need runtime preflight; fall back to BF16 *on the same A100*
only after a measured memory check. No H100 is required in this plan.
At 8K/16K initial context and one active sequence, 80GB per process is a
planning target, NOT proof no OOM will occur. Benchmark prompt length,
tokens/sec and peak allocated/reserved memory before any large batch.

## One GPU versus six

- **Sequential (required user plan):** rent only **one A100 80GB** and
  preflight **all six** model checkpoints, one after another.
  Devstral runs using a verified Ampere/Marlin weight-only FP8
  path or a validated BF16 path on the same A100; do **not**
  prescribe a different GPU family. Prefer 128GB host RAM
  (64GB absolute staging floor), 16+ CPU cores, 500GB–1TB local NVMe,
  fast internet/cached models and 1 live inference engine at a time.
  The AI Galaxy public A100 base listing showing 8 CPU cores/16GB
  requires checking upgraded host RAM and CPU options before checkout.
- **Optional capacity comparison only (NOT the rental recommendation):**
  six separate A100 80GB GPUs, all the same GPU family, minimize
  model residency contention. This is not budget-authorized and
  cannot be assumed cost-effective.
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
unverified**. No H100 or other GPU family is required or budgeted.
At the advertised A100 price, 50 charged A100-GPU-hours = ¥400,
100 = ¥800, 200 = ¥1,600, exclusive of all extras.
Six separately rented A100s at the same advertised rate cost
¥48 per concurrent hour (and six A100s for 100 clock-hours ¥4,800),
but this is not a recommendation to prepay; the user's approved
hardware choice is only A100 80GB.

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


## Rental duration is gated by measured task throughput

**Do not rent continuously while source admissions, oracle validation,
gated-model access, checkpoint pinning or code security reviews remain open.**
The research roadmap previously proposed a 40–60-task feasibility pilot
and approximately 250–400 unique-task confirmatory evaluation. The
canonical frozen registration includes **six models, eight prospective
policies, and three illustrative (NOT finalized) seeds**. These are
experimental design proposals, not completed runnable cells.

On a single sequential A100, estimated *charged GPU-days*
for N approved tasks, M models, P policies, S seeds and measured
minutes per policy assignment are:

```
GPU_hours = N * M * P * S * average_measured_minutes / 60
GPU_days  = GPU_hours / 24
subtotal_RMB = GPU_hours * checkout_RMB_per_GPU_hour
```

**Scenarios, not performance measurements:**

| Scenario | Model × policy × seed allocations | Hypothetical minutes/assignment | GPU time |
|---|---:|---:|---:|
| One-day preflight budget cap | ≤24h | Not a task claim | 1 GPU-day maximum |
| Feasibility pilot: 40 tasks × 6 models × 2 primary policies × 1 seed | 480 | 2 / 5 / 10 | 16 / 40 / 80 GPU-hours |
| 250-task full eight-policy design × 6 models × 3 seeds | 36,000 | 2 / 5 / 10 | 1,200 / 3,000 / 6,000 GPU-hours |
| 400-task full eight-policy design × 6 models × 3 seeds | 57,600 | 2 / 5 / 10 | 1,920 / 4,800 / 9,600 GPU-hours |

These hypothetical 2/5/10-minute cells are **not estimated actual
U-CODE runtime**, and omit model loading, download, retries, system
setup, CPU evaluator latency, errors, orchestration and warmup.
For genuine repository-level agents, individual assignments can
be much longer. Conversely batching/KV reuse can increase
throughput after independent budget fairness and reproducibility
are verified. Do not convert the table to a promised completion date.

**Spending recommendation:** cap the first A100 checkout at
**12–24 hours** (¥96–¥192 at ¥8/hour) for six-model load, token,
VRAM, and small synthetic pipeline preflight only; suspend the
instance between blocks if the provider allows it. After all
access, task and metering gates pass, reserve another short
24–72-hour run and decide subsequent rental from actual throughput.
An unqualified 250–400-task × 8-policy × 3-seed full campaign
is **not a 3–7-day job on one A100** under these example timings.

**Calendar work is distinct from paid GPU-days:** implementation
of safe inference adapters, license checks, task admission, sealed
evaluators and scientific review can span weeks even when the
model-load preflight fits into one day. The external journal
submission deadline is a planning target, not proof the work can
finish or be accepted by then.

## Verified technical references

- [Mistral official offline Devstral deployment guide](https://docs.mistral.ai/vibe/code/cli/offline-models)
  lists **H100 or A100** for Devstral Small 2 FP8 deployment.
- [vLLM FP8 guide](https://docs.vllm.ai/en/latest/features/quantization/fp8/)
  distinguishes native Hopper W8A8 kernels from Ampere W8A16
  FP8 weight-only Marlin support.
- [AI Galaxy public offers](https://www.ai-galaxy.cn/) show
  the A100 80GB promotion at ¥8/hour, but real
  instance specifications and rates require checkout verification.

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
