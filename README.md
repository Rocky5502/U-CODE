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

## Novelty candidate: model-coherent evidence acquisition (30 October 2026)

We added a new **two-level Bayesian diagnostic search reference** that
models uncertainty about a patch's correctness **and** uncertainty about
which frozen evidence-reliability model is generating the test results.
Its joint posterior is updated only through visible diagnostic outcomes;
the same hidden model identity persists across all observations. The
planner allocates tests/retrieval/static analysis under the existing
five hard resource caps and supports pooled-risk or all-surviving-model
release gates.

An [independent rational mathematical audit](docs/COHERENT_HYPOTHESIS_EVIDENCE_SEARCH_NOVELTY_2026-10-30.md)
includes a counterexample: a perfect-versus-inverted diagnostic appears
valuable when each hypothetical reliability model is treated as known,
but cannot help at one step when its meaning is truly unknown. A
calibration-then-diagnostic sequence has stipulated two-step net value
**0.48**. Twenty additional exact-rational configurations and
adversarial code tests check the restricted method.

**Scope:** first-party synthetic algorithm only; not a fitted model,
newly established theorem, real-task experiment, or measured software
repair improvement. The original six RQs and eight planned policy arms
are unchanged until a separate prospective protocol revision.

```bash
python -m unittest discover -s tests -p 'test_coherent_hypothesis_search.py' -v
```

## First real-task provenance gate: pinned Go source-era specification file (30 October 2026)

