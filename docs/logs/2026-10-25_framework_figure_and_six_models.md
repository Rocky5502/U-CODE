# U-CODE execution checkpoint — framework figure and all six selected models

**Date:** 2026-10-25. **Starting GitHub main:** 7bb0b21e8a0ef4db129e6e16ad10e793c5782819 (219 passing offline tests). **Requested:** publish the official framework image in README and keep progressing on all previously recommended LLMs.

## Completed and directly committed

1. Created [docs/figures/ucode-framework.svg](../../docs/figures/ucode-framework.svg), an original **publication-oriented, resolution-independent SVG**. Main policy arrow chain is stage 1 → 2 → 3 → 4 → 5 → 6, with a distinct return arrow from execution stage 5 to BES stage 4. The lower lane has task admission → independent sealed evaluator → metrics → outputs, an intake from stage 1 and a **terminal patch only** route from stage 6 into the evaluator. The diagram is a proposed architecture, not a completed experimental result. The author-requested oversized title and explanatory bottom paragraph are absent.
2. Embedded the SVG near the top of [README](../../README.md). Added semantic IDs to all 11 directed arrows (five policy, three lower research, one feedback, two cross-lane). [Arrow geometry validator](../../scripts/validate_framework_figure.py) checks XML, named stages, directional coordinates, routing, accessibility and absence of embedded scripts; [five first-party tests](../../tests/test_framework_figure.py) include reversed-arrow and wrong-oracle-route rejection.
3. Read and reconciled the official Hugging Face public model metadata for **all six v2 proposals**: Qwen2.5-Coder-7B-Instruct, Qwen3-Coder-30B-A3B-Instruct, Devstral Small 2 24B, DeepSeek-Coder-V2-Lite, CodeGemma 1.1 7B, and Llama 3.1 8B.
4. [configs/accepted_six_model_study_2026-10-25.json](../../configs/accepted_six_model_study_2026-10-25.json) records the researcher's **explicit approval to include all six in the planned matrix**; it does NOT claim checkpoint or tokenizer pinning, model-license acceptance, gated weight access, GPU feasibility, weights downloaded, or inference execution. These six checkpoints span **five publisher families** because both Qwen checkpoints are from Qwen.
5. [Six-model research protocol](../SIX_MODEL_STUDY_PLAN_2026-10-25.md) records the full six-model table, source cards and memory/licensing caveats. Large Qwen3/Devstral and gated Gemma/Llama models are **not silently excluded**, but cannot be called executable until relevant resource/rights gates pass.
6. [src/ucode/model_readiness.py](../../src/ucode/model_readiness.py) validates exact model identity/official card-license mapping, 40-hex model/tokenizer revisions, frozen chat-template SHA256, license review, gated terms, inference engine/version, precision, measured GPU peak, verified weights and sandbox review. The gate refuses calling an incomplete subset the six-model run and blocks any false license relabeling; [model preflight unit tests](../../tests/test_model_readiness.py).
7. Updated the Springer [manuscript source](../../paper/overleaf/main.tex) with an **explicitly prospective** six-checkpoint study protocol and all reproducibility/permissions prerequisites. Added [three integrity tests](../../tests/test_model_study_paper.py), checking all model names, manuscript caveats and README image.
8. GitHub Actions now executes figure-flow validator and model-readiness report on both Python 3.10 and Python 3.12, in addition to all existing offline unit tests and Overleaf ZIP source-only export.

## Verification status and constraints

Before final logger commit, the 237-test run [40112539318](https://github.com/Rocky5502/U-CODE/actions/runs/40112539318) passed on Python 3.10 and 3.12, including figure and model preflight steps. Then three model/manuscript tests and a restricted-license guard test were added; final expected suite **241 offline unit tests**, subject to checking a final post-commit run's actual conclusion and log.

**No externally sourced untrusted code was executed.** No model weights or gated datasets were downloaded, no user-provider terms accepted through this interaction, no GPU rental/paid resources or inference invoked. Root README SVG is real and committed; the imagegen PNG from the chat was *not* uploaded binary. A scalable freshly authored SVG is the versioned camera-ready figure.

There is still no direct authenticated Overleaf editing connection; GitHub manuscript sources and Actions-generated `ucode-overleaf-sources` ZIP are canonical. The figure SVG is intended for README. Before using it in official pdfLaTeX publisher template it must be exported to supported PDF/PNG and visually inspected in compiled page; the current CI tests SVG geometry/logic, not publisher compilation.

## Honest scientific next gates

- Preserve all six model identities as selected for study planning. Independently verify current model/tokenizer commit IDs, provider licenses and gated terms, actual runtime security, weights and VRAM use. Do **not** claim complete six-model experiment until every report is filled.
- Complete source attribution and rights/oracle qualification for at least one executable repository task in an audited disposable, non-root, network-disabled sandbox, then run a true pilot; ordinary GitHub CI must remain metadata/unit-test only.
- Fit separate patch-prior risk and diagnostic likelihoods on disjoint repository/fork training groups; withhold hidden oracle. Compare conditional and independence BES, uncertainty-free search, fixed testing, selective verification, and MCTS/reuse under identical measured vector budgets.
- Replace prospective manuscript Results only with independently reproduced metrics and confidence intervals. The current scientific readiness remains far below submission without genuine experiments.

**User-selected means accepted for PLANNING, not approved for unattended model execution or spending.**
