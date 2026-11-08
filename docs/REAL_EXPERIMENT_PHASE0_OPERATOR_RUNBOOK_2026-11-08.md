# U-CODE — Phase-0 operator runbook before the first REAL experiment
**8 November 2026 · Source-verified protocol; no GPU/model/third-party repository executed by this update**

## Executive decision

The repository currently has a successful first-party CI suite but **zero independently admitted executable research tasks, zero independently sealed real functional oracles, zero qualified six-model inference checkpoints, and zero measured eight-policy comparisons**. This is an explicit pre-experiment status, not a failure of the offline research implementation.

The first **real** measurements should be staged in two separate streams. **Stream A** can start on the user's own machines after deliberate human approval of each model's license: non-sensitive host hardware inspection, model checksum and tokenizer provenance, and *first-party synthetic model load/latency smoke*, with no real task or hidden oracle. **Stream B** needs an independent historical PHP/Go specification/rights review, isolated evaluator-only oracle and secure metered runner. Only after the streams meet can real source-task evaluation begin.

The **primary preregistered contrast remains** `ucode_conditional_bes` vs `no_uncertainty_search`, with all eight policies and all six exact models preserved for the eventual confirmatory design. Do not substitute a synthetic success indicator for a real outcome.

## 1. Command now: inspect phase-0 readiness without spending or downloading

From a trusted local checkout of `Rocky5502/U-CODE`:

```bash
python -m scripts.prepare_real_experiment_phase0
python -m scripts.prepare_real_experiment_phase0 --hypothetical-tasks 1 --hypothetical-seeds 3
python -m scripts.prepare_real_experiment_phase0 --require-real-ready
# The last command MUST exit 2 until separately authorized workflow exists.
```

The script checks the authoritative `configs/confirmatory_sbse_protocol_2026-10-25.json`, selected six-model inventory, local (blocked) preflight, 13 dataset source leads and the PHP #104/Go #43 pilot dossier. It refuses drifts in the model/policy roster, fake approvals, promoted experiment outcomes, the missing six-model checkpoint qualification or the wrong five-component budget. It does **not** silently make the frozen `seeds_frozen=false` or `final_budget_caps_frozen=false` into true statements.

This is a strict preparation command. No GitHub-network, model-weight download, untrusted module import, Docker invocation, model generation, hidden gold, task checkout, GPU allocation, third-party code, or reservation occurs.

## 1a. Read-only six-model public metadata and BF16 storage audit (9 November 2026)

The [new six-model public Hub-card audit](P0_3_PUBLIC_SIX_MODEL_CARD_AUDIT_2026-11-09.md) records public license tags, gated card status and **approximate** BF16 weight storage only, with the exact six planned IDs unchanged. The DeepSeek public Hub tag is other while the historical frozen planning record says deepseek-license: a human must review the actual license text rather than assuming one label supersedes the other. CodeGemma and Meta Llama are publicly gated; user/account access remains unknown. Three model families' rough BF16 weights exceed an illustrative 16 GiB card, while **under** 16 GiB does not imply load feasibility. Nothing was downloaded or executed.

    python -m scripts.audit_six_public_model_cards
    python -m scripts.audit_six_public_model_cards --require-six-ready
    # This intentionally exits 2, preserving zero approved real-model checkpoints.

## 1b. Optional six-model HEAD SHA metadata capture — *no model downloads*

See [the source-pinned model SHA workflow](P0_3_HF_SHA_REVISION_CANDIDATES_2026-11-09.md). Its CLI defaults to offline six-model PENDING rows; only an explicit operator switch makes six fixed HTTPS requests for public model **metadata only**:

    python -m scripts.capture_public_hf_sha_candidates
    python -m scripts.capture_public_hf_sha_candidates --capture-public-heads --output /private-study-metadata/public_hub_heads.json
    python -m scripts.capture_public_hf_sha_candidates --require-approved
    # The final command must exit 2 regardless of candidate SHAs.

