# U-CODE

> **NEW CHAT / AUTHORITATIVE HANDOVER (29 October 2026):** [V4 verified takeover and activation prompt](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md). This supersedes V3 as the startup guide and retains the exact R0–R16 research roles, recent merged PRs, full code/data/metric state, publisher source, strict scientific blockers and first next-chat sprint. V4's CI SHA is a dated baseline; re-query latest `main` and both Python CI results before using it. **No independently qualified runnable tasks or verified real effectiveness results.**

**Uncertainty-Guided Search for Reliable AI-Generated Software**

Research-stage, reproducible software-engineering framework investigating how
coding agents should allocate limited computation between **producing patches**
and **acquiring evidence** about patch correctness. The primary prospective
test compares uncertainty-aware decision making with matched-budget search
without calibrated uncertainty. No empirical superiority is claimed.

### Verified research evidence — 29 October 2026 snapshot

| Evidence | Source-grounded current status |
|---|---|
| PR-discovery metadata | **120** distinct PR/repository-name leads, **119** metadata records retrieved |
| Search-language strata | **12** query strata; **not** 12 independently verified changed-source languages |
| Production source-path leads | **62** metadata leads, **not** runnable tasks |
| Human-review shortlist | **12** candidates; approval is pending |
| Independent executable tasks / sealed functional oracles | **0 / 0** |
| Confirmatory study | **6 model names × 8 planned policy slots**; no real model-study results |
| Security | Non-executing OCI launch preflight; **not** a verified third-party sandbox |
| Empirical correctness / risk effects | **N/A** — no eligible verified task outcome observations |

**Start here:** [Dataset quality and provenance](data/curated/README.md) ·
[Source-free metadata release validator](scripts/verify_dataset_release.py) ·
[Research metric definitions and readiness exporter](scripts/export_research_readiness.py) ·
[Canonical Springer manuscript](paper/overleaf/main.tex) ·
[Research blockers](configs/ucode_work_remaining_gates_2026-10-27.json).

### Evaluator-only ITT and selective-release sensitivity analysis

U-CODE now includes an explicit
[post-terminal policy accounting module](src/ucode/postterminal_accounting.py)
that audits the **entire assigned task/model/seed/budget matrix** before
estimating full-task success, release coverage, conditional wrong-release
risk, failures and average five-resource costs. Infrastructure failures
produce worst/best missingness bounds rather than disappearing from the
denominator; a policy that never releases has **undefined (N/A)** observed
wrong-release risk, not `0%`.

[Methods, mathematical definitions and limits](docs/POSTTERMINAL_ITTS_RELEASE_AND_ATTRITION_2026-10-29.md)
· [Synthetic reproducibility smoke](scripts/smoke_postterminal_accounting.py).
**All tests are first-party synthetic records, not real patch outcomes,
authenticated evaluation evidence or risk guarantees.**

