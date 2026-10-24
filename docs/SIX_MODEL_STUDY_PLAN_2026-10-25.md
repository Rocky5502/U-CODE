# U-CODE: all six accepted LLMs — experiment readiness protocol

**Date:** 2026-10-25. **Decision:** all six model recommendations from the v2 shortlist are **accepted by the researcher for planned inclusion**. This decision is not model-provider license acceptance, account authorization, a frozen checkpoint, successful inference or a computed experimental result.

The canonical machine-readable selection is [accepted_six_model_study_2026-10-25.json](../configs/accepted_six_model_study_2026-10-25.json), and the original [v2 candidate inventory](../configs/models_v2_2026-10-24.json) and [legacy v1 plan](../configs/models.json) remain unchanged.

## Six-model panel

| Model ID | Publisher | Primary scientific role | Card license | Execution constraint |
|---|---|---|---|---|
| [Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) | Qwen | Small coding specialist and local feasibility anchor | Apache-2.0 | Verify revision, complete license and 16-GB VRAM quantized runtime |
| [Qwen/Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) | Qwen | Stronger coder, mixture-of-experts scaling | Apache-2.0 | About 30B **total** parameters: 3B active does not mean 3B stored. Validate high-memory runtime/offload |
| [mistralai/Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512) | Mistral | Repository agent/tool-use specialization | Apache-2.0 | Verify correct Mistral3 backend, weight format and larger-memory needs |
| [deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) | DeepSeek | Cross-publisher code specialist | DeepSeek Model License | Full model license review; any custom-code loader requires security review |
| [google/codegemma-1.1-7b-it](https://huggingface.co/google/codegemma-1.1-7b-it) | Google | Smaller distinct code-specific baseline | Gemma license | Provider terms acceptance/access and runtime verification required |
| [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) | Meta | General instruct baseline | Llama 3.1 community license | Provider terms acceptance/access, license review and runtime verification |

**Scientific counting:** six selected models represent **five publisher families**, because the Qwen2.5-Coder and Qwen3-Coder checkpoints are not independent publishers. Model independence cannot be claimed solely from model count.

## Readiness is strictly distinct from research consent

All six are included in the prospective model panel. **Zero** are marked reproducibly runnable. The explicit [preflight](../src/ucode/model_readiness.py) requires, for every model:

1. Immutable 40-hex model and tokenizer snapshot revision identifiers, model-card source identity, frozen chat-template hash and model-family identity.
2. Complete provider/model license review and required Hugging Face access/terms verification; public model metadata does not itself grant gated access.
3. Pinned inference engine+version and quantization or precision setting; runtime-specific loading and untrusted custom modeling code must undergo security review.
4. Verified model weight integrity and actual peak VRAM measurements; do not infer hardware fit from activated mixture-of-expert parameter counts.
5. Independent sandbox safety review, **plus** rights-cleared source tasks and an evaluator-only sealed correctness oracle before any results are interpreted.

The gate deliberately reports nonready models rather than silently dropping a larger or gated checkpoint and calling a subset a six-model experiment. A model ready for *inference* is not equivalent to a dataset/task ready for *scientific evaluation*.

## Execution staging without dropping the accepted models

**Phase A — metadata (completed):** source identity, published license tags, approximate model class and model study roles inspected. All six accepted for scientific planning. No model weights downloaded.

**Phase B — local feasibility (not run):** inspect revisions/terms and approved hardware environment; start with the smaller openly licensed coder anchor while preserving all six models. Record measured context, engine version, prompt template and peak VRAM. If 16 GB VRAM is insufficient, a model remains in the plan pending reviewed quantization/offload or explicitly authorized larger GPU; **do not silently substitute** a different checkpoint or model.

**Phase C — controlled pilot (not run):** after real tasks pass source/provenance/sandbox/oracle gates, freeze a budget-matched protocol; use a feasible subset for runtime estimation while reserving all six for the confirmatory matrix. Do not report subset-only results as six-model findings.

**Phase D — six-model comparison (not run):** on identically qualified task groups and preregistered budgets, run all six pinned models (or transparently report exclusions/failed environments rather than misleading complete-case statistics). For each record preserve model/tool revisions, seed, prompts, patch SHA, evidence provenance, all five resource costs, terminal action, hidden independent oracle result, and missing/aborted cases.

## Cost safeguards and scholarly transparency

No GPU rental, hosted inference, subscription, model download or gated dataset access has been authorized or executed by this planning work. A later real run may require separate approval for paid compute or third-party terms. Treat Qwen vs Qwen comparisons as correlated model-family evidence. Preregister primary endpoints on task-level independent correctness, release coverage and conditional wrong-release risk; use repository/fork grouping rather than pretending repeated seeds are independent data.

**Current scientific hold:** zero executable independently oracle-qualified tasks, zero frozen six-model checkpoint revisions, zero real inference runs, zero observed policy effect. The camera-ready [framework SVG](figures/ucode-framework.svg) is the **proposed** architecture, not proof of implemented model execution.

**Sources:** six official Hugging Face model cards linked individually above; checked October 25, 2026. These model cards show advertised metadata and distribution terms, not independent reproducibility audits.