A fetched 40-hex SHA names an *observed mutable main-branch target*, not a reviewed, fixed, downloaded or runnable checkpoint. The full model weights, per-file hashes, tokenizer/chat-template, full license and account terms, runtime and actual peak VRAM still require explicit independent approval. GitHub CI **never** uses the network capture flag.

## 2. Command on user's own Windows/WSL Linux or rented A100 host

Optional *read-only* host survey:

```bash
python -m scripts.prepare_real_experiment_phase0 --probe-gpu
```

This uses the fixed command

```text
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
```

It reports **locally declared** GPU names, VRAM MiB, driver versions, *nothing else*. Missing `nvidia-smi` is reported as unavailable, not an exception that certifies a CPU host. No weight files, private repositories, UUIDs, model prompts, device serials, hostname, credentials or private evaluator information are collected. The probe cannot prove actual rootlessness, cache safety, memory availability, CUDA compatibility or five-resource enforcement and **does not start a model**. Do not commit raw machine receipts, secrets or private reviewer results.

The existing planned hardware for the *full BF16 six-model study* is **one A100 80 GB sequentially**, not six concurrent GPUs. A 16 GB local card may be useful for lightweight engine/client tests but must not be silently recorded as a measured proof that all six exact checkpoints load at full intended precision. Before renting any A100, verify actual available VRAM, driver, host RAM, disk, model licenses and estimated cost.

## 3. Hypothetical capacity envelope — NOT actual running time, outcome or expense

The registered October protocol contains an **illustrative** vector *per policy arm*: 30,000 tokens, 20 test calls, 3,600 GPU seconds, 1,800 CPU seconds and 3,600 wall seconds. These are **not yet the final approved or enforced caps**, and tokens, GPU seconds, CPU seconds and wall seconds are different units and not substitutable. The user needs a separately approved budget and independent metering.

| Hypothetical scenario, **one future task** | Model × policy × seed slots | Tokens envelope | Test-call envelope | GPU-seconds envelope | CPU-seconds envelope | Per-arm wall-seconds envelope summed across slots |
|---|---:|---:|---:|---:|---:|---:|
| One illustrative seed | 6 × 8 × 1 = **48** | 1,440,000 | 960 | 172,800 (48 GPU-hours) | 86,400 (24 CPU-hours) | 172,800 |
| Three illustrative seeds | 6 × 8 × 3 = **144** | 4,320,000 | 2,880 | 518,400 (144 GPU-hours) | 259,200 (72 CPU-hours) | 518,400 |

These are arithmetic sums of *illustrative per-run ceilings*, **not predicted usage or elapsed experiment duration**. Parallelism and GPU rental logistics require separate planning; CPU/GPU measurements may overlap. There are **zero** admitted task slots today. This capacity what-if is expressly not a configured experiment, signed protocol or spending authorization. The exact seed values 11, 29, 47 are example-only.

## 4. Real execution activation sequence: two streams, no shortcuts

| Gate | Owner and evidence needed | Allowed next action |
|---|---|---|
| **A0. Host inventory** | Local operator: sanitized GPU/driver/memory; no model access | Read-only `--probe-gpu` |
| **A1. Model terms and pins** | Model owner: all six licenses/terms, gate access when applicable; immutable checkpoint and tokenizer revisions, chat templates, engine/precision/quantization | After rights approval: first-party local model-load canary, one model at a time; no historical GitHub task yet |
| **A2. Actual model smoke** | Systems operator: recorded actual peak VRAM and prefill/decode, exact engine/container image digest, output tokenizer count; independently audited if used for scientific inference | Record reproducible machine-level readiness evidence privately |
| **B1. Task provenance and scope** | Independent domain/spec reviewer: Go #43 six normative ambiguities or PHP #104 historical specification; signed task-era source precedence, declared microtask scope | Authorize a **specific** pre-fix task for later evaluator construction, not all of PR |
| **B2. Rights and test oracle** | Independently responsible file rights reviewer and evaluator: source/file use, independent pre-outcome gold oracle sealed outside policy repo | No policy-visible post-fix tests, gold labels or original patches |
| **B3. Secure execution** | Security/operations reviewers: real rootless network-off sandbox on dedicated host, pinned dependencies, actual enforced five-resource caps, signed operation receipts | Authorize isolated third-party execution **only through that runner**, never this phase-0 script |
| **C1. Exploratory matched pilot** | After A1–A2/B1–B3: separately approved 1 task × 1 compatible model × 2 policies × 1 seed with identical tool access, candidate proposals and nominal caps | Collect true released patch and independent evaluator verdict; **not** the final six-by-eight claim |
| **C2. Confirmatory expansion** | Independently qualified lineage-disjoint task cohorts, calibrated forecasts and full eight-arm fidelity, six checkpoints and frozen settings | Run *all assigned* task/model/policy/seed/budget cells; include abstention/timeouts; report matched ITT effects |