### Reproduce offline checks

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m scripts.audit_dataset_quality --output-dir dist/ucode-pr-metadata-clean
python -m scripts.verify_dataset_release dist/ucode-pr-metadata-clean
python -m scripts.export_research_readiness --output-dir dist/ucode-research-readiness
python -m scripts.audit_overleaf_sources
```

All commands run **offline** with first-party code and public, source-free
metadata; none download model weights, execute discovered repositories or
read sealed evaluation labels. The GitHub CI matrix runs Python 3.10 and
3.12 and attaches the generated metadata, metrics, and source-only manuscript
artifacts. Audit manifests and locally calculated SHA hashes establish
internal reproducibility, **not** external publisher authenticity or source
rights. A real experimental conclusion requires rights-cleared tasks, safe
execution, independent oracles and verified per-policy resource accounting.

---

> **Historical V3 handoff (27 October 2026):** [archived previous activation and cumulative evidence log](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V3_2026-10-27.md). For all **new** work, follow the [V4 canonical takeover](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md) and its [machine-readable evidence snapshot](configs/ucode_handoff_v4_2026-10-29.json).


**Uncertainty-Guided Search for Reliable AI-Generated Software**

> Research-stage framework. No effectiveness claims, completed model experiments, or verified 120-repository corpus are asserted.

U-CODE studies **when a software engineering agent should test, retrieve context, generate another patch, repair, or abstain** under a fixed execution and inference budget. The target is the Springer *Automated Software Engineering* special issue **Search-Based Software Engineering in the Era of LLMs and Agentic Systems** (30 January 2027): https://link.springer.com/collections/jjcfecffai.

## Continue U-CODE in a new ChatGPT chat

**[V4 verified new-chat master handoff — 29 October 2026](docs/UCODE_NEW_CHAT_MASTER_HANDOFF_V4_2026-10-29.md)** is the authoritative startup and R0–R16 role handoff. It supersedes the [26 October historical scientific handoff](docs/UCODE_MASTER_HANDOFF_2026-10-26.md) for session activation. Verify current GitHub `main` and live CI before acting; the V4 commit and CI numbers are a historical snapshot, not permanent current status.


## Framework at a glance

![U-CODE framework: six policy stages, a bounded feedback loop, and an independently sealed evaluation lane](docs/figures/ucode-framework.svg)

<sub>Figure 1. Proposed U-CODE architecture. The top row is the risk-aware agent policy (task → interventions → evidence modeling → BES → controlled execution → release/abstention); the curved teal arrow returns **visible** execution feedback from the execution stage to BES. The lower research lane independently admits tasks, seals the functional oracle, evaluates released artifacts, and summarizes evidence. **Architectural design, not a completed or validated experimental result.** [View scalable SVG](docs/figures/ucode-framework.svg).</sub>

## Springer manuscript and joint-scenario research update (27 October 2026)

**Canonical article source:** [paper/overleaf/main.tex](paper/overleaf/main.tex)
and [references.bib](paper/overleaf/references.bib). The abstract
and contribution statement now separate established work
(SWE-Search, SWE-Verifier, PATSSEL, Bayesian value of information)
from the testable proposed contribution: **whether conditionally
dependent diagnostic evidence is worth purchasing instead of
generating/repairing another patch under five equal hard resource
budgets**. The Springer Methods sections include one-step
finite-scenario model sensitivity, limited generative point-forecast
comparisons, and the newer **joint-scenario diagnostic and generation
minimax equation**. The Results section is explicitly a status report
with **zero confirmed empirical effectiveness results**.

**New algorithms:**
[full joint-scenario one-step selector](src/ucode/joint_scenario_action.py)
uses the SAME frozen set of alternative diagnostic and
generator/repair forecasts for every feasible action, and
abstains/releases if no feasible intervention has positive
worst-scenario marginal terminal utility. This remains a
restricted one-step analytical reference, NOT a statistically
robust or fully running repository coding agent. Upstream
[one-step mixed reference](src/ucode/robust_mixed_intervention.py)
uses point generation forecasts; their distinct assumptions are
documented explicitly. We also reject Python bool-as-int
substitution for probability, token/test/GPU/CPU/wall quotas,
resource prices, and release penalties.

**Reproducibility and review:** the
[manuscript source auditor](scripts/audit_overleaf_sources.py)
checks the publisher-class declaration, 150--250 word abstract,
4--6 keywords, all citations and cross-references, balanced
environments and no fabricated completed Results. This is
NOT an actual LaTeX PDF compile. Run:

```bash
python -m scripts.audit_overleaf_sources
python -m examples.joint_scenario_action_smoke
python -m unittest discover -s tests -v
python -m scripts.export_overleaf --output dist/UCODE_Overleaf_sources.zip
```

The [Overleaf README](paper/overleaf/README.md) explains why
GitHub changes do not automatically modify an existing live
Overleaf project; imports require the official Springer
`sn-jnl.cls` project and reconciliation of collaborator edits.

**Empirical blockers unchanged:** 120 clean PR *metadata* records
over twelve search-language strata, zero independently accepted
executable tasks, no authenticated evaluator/hidden oracle
or six-checkpoint GPU runs. The paper is not yet submission-ready.
The generated source ZIP, not a verified rendered PDF, is
attached to passing GitHub CI.

## New methodological falsifier and real pre-fix provenance (27 October 2026)

**Methodology:** [U-CODE novelty and falsification ledger](docs/UCODE_NOVELTY_FALSIFIERS_AND_MATHEMATICS_2026-10-27.md)
clarifies that VOI, search, verification, abstention and robust optimization
are established ideas. Our proposed scientific contribution is the **measured
incremental effect of buying history-dependent diagnostic evidence versus
candidate generation/repair under five shared hard resource limits**,
including model misspecification checks, when compared fairly with
SWE-Search, SWE-Verifier, RETRACE, and PATSSEL. No real experimental
reliability effect or statistical risk certificate is claimed.

The new [scenario-robust evidence audit](src/ucode/scenario_robust_evidence.py)
calculates finite-model best/worst-case **one-step** net diagnostic gain,
uses frozen history-conditional observation rows, enforces all five budget
caps, and conservatively stops if no probe benefits in all declared
scenarios. A new [mixed evidence-versus-generation reference](src/ucode/robust_mixed_intervention.py)
compares those conservative diagnostic scores with separately frozen
generation/repair terminal-utility POINT forecasts on the same
utility scale, using the same five hard budgets. Unlike diagnostics,
generative forecasts are not scenario-robust. These are deterministic
analytical controllers, NOT an integrated six-model repository agent,
a verified full-task result, or general robust POMDP theorem.
Reproduce both synthetic falsifiers:

```bash
python -m examples.scenario_robust_evidence_smoke
python -m examples.robust_mixed_smoke
```

**Real metadata progress:** two prioritized PHP and Go PRs now have
[original GitHub issue chronology observations](data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json)
and [immutable pre-fix Git commit/tree and source/toolchain blob observations](data/admission/2026-10-27/two_candidate_pre_fix_tree_inventory.json).
The original issues precede the PRs by 152 and 8 seconds respectively,
but the original issue text has NOT been archived as of PR creation.
The PHP/Go original tree lists 171/88 entries and contains checked
production/toolchain paths, respectively. First-party offline validators
reject forged IDs, path traversal, wrong tree/commit SHA substitutions
and unsupported claims of source rights, actual build or independent
functional tests:

```bash
python -m scripts.verify_two_issue_chronologies
python -m scripts.verify_pre_fix_git_trees
```

**Still blocked:** complete snapshot rights review, independent pre-fix
specifications, safe source checkout, hermetic build, evaluator-only oracle,
final family-safe split, and real six-checkpoint model/agent runs.
These two source trees are STRUCTURALLY OBSERVED but not executed.

## Independent A/B manual evidence review for the 12 pending tasks (27 October 2026)

A new [two-reviewer worksheet and non-automatic disagreement protocol](docs/INDEPENDENT_REVIEWER_ADJUDICATION_2026-10-27.md)
extends the existing frozen 12-candidate [pending admission packets](docs/PENDING_TWELVE_TASK_REVIEW_PACKETS_2026-10-27.md).
The offline [export script](scripts/export_independent_review_forms.py)
creates separate A/B pending human evidence forms, with **96 assessment
cells per reviewer (192 total)**. The [validator](src/ucode/reviewer_adjudication.py)
checks immutable candidate/PR/packet identities, duplicate/missing gates,
reviewer evidence digests, independent reviewer identity declarations
and disagreement across nonpending gate pairs. It NEVER automatically
authorizes task execution, even on agreement.

```bash
python -m scripts.export_independent_review_forms --output-dir dist/ucode-independent-reviewers-only
```

The generated forms contain **zero completed assessments, zero
independently approved executable tasks and zero observed reviewer
agreement statistics**. Real independent reviewers, verified file
licenses, sealed test oracles and audited safe execution are needed
before six-model experiments; these are *engineering instruments*,
not completed human annotations or finished empirical Results.
GitHub CI attaches the output as
`ucode-two-reviewer-forms-PENDING-v1`. Never expose these reviewer-only,
post-PR records to code-generation agents.

## Compact 120-repository dataset cleaning (27 October 2026)

The original 120 unique repository-name/PR-link discovery records span
**12 GitHub query-language strata, 10 PR links each**: Python,
JavaScript, TypeScript, Java, Go, Rust, C++, C, C#, Kotlin, PHP and Ruby.
Read-only metadata retrieval succeeded for 119 links. The audited
triage identified 62 **production-source PATH** leads, 14 higher-priority
manual-review cases, an initial **12-item manual-review queue** spanning
nine query-language strata, and 11 source-lead query-language mismatches
or unobserved changed-source languages. **Zero tasks** are approved for
real execution: path suffixes do not establish independent functional
oracles, file-specific rights or per-line AI authorship.

This is now a versioned compact [120-repo discovery frame](data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv)
plus [frozen, CI-verified twelve-stratum summary](data/curated/2026-10-27/frozen_cleaning_summary.json),
[full data card and seven-day gated pilot schedule](data/curated/README.md),
[deterministic offline cleaning library](src/ucode/dataset_curation.py)
and [dataset builder](scripts/build_clean_pr_dataset.py).
The stricter [technical-quality auditor](scripts/audit_dataset_quality.py)
joins all 120 canonical audit entries, preserves the retrieval failure,
checks **exact** raw-to-clean commit identities, detects structural
duplicate, owner and fork-lineage review flags, distinguishes queried
from changed-source languages, and fails closed on unsupported approval
or leaked hidden-evaluator fields. It produces **eight compact,
source-free files** including the four cleaning outputs,
`dataset_schema.json`, `quality_report.json`,
`manual_lineage_and_rights_flags.json` and a portable SHA256
`release_integrity.json`. CI publishes these as
`ucode-pr-metadata-clean-v1` for independent inspection.
See the [Scientific Data readiness gates](docs/SCIENTIFIC_DATA_READINESS_2026-10-27.md):
our current metadata resource is **not** an independently verified
executable benchmark or a submission-ready Nature Data Descriptor.

```bash
python -m scripts.audit_dataset_quality --output-dir dist/datasets/ucode_pr_metadata_v1
```

**Scope and one-week limitation:** metadata cleaning is inexpensive
and does not require a rented GPU, but producing a genuinely
independent 12-language repair benchmark requires rights clearance,
pre-fix task reconstruction, executable isolated environments, and
separate sealed correctness oracles. The one-week target is an
**engineering/qualification pilot**, not a guarantee of 12-language
or six-model full experimental Results.

## Conservative 120-PR lineage and contamination review (27 October 2026)

U-CODE now reconstructs a [deterministic metadata provenance graph](src/ucode/lineage_risk_graph.py)
from all 120 source PR records, looking for matching
fork-parent hints, identical Git SHA values (even across
base/head/merge roles), and separately **same-owner warnings**.
The frozen audit has **nine same-owner warning edges**, zero
cross-record shared-commit/fork-parent edges, and 120
provisional single-record components. **This is not proof
that the code is independent**; content-level near-duplicates,
issue overlap, reused tests and unauthorized train/test
leakage have not yet been inspected. No experimental split
is certified. See the [lineage review ledger](docs/PR_LINEAGE_REVIEW_2026-10-27.md).

The [graph exporter](scripts/audit_lineage_risks.py)
produces four compact text-only files in its **own CI
artifact**, `ucode-lineage-review-only-v1`, kept
separate from the eight-file dataset-quality ZIP.
[SHA256 verifier](scripts/verify_lineage_review.py)
and [adversarial tests](tests/test_lineage_risk_graph.py)
check cross-role ancestry flags, source-of-truth consistency,
zero task admissions and tamper resistance.

The optional [SWE-rebench V2 metadata intake](src/ucode/external_dataset_intake.py)
also accepts verified Unix-millisecond timestamps as
well as safe upstream string fields; external CSV
formula/control characters and malformed metadata
are excluded with explicit attrition reasons.
This is **not** execution or qualification of
the third-party 32,079-task source.

## Human review packets: twelve PR leads, 96 open evidence gates

The [pending dossier generator](scripts/export_pending_review_packets.py)
converts the original 12-item diversity-aware manual shortlist into
**twelve independent-review metadata forms**; they are checked against
each original PR URL, revision and modified source/test path by
the [existing task-admission validator](scripts/check_task_admission.py).
Each form has eight `PENDING` evidence gates, making **96 open
reviews, zero approved tasks**. GitHub CI publishes them separately
as `ucode-admission-review-only-v1`; see the
[human-review protocol](docs/PENDING_TWELVE_TASK_REVIEW_PACKETS_2026-10-27.md).

**Never provide these reviewer packets directly to a model:** they
include post-PR identifiers and changed test paths which can
leak the solution. The executable agent-visible task
representation and genuinely sealed oracle are still absent.

## Optional larger multilingual benchmark screening (not run)

The [SWE-rebench V2 public dataset](https://huggingface.co/datasets/nebius/SWE-rebench-V2)
reports **32,079 upstream tasks and 20 repository-language categories**.
This dataset belongs to its original authors and is NOT part of the 120
distinct U-CODE discovery PRs. A new [local, optional metadata-only
intake](src/ucode/external_dataset_intake.py) and
[CLI](scripts/screen_swe_rebench_v2.py) accept only **seven projected,
non-oracle fields** from an *already-downloaded, revision-pinned,
offline Parquet snapshot*. They explicitly forbid reading the upstream
gold solution patch, test patch, test IDs, problem statement,
install instructions or LLM annotations into the intake table.
They normalize twelve in-scope language aliases, flag duplicate
source identities and same-base/overlapping repository candidates,
and never mark tasks runnable or independent.

The [source registration](configs/external_multilingual_source_swe_rebench_v2_2026-10-27.json)
and [intake protocol](docs/SWE_REBENCH_V2_SAFE_DATA_INTAKE_2026-10-27.md)
retain source rights, executable task admissions, source revision
and GPU experiments as **unverified/not run**. Real data acquisition
and evaluator reconstruction require separate authorization and a
rootless, network-off sandbox. Do not describe this external
source as a new original U-CODE or Nature Scientific Data dataset.

## Optimized uncertainty-free search comparator (26 October 2026)

A new [bounded heuristic beam-search reference](src/ucode/optimized_search.py)
implements the prospective `no_uncertainty_search` controller at the
**first-party/offline algorithm-engineering stage**. Unlike the separate
[fixed-schedule blind negative control](src/ucode/blind_search.py), it
searches over feasible action sequences, adapts to visible test/analysis
results, archives multiple candidate SHA256 artifacts and tracks repair
parents. Its public input schema excludes predictive acceptability,
confidence, Bayesian likelihoods, golden patches and evaluator-only results.
All five resources remain independently capped; a scalar planning price
cannot make an infeasible action admissible. Candidate archive evidence
is bound to the **original patch**, including after later repair.

[Design, limits and falsifiers](docs/OPTIMIZED_UNCERTAINTY_FREE_SEARCH_2026-10-26.md)
· [adversarial engineering tests](tests/test_optimized_search.py)
· [shared action-inventory parity tests](tests/test_optimized_action_parity.py).

**Do not call this a tuned empirical baseline yet.** Beam scores are
heuristic action-opportunity proxies, not expected patch-success probabilities.
The [static BES-versus-optimized inventory audit](src/ucode/matched_action_inventory.py)
matches action IDs, kinds, five-dimensional nominal costs and initial caps,
and the new [matched action-target expander](src/ucode/matched_opportunities.py)
now also offers both policies the same candidate-target choices.
**End-to-end parity remains blocked** by missing shared measured-cost
LLM/tool execution, training-only tuned weights, independently rights-cleared
tasks and sealed-oracle outcomes. The existing eight-policy and
six-model prospective rosters are unchanged.

## Shared candidate/receipt ledger (26 October 2026)

The [shared offline action and archive contract](src/ucode/matched_session.py)
now lets the search-optimized uncertainty-free policy and a
[per-candidate conditional BES adapter](src/ucode/conditional_archive.py)
operate on the **same typed candidate SHA archive, patch-specific evidence,
one-use tool IDs, and reported five-resource receipt ledger**.
The [pre-execution matched-start audit](src/ucode/matched_session.py)
fails on changed initial candidate identity, action opportunities, archive
capacity, or budget. [Adversarial offline tests](tests/test_matched_session.py)
exercise both policy paths on common synthetic states, including cases where
the two release gates disagree. Details and scientific falsifiers are in
[the dated research ledger](docs/SHARED_MATCHED_ARCHIVE_2026-10-26.md).

**Updated 26 October 2026:** the [joint conditional BES planner](src/ucode/joint_conditional_bes.py)
now performs finite-horizon whole-archive look-ahead across diagnostic
targets and symbolic future generation/repair branches. The
[matched uncertainty-free controller](src/ucode/matched_opportunities.py)
uses the same public action-target opportunity menu, but no Bayesian
inputs. The original [per-patch adapter](src/ucode/conditional_archive.py)
remains available for regression comparisons. See the
[joint planner research ledger](docs/JOINT_MULTICANDIDATE_BES_2026-10-26.md)
and [synthetic adversarial tests](tests/test_joint_conditional_bes.py).
**Limits:** finite factorized hypothetical model only; no train-fitted
kernels, admitted tasks, sealed real trials, independently measured
hardware telemetry, sandbox enforcement, or demonstrated reliability gain.
Prompts, RNG sampling, actual generation and tool opportunities, model
checkpoint snapshots, sealed oracles and safety remain unverified.
This is **engineering parity, not a real paired effectiveness result**.

## Correlation-aware whole-archive Bayesian planning (27 October 2026)

The new [finite joint-truth Bayesian search reference](src/ucode/correlated_archive_bes.py)
models **dependence between the acceptability of different archived patches**,
not just dependence among diagnostic outcomes for a single patch. A visible
diagnostic on patch A can therefore change the predicted acceptability of
patch B; a repair-production outcome can update the latent belief about its
parent. The algorithm uses the **same public action-target menu** as the
uncertainty-free comparator, while keeping its private joint probability
model out of the baseline.

A [same-marginal synthetic falsifier](tests/test_correlated_archive_bes.py)
shows that an independent versus anti-correlated three-patch prior can
reverse the preferred first diagnostic, despite identical per-patch
marginal priors. See the [mathematical and integrity ledger](docs/CORRELATED_JOINT_TRUTH_2026-10-27.md)
and the updated [Springer manuscript source](paper/overleaf/main.tex).

**Not empirical:** no fitted joint priors, sealed external evaluation,
verified task permissions, actual model execution, trusted five-resource
metering, calibrated risk guarantee, or live Overleaf synchronization.
The correlated planner is a bounded offline sensitivity-analysis
reference, **not** a validated improvement over uncertainty-free search.

## Policy-neutral metering attestation prototype (27 October 2026)

A new [five-resource structural metering gate](src/ucode/metering_attestation.py)
checks candidate evidence for **tokens, test calls, GPU, CPU, and wall time**,
requiring separately declared source counters, cap enforcement, independence
and receipt hashes for each. The
[shared-ledger reconciliation](src/ucode/metering_reconciliation.py)
compares one new action receipt against all five recorded budget deltas and
the SHA256-fingerprinted visible execution trace. Both are policy-neutral,
so neither algorithm is granted extra meter or evaluator-only information.

A **Linux first-party subprocess smoke** tests hardcoded internal scripts
with a wall watchdog and integer CPU rlimit; no untrusted repository code is
run. The [research-integrity memo](docs/METERING_ATTESTATION_CONTRACT_2026-10-27.md)
documents its limitations. These contracts remain **structural only**:
claimed receipt digests are not cryptographic signatures; CPU child rusage
can include concurrent children; no rootless network-isolated runner, trusted
token/test/GPU counters, independently signed attestation or real executable
task has been established. The APIs explicitly decline real-trial approval.
The Springer [Methods draft](paper/overleaf/main.tex) reflects this boundary.

## All-six AI Galaxy GPU rental deployment configuration (27 October 2026)

All six **unchanged** selected Hugging Face checkpoint IDs now have one
[version-controlled deployment configuration](configs/ai_galaxy_six_model_deployment_2026-10-27.json)
with a **single NVIDIA A100 80GB GPU hardware family for ALL SIX**
(including Devstral), initial model contexts, one-sequence concurrency,
unique ports 8100–8105, and explicit compatibility risk flags.
The recommended profile is **one A100 80GB running the models sequentially**;
an optional six-A100 capacity estimate is NOT an approved rental. See the
[AI Galaxy hardware sizing, advertised rental price and safety ledger](docs/AI_GALAXY_SIX_MODEL_RENTAL_PLAN_2026-10-27.md).

A [conservative GPU-days and RMB scenario estimator](scripts/estimate_ai_galaxy_rental.py)
requires an explicit `--minutes-per-assignment`; it cannot invent
task throughput or count unqualified candidate PRs as executable tasks.
Start with a limited **12–24-hour rental preflight**, not a prepaid
multiweek GPU reservation. Full eight-policy × six-model × multiple-seed
evaluation can demand many weeks of sequential A100 time depending
on actual per-task latency. See
[the rental scenario ledger](docs/AI_GALAXY_SIX_MODEL_RENTAL_PLAN_2026-10-27.md).

Use `python -m scripts.plan_ai_galaxy_six_models` for read-only full-roster
preflight, or add `--profile simultaneous_six_gpu --json`.
[Adversarial registry tests](tests/test_ai_galaxy_six_models.py)
reject missing/reordered model IDs, false weight/license/inference claims,
non-immutable revisions, unsafe initial memory allocations, duplicated ports,
and deletion of authorization gates. CI checks both Python versions.

**Planning is not deployment:** zero of the six weight snapshots are
downloaded or pinned, zero provider terms approved, zero model inference
performed, and zero real dataset tasks admitted for sealed evaluation.
Official Mistral documentation explicitly lists **A100** for
Devstral Small 2. vLLM supports Ampere FP8 weight-only **Marlin W8A16**
as an alternative to H100-native FP8; the exact pinned Devstral/A100
runtime must still be verified. No second GPU type is required
or budgeted. DeepSeek custom model code needs independent review.
The model roster remains six checkpoints from five publisher families;
no model is silently excluded because it is too large or gated.

## Six LLMs selected for the planned study (25 October 2026)

All six recommended models have been **accepted by the researcher for the U-CODE study plan**. The [version-controlled six-model configuration](configs/accepted_six_model_study_2026-10-25.json), [model preflight code](src/ucode/model_readiness.py), and [experiment/reproducibility protocol](docs/SIX_MODEL_STUDY_PLAN_2026-10-25.md) preserve every checkpoint—none is silently excluded for being larger or gated.

| Selected model | Research role | Current status |
|---|---|---|
| [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) | Local-feasibility coding baseline | Planning selected; no pinned weights |
| [Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) | Larger mixture-of-experts coding agent | Planning selected; high-memory gate |
| [Devstral Small 2 24B](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512) | Repository-agent specialist | Planning selected; runtime/memory gate |
| [DeepSeek-Coder-V2-Lite-Instruct](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) | Independent code-specialist publisher | Planning selected; model-license/security gate |
| [CodeGemma 1.1 7B IT](https://huggingface.co/google/codegemma-1.1-7b-it) | Smaller code-specific control | Planning selected; gated terms/access |
| [Llama 3.1 8B Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) | General-instruct control | Planning selected; gated terms/access |

**Planning approval is not provider authorization or a benchmark result.** All six currently fail the inference-readiness gate until their provider terms, full model/tokenizer revisions, weights, compatible execution environment, memory profile, and sandbox have been verified. We will compare **six checkpoints from five publisher families**. No inference, paid GPU, or independently verified repository task run has been performed.

## Current status (25 October 2026, all ten PR screening positions per language)

- **120 discovery candidates across 12 GitHub primary-language search categories**, each with a PR link returned for `author:copilot-swe-agent[bot] is:pr is:merged`. **These are NOT 120 verified AI-generated repositories.** GitHub bot attribution alone does not establish what fraction of source code is AI-authored.
- Public dataset leads: [AIDev](https://huggingface.co/datasets/hao-li/AIDev), [SWE-chat](https://huggingface.co/datasets/SALT-NLP/SWE-chat) (gated), [DroidCollection](https://huggingface.co/datasets/project-droid/DroidCollection), [SWE-rebench](https://proceedings.mlr.press/v306/badertdinov26a.html), [EffiBench-X](https://huggingface.co/datasets/EffiBench/effibench-x). They have **distinct units of analysis** and must not be naively merged.
- **Issue #1 completed discovery metadata screen:** **120/120 links attempted, 119/120 PRs retrieved**, with **1 GitHub 404 retrieval failure** (candidate #26). Among the 119 retrieved: **62** production-source-path *candidates*, **10** test-only, **45** non-source, and **2** empty-file-list cases requiring review. **62** have recognized repository-level SPDX metadata; **12** forks; **zero fully eligible executable tasks** pending independently verified AI-line attribution, file rights and sealed independent functional oracles. These 62 are weak path-level hints, **not 62 verified AI-generated patches**. [Full 120-link research ledger](docs/logs/2026-10-25_complete_120_pr_screen.md) · [Initial 24-PR evidence](docs/logs/2026-10-24_issue1_stratified_pr_audit.md) · [Third-entry screening](docs/logs/2026-10-24_issue1_second_stratified_batch.md) · [Fourth-entry screening](docs/logs/2026-10-24_issue1_fourth_stratified_batch.md) · [Fifth-entry screening](docs/logs/2026-10-24_issue1_fifth_stratified_batch.md) · [Sixth-entry screening](docs/logs/2026-10-24_issue1_sixth_stratified_batch.md) · [Seventh-entry screening and .NET generated-artifact correction](docs/logs/2026-10-24_issue1_seventh_stratified_batch.md). GitHub discovery language is not necessarily the changed-source language. [Latest source-only manual review queue](scripts/triage_review_queue.py) scores **62** path candidates but admits **none** without independent review.
- The project initially offers a **pure-Python research scaffold** and **offline toy environment**, not a trained/calibrated uncertainty model or model-driven code repair engine.

## Scientific novelty and mathematical formulation (24 October 2026)

**Reviewed close competitors:** 24 primary-source links and potential baseline threats
in [the dated novelty matrix](literature/novelty_matrix_2026-10-24.csv).
Key comparison papers include SWE-Search (MCTS), GA4GC (multiobjective
configuration search), SWE-Replay (trajectory reuse), SWE-Verifier (2026-10-21
selective action verification) and work finding negative effects of
uncertainty-only regeneration. None of these concepts can be claimed
individually as a first.

**Refined U-CODE question:** can independent calibration and resource-aware
evidence acquisition determine when to test, statically analyze, retrieve,
generate, repair or abstain, improving *released* patch reliability
against equal-budget search without calibrated uncertainty?

The [formal methods and novelty/falsification memo](docs/FORMAL_PROBLEM_AND_NOVELTY_2026-10-24.md)
defines a partially observed decision process, the five-resource budget vector,
full-task independent verified success, selective wrong-release risk, coverage
constraints, Bayesian value of diagnostic evidence, and exactly what would
falsify the method. A strict posterior acceptance gate can even make signed
diagnostic evidence value negative; this is a **mathematical reference
counterexample**, not a measured study result.

**Algorithmic prototypes:** `src/ucode/voi.py` provides an analytically
testable one-step binary diagnostic value benchmark; `acquisition.py`
applies candidate-generation EHVI only to `generate` and `repair` actions.
`test` / `retrieve` / `static_analysis` do **not** manufacture new
candidate points. These two prototypes are **not integrated into a learned,
fully tested search controller** and are not empirically validated.

**Manuscript:** [paper/overleaf/main.tex](paper/overleaf/main.tex)
now has properly separated objectives, resource-constrained Bellman/EVSI
formulations, 16 source-linked BibTeX entries, and no fabricated results.
The official Springer publisher class is still required for a real compile.

## Version-controlled Springer/Overleaf workflow (updated 2026-10-24)

- **Directly updated GitHub sources:** [paper/overleaf/main.tex](paper/overleaf/main.tex)
  and [paper/overleaf/references.bib](paper/overleaf/references.bib).
- **New honest methodological reference:** [src/ucode/vector_policy.py](src/ucode/vector_policy.py)
  checks five independent resource budgets and compares modeled diagnostic
  evidence against generation/repair forecasts on one terminal-value scale.
  These forecasts are *hypothetical*, not fitted performance results.
- **Safe manuscript export:** `python -m scripts.export_overleaf --output
  dist/UCODE_Overleaf_sources.zip` creates a checksum-verified, deterministic
  paper-only ZIP. The CI workflow attaches that ZIP as an artifact named
  `ucode-overleaf-sources` on successful runs.
- **Live Overleaf is NOT directly connected.** The bundle is for importing into
  the [official Springer Nature template](https://www.overleaf.com/latex/templates/springer-nature-latex-template/myxmhdsbzkyd);
  the publisher class is intentionally not included. Overleaf Git/GitHub
  sync is a separate authenticated user-side operation.
  [Details](paper/overleaf/README.md).

## Next evidence gates: task admission and training-only diagnostic fitting

- [Diagnostic training interface](src/ucode/diagnostic_fit.py):
  binary sensitivity and specificity are estimated **only from labeled training
  repository/fork groups** with pre-oracle observation times, explicit model
  IDs and frozen input fingerprints. Validation/evaluation groups, duplicated
  task IDs and mixed model/action records fail closed. A trained diagnostic
  likelihood does NOT by itself supply a calibrated prior or a risk guarantee.
- [Task admissibility contract](src/ucode/task_gate.py): checks immutable
  revision identifiers, production-file language, declared file-rights and
  independent-oracle review references, pinned image digest and secure
  sandbox policy. Its positive status means **declared complete, needs human
  verification**, never safe or rights-cleared by automation.
- [Scientific procedure](docs/CALIBRATION_AND_TASK_ADMISSION_PROTOCOL_2026-10-24.md):
  split, leakage, selection bias, statistical limitations and go/no-go criteria.
- [Two-PR deep provenance case ledger](data/audits/2026-10-24/two_pr_commit_and_license_deep_check.jsonl):
  dependabot-core #16665 has human-authored commits with Copilot co-author
  trailers, whereas onnx-light-cpu #1005 has Copilot-authored commits with
  human co-author trailers on two commits. PR-level Copilot accounts are
  **not** precise AI line-authorship annotations. Both candidates have
  production-source changes and root LICENSE files, but are **not** admitted
  or independently executed.
- The Springer source in [paper/overleaf/main.tex](paper/overleaf/main.tex)
  now reflects both the training-only equations and the observed
  human/agent commit-metadata ambiguity. CI continues to generate the
  **ucode-overleaf-sources** source-only artifact; no direct Overleaf-account
  write is claimed.

## Deep Research continuation — 2026-10-24

The [dated Deep Research synthesis](docs/DEEP_RESEARCH_SYNTHESIS_2026-10-24.md)
reconciles new papers and model/dataset leads with the **canonical 84-PR
screening checkpoint**. The older 24-PR stratified screen is an initial
subset, not the total screened count. No naturalistic source is fully
oracle-qualified yet.

**Manuscript:** [Springer/Overleaf main.tex](paper/overleaf/main.tex)
has a stronger citation-grounded related-work and novelty-falsifier
section, plus a prospective matched-task evaluation subsection.
[references.bib](paper/overleaf/references.bib) includes recent 2026
verification papers, correctly marked as preprints.
[Novelty matrix](literature/novelty_matrix_2026-10-24.csv) currently
includes 24 source-linked comparisons, not an exhaustive systematic review.

**Reproducible pilot inputs:** [model candidates v2](configs/models_v2_2026-10-24.json)
(six leads, none license/revision/memory-approved), and
[dataset candidate registry v2](data/discovery/dataset_source_registry_v2_2026-10-24.csv)
(13 leads, not downloaded or independently executed).
Old v1 inventories remain version-controlled for transparency.

**Evaluator-only metrics:** [src/ucode/evaluation.py](src/ucode/evaluation.py)
calculates full-task verified success, release coverage and wrong-release
risk, and a strict task/model/seed/budget paired contrast with a
repository-lineage cluster bootstrap. All related regression tests are
**synthetic engineering tests**, not U-CODE success results.
[CI registry guard](scripts/validate_research_registries.py) prevents
candidate manifests from silently asserting approved rights, pinned
model revisions or verified execution.

**Latest CI:** [GitHub Actions](https://github.com/Rocky5502/U-CODE/actions)
executes the offline tests on Python 3.10 and 3.12, runs the candidate
manifest guard and produces an `ucode-overleaf-sources` manuscript
ZIP artifact. The GitHub paper source is canonical; **no authenticated
live Overleaf editor write or LaTeX compilation is claimed**.

**Next scientific blocker:** a source-rights reviewed, immutable,
independently oracle-tested **real** task in a truly isolated
nonprivileged/network-disabled sandbox. The proposed 40–60-task
pilot and 250–400-task confirmatory range are **conditional plans**,
not observed samples or fixed power targets.

## Algorithm milestone: Bounded Evidence Search (2026-10-24)

We now maintain an explicitly defined and tested `BES` **finite-horizon
look-ahead algorithm** rather than relying solely on the existing heuristic
and one-step vector selector.

- [Finite-depth BES](src/ucode/budgeted_belief_search.py) compares visible
  testing/static-analysis/retrieval outcomes with possible next candidate
  generation/repair outcomes under **five hard resource budgets**. It
  explicitly represents uncertain branch consequences and a terminal
  predicted-risk release or abstention decision. Up to 10 actions and depth
  4 are permitted in the bounded reference; search fails closed if it
  exceeds its state cap.
- [Closed-loop visible-evidence adapter](src/ucode/belief_session.py)
  incorporates an actual visible diagnostic sign or a predicted
  generated-candidate risk, deducts the measured budget, prevents action
  replay and replans. Hidden correctness-oracle results are **not policy
  inputs**.
- [Fully mathematical protocol](docs/BES_ALGORITHM_METHOD_AND_FALSIFIERS_2026-10-24.md)
  provides the bounded Bellman recursion, **restricted** backward-induction
  argument, hard-budget invariant and a toy two-test example showing
  positive *sequential option value* despite zero one-step gain.
- [First-party demonstration](examples/bes_lookahead_smoke.py) can be run
  with `python -m examples.bes_lookahead_smoke`. It prints explicit
  **SYNTHETIC** warnings; no third-party code/model/oracle is run.
- [Springer LaTeX](paper/overleaf/main.tex) includes an additional BES
  algorithm subsection with exact scope and toy caveats; the CI-generated
  `ucode-overleaf-sources` ZIP contains the current GitHub manuscript,
  but **does not sync a live Overleaf project**.

**Critical research limitation:** BES presently models **one active code
candidate**, not a joint multiobjective Pareto archive; it assumes declared
conditional independence between separate diagnostic probes if more than one
is planned and uses frozen externally supplied scenario probabilities.
Both the Bellman algorithm and value-of-information reasoning are established
prior mathematical ideas. Our implementation is new to this repository,
but publication-level **algorithmic novelty and actual performance gains
are NOT demonstrated** until a controlled multi-model, sealed-oracle
study with strong budget-matched baselines is completed.

## Research continuation: dependency-aware evidence (2026-10-24)

- [History-conditioned BES](src/ucode/conditional_bes.py) makes
  the next diagnostic likelihood depend explicitly on the sequence
  of *visible* prior test results, rather than multiplying marginal
  independent-test probabilities. Missing contexts or impossible
  reported outcomes fail closed. It currently handles **one existing
  candidate and diagnostic actions only**, not generation/repair.
- [Training-only conditional kernel fitter](src/ucode/conditional_fit.py)
  requires a precommitted complete diagnostic panel, segregated
  repository/fork train/validation/evaluation groups, monotonic
  evidence-before-training-oracle times and context-specific class
  support. Merely declaring these properties does not attest
  independently verified data collection or prevent upstream leakage.
- [Independence versus redundancy demo](examples/conditional_dependence_smoke.py)
  shows, with **synthetic** probabilities and identical marginal test
  accuracies, that an independent two-test plan can have positive
  option value while a perfectly redundant test pair does not.
  Reproduce with `python -m examples.conditional_dependence_smoke`.
- [Research protocol and elementary non-identifiability proof](docs/CONDITIONAL_DIAGNOSTIC_EVIDENCE_2026-10-24.md).
  [Springer LaTeX](paper/overleaf/main.tex) now includes explicit
  history-conditional posterior equations and a correlated-test
  counterexample. The `ucode-overleaf-sources` CI artifact contains
  this GitHub source; authenticated live Overleaf is not connected.

**Research status:** These are training-contract and algorithmic
engineering achievements, not real fitted test kernels, executable
external benchmark tasks or evidence of an empirical improvement.
The discovery metadata screen is now **120 of 120 attempted, 119 retrieved,
62 production-source-path hints and zero fully study-eligible tasks**. The
[deterministic manual-review queue](src/ucode/review_queue.py) separates
first-pass human leads from experimental admission. It **cannot** mark a
PR as AI-line-attributed, rights-cleared or independently oracle-verified.

## Real-task pilot admission: two pinned PR candidates (25 October 2026)

Following the completed 120-link metadata screen, we have opened **two real pre-fix pilot dossiers**: [PHP file-persistence and cache layout (PR #172)](https://github.com/mvdbos/php-spider/pull/172) and [Go settlement/scoring and rank rules (PR #30)](https://github.com/PlayHuai/eighty-point-huai-an/pull/30). The [research report](docs/PILOT_ADMISSION_EVIDENCE_GATE_2026-10-25.md) records original issue timing, immutable base/head/merge revisions, source/test paths, observed license files and unresolved evaluator constraints.

- [Eight-gate admission contract](src/ucode/task_admission.py): immutable pre-fix snapshot, AI/human line attribution, file-specific reuse rights, independent functional oracle, hidden-oracle split, sandbox isolation, pinned toolchain and enforceable resource limits.
- [Two original evidence dossiers](data/admission/2026-10-25/pilot_dossiers.jsonl): **16/16 gates currently PENDING**; neither candidate is an admitted research experiment. Even fully self-reported evidence requires **external independent adjudication**, never automatic promotion.
- [Offline metadata-linked validation](scripts/check_task_admission.py): `python -m scripts.check_task_admission`. CI verifies unchanged PR identities/hashes/paths; no external program is cloned or executed.

**This is provenance and task-admission engineering, not model-task benchmarking.** PR-added test files are not independent correctness oracles. License tags and human/bot co-author trailers do not establish changed-line provenance. Both candidates need independently attested file rights, sealed tests, and audited network-off non-root execution before any six-model study is possible.

## Prospective sealed evaluation boundary and oracle ambiguity (25 October 2026)

The experimental-policy/evaluator interface is now specified and regression-tested in first-party code. The [boundary module](src/ucode/evaluator_boundary.py) serializes only the **agent-visible** pre-fix task/specification references and explicitly omits evaluator-only oracle references, oracle commitments, reviewer metadata and PR-authored test paths. The [offline checker](scripts/check_evaluator_boundary.py) binds both registrations to the original frozen task-admission dossiers. The [prospective registration JSONL](data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl) has **zero private oracle files and zero execution approvals**; this is metadata segregation, not a validated operating-system security boundary.

For the Go settlement pilot, a new [pre-fix specification ambiguity witness](src/ucode/spec_ambiguity.py) demonstrates that capped loser deltas `(0,-5)` imply a recovered pool of `5`; both nearly equal winner awards `(2,3)` and `(3,2)` meet zero-sum, nonnegativity and the **extra hypothetical** fairness rule. Neither output is established as the unique domain-approved gold answer. [Reproduce only first-party metadata and arithmetic](examples/pilot_oracle_boundary_smoke.py) with `python -m examples.pilot_oracle_boundary_smoke`. Real independent specification sign-off, task rights and sealed execution remain blocked.

**Scientific constraint:** The two real PR candidates are still unapproved, the six-model study has not executed, and no observed model success-rate improvement or risk certificate is claimed.

## Journal-grade empirical protocol (25 October 2026)

U-CODE now has a [prospective Springer SBSE evaluation and falsification plan](docs/SBSE_CONFIRMATORY_EVALUATION_AND_FALSIFIERS_2026-10-25.md) grounded in the official journal call, the latest independent-verifier literature, and the project's real zero-admission task audit. The [frozen-proposal JSON](configs/confirmatory_sbse_protocol_2026-10-25.json) retains **all six user-selected LLMs** and specifies **eight proposed policies**, with primary U-CODE conditional BES versus **the same search tools and hard budgets without uncertainty**. Those controls are **planned**, not eight executed agents.

The [evaluator-only paired-trial contract](src/ucode/experiment_contract.py) requires a complete policy × task × model × seed × budget assignment, frozen pre-fix commit, model revision, tool rights, environment fingerprint, five measured resource costs, release-patch digest and matching independent evaluator verdict. It refuses fabricated/missing comparison cells and unmeasured or excessive costs. [Missing-infrastructure bound analysis](src/ucode/attrition_bounds.py) keeps incomplete attempts in the denominator and reports *worst/best-case effect bounds* without pretending they are confidence intervals. The [offline protocol verifier](scripts/validate_sbse_protocol.py) rejects any unsupported promotion to a completed six-model result.

**Research status:** The original 120 PR metadata screen is complete, two actual PHP/Go task-admission dossiers exist, but **zero independent executable tasks**, **zero confirmed six-model runs** and **zero verified policy-effect observations** are available. Experimental algorithms and methodological software do not establish journal-level empirical novelty. [Related primary sources: RETRACE](https://arxiv.org/abs/2608.08950), [Dockerless (EMNLP 2026)](https://aclanthology.org/2026.emnlp-main.640/), and [SWE-Bench Pro Verified](https://arxiv.org/abs/2609.08149).

## Reproducible uncertainty-blind control and equal action opportunities (25 October 2026)

The [first-party blind-search controller](src/ucode/blind_search.py) implements an observable-feedback **fixed-schedule** negative control using generate, retrieve, test, static analysis, repair and terminal release/abstain actions, with all five hard resource caps. It explicitly cannot receive Bayesian predicted success, diagnostic likelihoods or independent oracle labels. Diagnoses on an old patch cannot be reused after repair. A [shared action-inventory auditor](src/ucode/matched_action_inventory.py) verifies identical action IDs, action types, costs and budgets between the blind control and the BES reference. Its canonical digest omits BES-only forecast probabilities.

The [synthetic end-to-end action trace](examples/blind_search_smoke.py), [synthetic action-parity reproduction](examples/action_parity_smoke.py) and [study limitations](docs/BLIND_SEARCH_AND_PARITY_2026-10-25.md) are committed and run in CI. The trace generates a fake patch, retrieves context, fails a visible test, repairs, passes another visible test and chooses release—all **invented fixtures**, with no model inference or independent patch correctness judgment. This controller is a **negative control, not yet the optimized uncertainty-free search competitor** required for the journal's primary effectiveness claim.

## Research thesis

Our testable hypothesis is that **calibrated uncertainty signals, integrated into budget-constrained multi-objective search, can improve independently verified code reliability** against matched-cost baselines. Null and negative results are publishable.

## Repository contents

| Path | Purpose |
|---|---|
| `data/discovery/agent_pr_candidates_120.csv` | 120 discovery links, not vetted code |
| `data/discovery/dataset_source_registry.csv` | 10 dataset leads, all not downloaded |
| `data/discovery/pilot_pr_metadata_triage_4.jsonl` | Four real PR metadata checks; no code execution |
| `src/ucode/audit.py` | Read-only GitHub PR metadata/changed-file screening |
| `scripts/summarize_audit.py` | Deduplicated, fail-closed audit rollup from canonical JSONL |
| `src/ucode/uncertainty.py` | Probability quality, entropy, disagreement, calibration metrics |
| `src/ucode/search.py` | Explicit Pareto frontier and cost-aware intervention controller |
| `src/ucode/acquisition.py` | Monte Carlo expected hypervolume improvement per unit cost (prototype) |
| `src/ucode/simulation.py` | Deterministic *synthetic* environment for unit tests and debugging |
| `docs/RESEARCH_PROTOCOL.md` | Design, RQs, experiment matrix, rigor and leakage rules |
| `docs/DATA_GOVERNANCE.md` | Evidence and redistribution gates |
| `docs/PROJECT_BOUNDARIES.md` | Novelty and overlap safeguards |
| `paper/OUTLINE.md` | Journal manuscript blueprint, no fabricated results |
| `configs/models.json` | 6 model candidates, not downloaded |
| `tests/` | Offline tests |

## Quickstart

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
ucode simulate --seed 7
python examples/ehvi_smoke.py
ucode audit --limit 3 --output data/derived/pr_audit.jsonl
# Summarize the canonical GitHub-audited candidates and validate provenance
python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --output data/derived/screening_summary.json
# Next *unattempted* balanced cohort: eighth entry in each of 12 query-language groups
ucode audit --per-language 1 --language-offset 7 --output data/derived/batch08.jsonl
```

