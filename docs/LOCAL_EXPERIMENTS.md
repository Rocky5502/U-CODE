# Local experiment preparation — safe offline-to-real gates

**Status: CONFIGURATION / PREFLIGHT ONLY; no real U-CODE benchmark may be claimed yet.**
This is a runbook for preparing user-controlled machines, not a command
to execute untrusted repositories or spend on hosted/rented GPUs.

## Stage 0 — independent local setup (safe today)

Use Python 3.10 or 3.12 and an isolated virtualenv:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.check_local_readiness
python -m scripts.audit_six_model_crosswalk
python -m scripts.validate_sbse_protocol
```

The standard-library-only installed package has **zero third-party runtime
requirements**. Neither `requirements.txt` nor `requirements-dev.txt`
installs PyTorch, vLLM, llama.cpp, Docker, a model or any dataset. The six
accepted model IDs are exactly in the canonical JSON; don't rewrite them
to match a locally cached model.

## Stage 1 — local hardware and runtime inventory (manual, no inference)

Record operating system/WSL release, CPU, RAM, disk free space, actual GPU
model/VRAM, driver, CUDA support, Python and PyTorch/engine version *if installed*.
Classify every checkpoint as `NOT_PINNED`, `LICENSE_PENDING`,
`NOT_LOADED`, or `PREFLIGHT_VERIFIED` based on facts, not aspiration.

For 16GB-class local hardware, *selected* 7B/8B weights may need
quantization and small contexts; **quantized feasibility is unverified**.
30B total-weight MoE, 24B and 15B-class checkpoints must not be
assumed to fit. The prospective A100 80GB plan remains separate and
requires approval, pinned checkpoints, security and measured preflight.

## Stage 2 — model admission (still blocked)

For each of the six selected models, capture the full commit SHAs for
weights/tokenizer, hash the instruction/chat template and shards, archive
terms authorization, independently audit custom code, and choose a frozen
runtime, quantization, context/sampling parameters, seed and one-model-only
port. See [model matrix](MODELS.md). Do not enable `trust_remote_code`
to make a failed load pass. No external inference or GPU rental is
authorized by this file.

## Stage 3 — independently admitted and sealed task

Require task-era immutable spec and base commit, independent source
rights and AI authorship review, an approved original/prospective cohort
label, no post-fix leakage, private independent oracle, and source-hash
verified build context. PHP #104 and Go #43 are currently **not admitted**.

## Stage 4 — isolated repository build/test, with an independent reviewer

Design, *separately* implement, inspect and test a disposable rootless
no-network execution runner with read-only pinned source and small
writable overlay, no host credentials, no privileged mount/daemon, and
measured hard caps on token/test/GPU/CPU/wall resources. The current
`oci_sandbox_preflight.py` is a **dry-run only**. Do not run discovered
PR code in GitHub Actions, on Windows host, or directly in WSL.

## Stage 5 — registered bounded feasibility pilot

Only after Stages 1–4, freeze task families, independent training/calibration
splits, exact model weight/config digests, eight-arm policy fidelity,
assigned task/model/seed/budget table, and actual five-resource caps.
First compare `ucode_conditional_bes` with `no_uncertainty_search`
on the same public opportunities and independent outcomes.

Publish assigned-cell success (ITT), release coverage, conditional
wrong-release risk (N/A if none released), resource use, missingness,
infra failures, timing, and repository-family confidence intervals.
Unsuccessful or abstained runs stay in denominators.

## Repeatable repository readiness check

`python -m scripts.check_local_readiness` prints a deterministic
**BLOCKED** readiness report from the committed prospective manifest
and explicit hard gates; it does not inspect the actual machine,
authenticate any external reviewer, download anything, or run tests.
A passing report validation means the *prepared configuration* is
internally consistent, **not that the experiment is authorized**.

See [SECURITY](../SECURITY.md), [dataset catalog](DATASETS.md),
[protocol](../configs/confirmatory_sbse_protocol_2026-10-25.json).