The [source-era Go #43 document binding audit](docs/GO43_PRE_FIX_DOCUMENT_GIT_TREE_BINDING_2026-10-30.md)
now cross-checks the registered pre-fix design document against the
actual immutable Git base-tree entry observed through read-only GitHub
metadata. It requires the exact `docs/design.md` path, base commit, Git
tree, blob SHA, regular-file mode and file size; wrong document links
or plausible-looking but unrelated SHA40 values fail the evaluator
registration audit. The historical PHP #104 issue remains quarantined:
its current body is not a frozen historical pre-PR specification.

This closes an important *source-identity* control gap without
promoting either lead to experiment eligibility. File-level rights,
independent behavior review, sealed tests, authenticated sandbox and
five-resource enforcement are still absent; **qualified tasks remain 0**.

```bash
python -m scripts.check_evaluator_boundary
python -m unittest discover -s tests -p 'test_pre_fix_spec_binding.py' -v
```

## Whole-archive Bellman search: independent mathematical cross-validation (30 October 2026)

A new [exact-rational joint-search audit](docs/INDEPENDENT_JOINT_BELLMAN_RATIONAL_AUDIT_2026-10-30.md)
compares both finite-horizon, candidate-aware Bayesian controllers against
an independent `fractions.Fraction` reference enumerator. The standalone
reference enumerates latent candidate-truth vectors and every binary
diagnostic outcome without calling either planner's Bayes updater or
terminal-value helper. It checks **205 authored mathematical model
configurations**: 144 independent candidate-prior configurations, 36
correlated-prior configurations, one zero-probability edge case, and
24 mixed generation/verification cases with optional incumbent release.

The tests target globally single-use diagnostics, exact branchwise
posterior value, generation failure, surviving archived candidates and
correct placement of action costs. **These are synthetic calculations,
not 205 approved repository tasks or measured LLM performance**. The
paper's Methods describe the checks, with no claim of real effectiveness.

## Training-only Bayesian diagnostics: lineage-support and hash hardening (29 October 2026)

A [new scientific validity audit](docs/CLASS_CONDITIONAL_LINEAGE_SUPPORT_AUDIT_2026-10-29.md)
closes a gap in the diagnostic likelihood estimators. Requiring two
repository/fork lineages *overall* cannot establish class-specific support
when one source group supplies only acceptable cases and another only
unacceptable ones. The conditional estimator now checks **at least
two training lineages per class per observed action/history cell**;
the unconditional estimator applies the same principle per
correctness class. Sparse or source-confounded estimates fail closed.

Both fitters also use versioned structured input fingerprints instead
of ambiguous delimiter-concatenated identifiers. The source-only
regressions and proposed Springer Methods are updated. **These changes
do not establish empirical calibration or real model correctness**;
independent task admission and held-out lineage validation remain blocked.

## Corrected archive-conditional Bayesian value of information (29 October 2026)

The [incumbent-preserving Bellman audit](docs/CONDITIONAL_ARCHIVE_INCUMBENT_BELLMAN_FIX_2026-10-29.md)
fixes a **scientific planning bug**: the conditional archive had
computed `max(E[posterior patch utility], other-patch utility)` rather
than preserving the best unchanged archive candidate at **each
diagnostic outcome**. It now computes the correct
`E[max(posterior patch utility, other-patch utility)]`
under the finite per-patch kernel assumptions. A separate exact-rational
oracle checks 1,152 hypothetical one-step cases, alongside tested
positive/negative release-branch outcomes and five-resource budgets.
The prospective manuscript Method section now discloses this fix.

An illustrative **synthetic** two-candidate counterexample has
stop utility `0.84` and corrected expected diagnostic value `0.91`.
These are **not model inference or real code-repair results** and do
not support a performance claim.

## First prospective task contract and evaluator-boundary hardening (29 October 2026)

The [new prospective PHP #104 review contract](docs/NEW_PROSPECTIVE_PHP_TASK_BOUNDARY_AUDIT_2026-10-29.md)
is now separately identified from the **unverified historical PR task**.
Its proposal is linked to the original base-source Git blob inventory,
but it has **no independent reviewer approval, private oracle, license
clearance, isolated runner or experimental authorization**. CI validates
the public source crosswalk and rejects fabricated approval fields.
We also fixed cross-repository GitHub issue-reference substitution and
unsafe Unicode control characters in policy-visible task views.

```bash
python -m scripts.validate_php104_prospective_draft
```

## Executable first-party repair canary (29 October 2026)

The [first-party executable canary and real-task admission report](docs/FIRST_PARTY_EXECUTABLE_CANARY_AND_REAL_TASK_GATE_2026-10-29.md)
now exercises **actual trusted Python code** for two frozen public repair
alternatives. The intentionally faulty fixture passes **4/7** and the
corrected fixture **7/7** public cases; an independent seal, real
repository task, LLM run and physically isolated sandbox are **not**
claimed. The first-party subprocess smoke runs in CI.

```bash
python -m scripts.smoke_first_party_executable_canary
```

An optional [operator-only local rootless Docker probe](scripts/probe_local_oci_first_party.py)
can validate a pre-reviewed, locally cached digest-pinned image with a
fixed first-party print fixture. It is **not** called by CI; it cannot
execute external repository tasks or grant real-study approval.

## Ten senior SE/AI research perspective audit (29 October 2026)

The [ten-perspective source-code audit](docs/TEN_SENIOR_SE_AI_CODE_REVIEW_2026-10-29.md)
documents concrete fixes to fork-lineage statistical grouping, metadata
source validation, scalar-cost overflow and tiny-resource ledger reconciliation.
It also distinguishes unimplemented experimental infrastructure from
first-party passing tests. These are ten analytical disciplinary reviews,
**not ten independent human researchers or proof of real-task performance**.

## Independent mathematical and 1,000-perspective review (29 October 2026)

The [new source-grounded research audit](docs/RESEARCH_1000_PERSPECTIVE_MATH_DATA_AUDIT_2026-10-29.md)
provides an independent exact-rational cross-check of Bayesian posterior,
bounded two-step evidence search and infrastructure-missingness equations;
a strict 120-PR/13-source dataset crosswalk; and a repair to malformed
Springer citation syntax. Its [1,000-perspective review register](scripts/export_1000_research_lenses.py)
is **20 scientific domains × 10 risks × 5 review roles**, all **PENDING**:
it does not claim a thousand independent reviewers or completed experiments.

```bash
python -m scripts.audit_dataset_cohort_crosswalk
python -m scripts.export_1000_research_lenses
python -m scripts.audit_overleaf_sources
python -m unittest discover -s tests -v
```

All math and dataset checks are **source-only/synthetic** and leave the
first real executable task admission and hidden oracle **blocked**.

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