The `audit` command makes **read-only** GitHub REST requests and may hit rate limits; set `GITHUB_TOKEN` in your environment for higher limits. Do not commit the token. No GitHub repository is cloned or executed by the audit command. The demo uses synthetic, explicitly labeled data; its scores are **not experimental evidence**.

See the protocol before drawing any conclusions. Code in this repository may be redistributed according to its own license; third-party code and data retain their source licenses.

## 2026-10-24 research execution snapshot

The complete GitHub-derived PR metadata with immutable SHAs is in
[data/audits/2026-10-24/](data/audits/2026-10-24/), including the
[24-record normalized manifest](data/audits/2026-10-24/stratified_24_verified_metadata_with_triage.jsonl).
The read-only audit CLI now supports deterministic query-language stratum
offsets, distinguishes production-source / test-only / non-source changes,
and halts immediately on GitHub HTTP 403/429 instead of retrying in a loop.
**Metadata approval is not dataset eligibility.** No runnable third-party
code was executed for this research block.

## Evidence and next milestones

A four-PR API metadata spot-check found two source-bearing candidates
(MLflow #27058 is a JavaScript module under a tooling directory and
forem #24047 has Ruby source/tests) and two build/CI-only candidates
(Quantinuum/zixy #270 and boot-ui #1549). These are *initial* path checks,
not completed source attribution/license/functional verification. GitHub's
API identifies the author as `Copilot`, so the auditor accepts that
confirmed API alias as well as the discovery query name.

The initial offline CI suite passed on Python 3.10 and 3.12 for
the pre-acquisition commit; subsequent commits are checked by the
same workflow. Check [Actions](https://github.com/Rocky5502/U-CODE/actions)
for the current head commit status.

Track the six research gates in [GitHub Issues](https://github.com/Rocky5502/U-CODE/issues).
No model weights or 2–5 GB repository corpus have been downloaded,
and no real model accuracy/reliability experiment is claimed.


## Research command center — 24 October 2026

- **[Principal Investigator Master Superprompt (dated)](docs/UCODE_MASTER_SUPERPROMPT_2026-10-24.md)** — all senior research roles, Mermaid dependency graph, G0–G13 gates, six RQs, multiobjective search, dataset/model matrices, 30-minute work-block checklist, and journal milestones.
- **[Execution checkpoint](docs/UCODE_EXECUTION_CHECKPOINT_2026-10-24.md)** — exact next issue, status and evidence-led session ledger.
- **[Official Springer/Overleaf LaTeX shell](paper/overleaf/main.tex)** — sn-jnl manuscript skeleton, **not submission-ready**.
- **[Overleaf setup instructions](paper/overleaf/README.md)** — use publisher class from official Springer template.
- **[Six GitHub research issues](https://github.com/Rocky5502/U-CODE/issues)** — persistent acceptance gates.

**Reminder limitation:** the 30-minute schedule is a work-session *timebox*;
a one-time reminder, if created, does not establish an always-on research agent.
Every task requires real execution evidence and a current-state check.
