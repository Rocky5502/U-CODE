# U-CODE

**Uncertainty-Guided Search for Reliable AI-Generated Software**

[![Offline tests](https://github.com/Rocky5502/U-CODE/actions/workflows/ci.yml/badge.svg)](https://github.com/Rocky5502/U-CODE/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/original%20U--CODE%20code-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12-3776AB)](pyproject.toml)
[![Study status](https://img.shields.io/badge/study-prospective%20%2F%20no%20real%20outcomes-555)](docs/RESEARCH_PROTOCOL.md)

> **Research prototype — not a validated repair agent.** U-CODE studies whether an LLM coding agent should **generate/repair another candidate** or **acquire additional correlated evidence** about candidates, then **release or abstain**, under independently constrained resources. No measured real-task U-CODE improvement, task admission, risk guarantee or six-model benchmark is claimed.

**Target venue:** Springer *Automated Software Engineering*, special issue
[Search-Based Software Engineering in the Era of LLMs and Agentic Systems](https://link.springer.com/collections/jjcfecffai)
(submission deadline **30 January 2027**, subject to publisher updates).

**Research handoff:** [V4 canonical scientific handoff](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md) ·
[Scientific blockers](configs/ucode_work_remaining_gates_2026-10-27.json) ·
[Springer source-era/novelty audit](docs/SPRINGER_V4_SOURCE_ERA_AND_NOVELTY_AUDIT_2026-10-29.md).

## At a glance

| Area | Source-verified scope (29 October 2026) | Important limit |
|---|---|---|
| Discovery | **120** distinct PR/repository-name leads; **119** retrieved metadata records | Not 120 runnable repositories |
| Language coverage | **12 search-language strata** | Actual changed-code language remains to be independently qualified |
| Screening | **62** production-source-path leads; **12** prioritized manual-review leads | Not 62 or 12 approved executable tasks |
| Real evaluation | **0** independently admitted executable tasks; **0** sealed functional oracles | Correctness, calibrated risk and causal effectiveness all **N/A** |
| Models | **6** selected open-weight model IDs | No weights/revisions/runtime/terms fully verified for this project |
| Policies | **8** preregistered arms | Only restricted first-party synthetic references, not eight faithful real runs |
| Runner | OCI launch-command **dry-run** and accounting interfaces | No independently attested isolation or five-resource physical meters |
| Offline tests | Python **3.10 / 3.12** GitHub Actions | First-party checks, not third-party software executions |

The two source-era PHP/Go pilot dossiers have **16/16 gates currently PENDING**;
neither candidate is an admitted executable task. Independent source-era
specification, rights, sealed oracle and sandbox evidence are still required.

The last pre-refactor `main` CI was green with 1,142 offline tests per Python version. **Always inspect the current [CI](https://github.com/Rocky5502/U-CODE/actions)** for the latest count, SHA and outcome.

## Framework

![U-CODE framework: risk-aware policy loop, evidence acquisition and isolated evaluator lane](docs/figures/ucode-framework.svg)

*Figure 1. Architectural design, not a completed or validated experimental result.* The evaluator-only oracle must never be passed to the policy, model prompts, retrieval context or uncertainty estimators.

The primary confirmatory comparison is **conditional evidence-search U-CODE vs equal-budget no-uncertainty search**, keeping the task/model/seed/public proposal opportunities and all five caps matched (tokens, test calls, GPU seconds, CPU seconds, wall seconds). Other registered arms include unconditional evidence search, uncertainty-only, fixed testing, selective verification, MCTS and replay-based search; implementation fidelity is not yet established.

## Quickstart: safe, offline, first-party checks

Python **3.10 or 3.12** is used in CI. From a cloned repository:

```bash
git clone https://github.com/Rocky5502/U-CODE.git
cd U-CODE
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.check_local_readiness
```

The default package has **no third-party runtime Python dependencies**.
`requirements.txt` installs this package in editable mode; optional model
engines, PyTorch, Docker/Podman, GPU drivers, benchmark toolchains and upstream
datasets are **not** silently installed. Do not run external repositories on
the host or GitHub Actions. Local inference is an **explicit, separately
reviewed** step after the [local experiment gates](docs/LOCAL_EXPERIMENTS.md).

Useful reproducible, *offline metadata-only* commands:

```bash
python -m scripts.validate_sbse_protocol
python -m scripts.audit_six_model_crosswalk
python -m scripts.audit_dataset_quality --output-dir dist/ucode-pr-metadata-clean
python -m scripts.verify_dataset_release dist/ucode-pr-metadata-clean
python -m scripts.export_research_readiness --output-dir dist/ucode-research-readiness
python -m scripts.audit_overleaf_sources
```

These checks never download model weights or run third-party source code. Generated
outputs stay under ignored `dist/` paths.

## Model and dataset registry

The **authoritative, immutable-for-planning six-model roster** is
[`configs/accepted_six_model_study_2026-10-25.json`](configs/accepted_six_model_study_2026-10-25.json).
The prospective study contract is
[`configs/confirmatory_sbse_protocol_2026-10-25.json`](configs/confirmatory_sbse_protocol_2026-10-25.json).
The [six-model A100 planning profile](configs/ai_galaxy_six_model_deployment_2026-10-27.json)
is **configuration only**; it does not approve rental or claim compatibility.

**[Model matrix and per-model restrictions](docs/MODELS.md)** documents all six
Hugging Face IDs, advertised card licenses (not approved rights), tokenizer
and checkpoint freeze requirements, quantization/runtime caveats, and
hardware-dependent decisions.

**[Dataset catalog and readiness](docs/DATASETS.md)** distinguishes the
source-audited 120-PR metadata pool from the **13 external candidate sources**
in the V2 registry and from any independently executable task cohort.
[Curated dataset provenance](data/curated/README.md) explains the SHA-checked
eight-file metadata release. No external dataset weights, code trees, hidden
tests or model outputs are stored in this repository.

## Repository map

| Path | Purpose |
|---|---|
| `src/ucode/` | Formal search, reference controllers, provenance, policy/evaluator boundary and audit code |
| `configs/` | Frozen prospective study contract, selected model IDs, restricted deployment/experiment planning |
| `data/discovery/` | Source URLs, search leads and dataset candidate registries |
| `data/audits/` and `data/curated/` | Reproducible, source-free PR metadata and quality checks |
| `data/admission/` and `data/evaluation/` | **Pending**, evaluator-separated review metadata; never public hidden gold |
| `scripts/` | Offline validations, exports, readiness and synthetic smoke tests |
| `tests/` | Adversarial first-party offline unit tests (no untrusted source builds) |
| `paper/overleaf/` | Prospective Springer LaTeX and bibliography; not a verified compiled PDF |
| `docs/` | [Research handoff](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md), [experiment preparation](docs/LOCAL_EXPERIMENTS.md), [data rights](docs/DATA_GOVERNANCE.md), [scientific protocol](docs/RESEARCH_PROTOCOL.md) |
| `docs/README_RESEARCH_LOG_THROUGH_2026-10-29.md` | Complete preserved historical development log; dated snapshots not current eligibility |

## Scientific integrity, security and attribution

- **No fabricated accuracy:** neither a passing synthetic test nor a merged
  upstream PR is independent functional correctness evidence. The 120/120 links attempted, 119/120 PRs retrieved
  metadata screen yielded **zero fully eligible executable tasks**.
- **No oracle leakage:** post-fix patches, private labels and independently
  sealed evaluator fixtures never enter prompts or public policy observations.
- **No unsafe execution:** discovered repositories must first pass source rights,
  independent task admission, rootless/disposable network-off sandbox validation,
  and real five-resource enforcement. The present repo does not offer that runner.
- **No implicit rights:** MIT applies to **original U-CODE source** only. External
  repositories, datasets and model weights retain their own licenses and gated terms.
  See [LICENSE](LICENSE), [SECURITY.md](SECURITY.md),
  [model licenses](docs/MODELS.md), [data governance](docs/DATA_GOVERNANCE.md).
- **No unverified generalization:** naturalistic agent-attributed PR metadata,
  controlled model-generated patches, issue-repair datasets and attribution
  snippets are **distinct cohorts**; never pool them without an explicit design.

**Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md) · **Security reports:** [SECURITY.md](SECURITY.md) ·
**Original project license:** [MIT](LICENSE) · **Citation:** [CITATION.cff](CITATION.cff) ·
**Canonical Springer manuscript:** [main.tex](paper/overleaf/main.tex).