**Do not mark C1 or C2 complete just because an offline CI smoke test passed.** The current `ShadowMatrix` only verifies eight policy *wiring slots* with synthetic callbacks, not that eight independent research methods have been faithfully implemented and benchmarked.

## 5. What must be recorded BEFORE the first real benchmark task

An independently governed experiment record should freeze: the exact pre-fix task and lineage, independent use-rights decision, approved task instructions, public-only policy view, held-out test oracle commitment in **another evaluator-only store**, environment/container digest, model weight/tokenizer/chat-template revisions, engine and precision, actual hardware, time/seed, eight-policy comparator implementation versions, matched proposals/action IDs, and **five separately enforced** token/test/GPU/CPU/wall caps. Role-separated signatures must be authenticated outside source-control code.

The complete run ledger must include assigned arms even if they abstain, time out, are killed for budget overrun, or encounter infrastructure errors. Release correctness is assessed only by the independently sealed evaluator **after** policy termination. Wrong-release risk is undefined when no patch was released; absent results are N/A rather than an estimated 0% or a new calibration threshold.

## 6. Canonical artifacts and current blockers

- [Real phase-0 readiness implementation](../src/ucode/real_trial_phase0.py), [read-only operator CLI](../scripts/prepare_real_experiment_phase0.py), and [first-party adversarial tests](../tests/test_real_trial_phase0.py).
- [Go §3.2 contradictions/authority handoff](G5_GO43_SPEC_FEASIBILITY_DECISION_PACKET_2026-11-08.md) and [private independent Go rule-review workflow](G5_GO43_PRIVATE_RULE_ADJUDICATION_PROTOCOL_2026-11-08.md). These are prospective, not human-approved oracle outputs.
- [External pilot admission contract](G5_M4_REAL_PILOT_ACTIVATION_2026-11-06.md), [OCI dry-run contract](OCI_SANDBOX_LAUNCH_PREFLIGHT_2026-10-29.md), [local preflight](../configs/local_experiment_preflight_2026-10-29.json), [six-model A100 deployment plan](AI_GALAXY_SIX_MODEL_RENTAL_PLAN_2026-10-27.md), and [master V5 handoff](UCODE_NEW_CHAT_MASTER_HANDOFF_V5_2026-11-07.md).
- **Still blocked:** Go 8/8 + PHP 8/8 pending admission evidence; zero independently sealed golds; zero model checkpoints certified for the full study; eight faithful policy adapters not verified; no actual measurement.
- CI must run **without** `--probe-gpu`: GitHub-hosted GPU/driver observations would say nothing about the user's Windows workstation or A100 rental. The optional local machine command is the ONLY hardware action in this phase-0 tool. No live Overleaf cloud sync or compiled publisher PDF is claimed.

## 7. Concrete highest-value next human action

Arrange the **independent, private Go #43 domain review** of the six source-era questions (including conservation/low-balance, fractional multiplier and business-rule precedence); do not send these completed responses into the public repo or agent context. In parallel, run the read-only GPU survey on the intended Windows/WSL or A100 host, and confirm the model licenses, exact revisions and engine versions. If Go's original intended rules remain unrecoverable, reject that microtask and advance a new source-era eligible candidate rather than guessing the answers. Only then allocate compute for the first measured matched pilot.
