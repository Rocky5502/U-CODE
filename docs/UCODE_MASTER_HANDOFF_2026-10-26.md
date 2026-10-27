# U-CODE — MASTER RESEARCH HANDOFF AND NEW-CHAT SUPERPROMPT
**Handoff version:** 2026-10-26 (Asia/Singapore, user's local time)  
**Project:** U-CODE — Uncertainty-Guided Search for Reliable AI-Generated Software  
**Canonical GitHub repository:** https://github.com/Rocky5502/U-CODE  
**Default branch:** main  
**Verified pre-handoff commit:** 4d6b9f8f9431e6dd15ce7d0b2766e9be5a2af2f6  
**Verified pre-handoff CI:** https://github.com/Rocky5502/U-CODE/actions/runs/40179406607 — SUCCESS, 426 offline tests on EACH of Python 3.10 and Python 3.12, artifact ucode-overleaf-sources  
**This handoff file itself will create a later GitHub commit. Always refresh HEAD/CI before acting.**  
**Target:** Springer *Automated Software Engineering* special issue "Search-Based Software Engineering in the Era of LLMs and Agentic Systems" — https://link.springer.com/collections/jjcfecffai  
**Target submission deadline:** 2027-01-30. Verify publisher changes when working later.  
**Honest stage:** substantial reproducibility, metadata-screening and algorithmic prototypes; ZERO independently admitted executable software tasks; ZERO real six-model comparison or measured U-CODE reliability gain; journal paper NOT ready to submit.

---

## 27 OCTOBER 2026 — TWELVE HUMAN-ONLY ADMISSION PACKETS

**This entry supersedes the earlier 726-test figure.**

- `src/ucode/pending_review_packets.py` and
  `scripts/export_pending_review_packets.py` construct a deterministic
  **twelve-PR reviewer-only** packet from the original manual shortlist,
  preserving PR URLs, base/head/merge SHAs and changed source/test paths,
  validated via the existing `task_admission.py` gate checker.
- All 12 packets have exactly **eight pending evidence gates**, for **96
  pending / 0 approved / 0 admitted executable tasks**.
  These are NOT agent-visible pre-fix prompts: post-PR references and
  test-path metadata could leak solution information.
- GitHub CI now builds and validates a third small source-free artifact
  `ucode-admission-review-only-v1`, alongside the cleaned QC bundle,
  conservative lineage graph ZIP, and source-only Overleaf bundle.
- `paper/overleaf/main.tex` includes a Methods explanation of
  how the pending packet population and 96-gate denominator
  were created without fabricating human approvals.
- [Reviewer packet protocol](PENDING_TWELVE_TASK_REVIEW_PACKETS_2026-10-27.md).
- **Verified intermediate CI:** [run 40428768615](https://github.com/Rocky5502/U-CODE/actions/runs/40428768615)
  passed **731/731 offline tests on Python 3.10 and Python 3.12**.
  Subsequent README/handoff edits require final-head CI.

---

## 27 OCTOBER 2026 — CROSS-ROLE LINEAGE AUDIT & EXTERNAL-METADATA HARDENING

**Supersedes the earlier dataset claim of 707 offline tests.** Always
refresh live `main` CI and current source hashes before a new sprint.

- [Conservative leakage graph](../src/ucode/lineage_risk_graph.py),
  [offline graph runner](../scripts/audit_lineage_risks.py),
  [SHA256 re-verifier](../scripts/verify_lineage_review.py),
  [adversarial tests](../tests/test_lineage_risk_graph.py)
  and [methodological ledger](PR_LINEAGE_REVIEW_2026-10-27.md)
  flag metadata overlap across shared fork-parent, Git commit SHA
  (including head-to-base cross-role) and common GitHub owner.
  Frozen 120-record audit found **nine owner warning edges**,
  zero shared cross-record fork-parent/Git-SHA edges,
  120 provisional candidate provenance components,
  **zero independently adjudicated duplicates or leakage-safe splits**.
  Absence of metadata edges is NOT source-code independence evidence.
- Graph export is a **separate four-file reviewer artifact**
  `ucode-lineage-review-only-v1`, alongside (NOT merged into)
  the eight-file `ucode-pr-metadata-clean-v1` quality release.
  Both outputs are generated and re-verified in GitHub CI.
- [External SWE-rebench V2 intake](../src/ucode/external_dataset_intake.py)
  now handles bounded epoch-millisecond timestamps and string
  timestamps and excludes unsafe foreign spreadsheet formulas/control
  metadata while retaining all exclusions in screening denominators.
  [Input hardening tests](../tests/test_external_dataset_intake.py)
  cover this. Upstream 32,079-row Parquet has NOT been imported.
- [Springer ASE Methods](../paper/overleaf/main.tex) documents the
  nine owner warnings, zero matched source-hint components,
  no frozen split, and safe optional metadata intake. GitHub
  Overleaf sources updated; external live Overleaf remains unsynced.
- **Verified intermediate CI:**
  [run 40428161725](https://github.com/Rocky5502/U-CODE/actions/runs/40428161725)
  passed **726/726** on Python 3.10 and **726/726** on Python 3.12,
  including both source-free output verifier steps.
  Source/doc edits afterward require their own final HEAD CI.
- Still **0 admitted executable tasks, 0 verified real six-model
  inferences, 0 independent held-out oracle trials or attested
  five-dimensional metering**. Do not claim Nature Scientific Data
  submission readiness or one-week full experiment completion.

---

## 27 OCTOBER 2026 — REPRODUCIBLE DATA QUALITY & MULTILINGUAL SOURCE ADDENDUM

**This addendum supersedes earlier statements that U-CODE has only the
pre-cleaning 120-PR CSV or 4-file dataset output.** Recheck `main`
and GitHub CI every turn.

- [Frozen source 120-PR frame](../data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv),
  [12-stratum verified statistics](../data/curated/2026-10-27/frozen_cleaning_summary.json),
  and [source dataset card](../data/curated/README.md):
  120 unique repo names/PR URLs, 119 retrievable, 62
  production-source-path leads, 14 first-pass manual-review
  leads, 12 manually reviewable records, 11 search-versus-changed-language
  mismatches/unobserved; **zero independently approved executable tasks**.
- [Eight-file source-free curation and QC tool](../scripts/audit_dataset_quality.py),
  [recomputed QA](../src/ucode/dataset_quality.py), and
  [independent post-export verifier](../scripts/verify_dataset_release.py):
  reproducible SHA256 of input audit files and seven output files,
  ID/PR uniqueness, exact original SHA fidelity, language coverage,
  metadata missingness, owner/fork/common-base risk warnings,
  no contaminated/hidden evaluator fields or self-approved task flags.
  A SHA256 match does NOT authenticate original GitHub observations,
  individual code licenses, source authorship or independent correctness.
- [Scientific Data technical-readiness ledger](SCIENTIFIC_DATA_READINESS_2026-10-27.md)
  and [standalone data descriptor outline](../paper/scientific_data/DATA_DESCRIPTOR_PRE_SUBMISSION_OUTLINE.md)
  are transparent **NOT SUBMISSION READY** proposals. The current
  metadata is not an AlphaCode-comparable task benchmark or
  validated Nature data resource.
- [Optional SWE-rebench V2 read-only source](../configs/external_multilingual_source_swe_rebench_v2_2026-10-27.json),
  [restricted seven-column local Parquet intake](../src/ucode/external_dataset_intake.py),
  [CLI](../scripts/screen_swe_rebench_v2.py), and
  [provenance/rights warning ledger](SWE_REBENCH_V2_SAFE_DATA_INTAKE_2026-10-27.md).
  Upstream publisher reports **32,079 tasks and 20 repository languages**,
  not newly collected U-CODE tasks. Their gold patches/test identifiers
  MUST NEVER appear in policy-visible ingestion. **Source not
  downloaded or screened yet**, immutable HF revision not frozen,
  per-task rights/oracles not verified; no combined 120+32k dataset.
- Updated `paper/overleaf/main.tex` documents quality controls
  and prospective external source **without empirical model outcomes**.
  GitHub source-only ZIP export is **not live Overleaf synchronization**.
- **Verified intermediate CI:** [run 40399787748](https://github.com/Rocky5502/U-CODE/actions/runs/40399787748)
  passed **707/707 offline tests on each of Python 3.10 and 3.12**.
  Any later commits must be verified separately.
- **Next real scientific gates:** independently adjudicate file rights,
  task-era specifications, oracle secrecy, runnable containers,
  contamination/leakage groups; pin six model revisions, launch approved
  A100 preflights and measure throughput. Do not claim full
  multilingual experiments can finish in a week without these.

---

## 27 OCTOBER 2026 — METERING AND LEDGER-BOUND RESOURCE ACCOUNTING UPDATE

**This section supersedes the earlier statement that the next unblocked task is to implement a metering schema.** The actual **independent physically hardened runner** and authenticated five-component metering remain open.

- [Structural contract](../src/ucode/metering_attestation.py): policy-neutral finite nonnegative token/test/GPU/CPU/wall evidence readings, independently declared counter types, enforced-cap claims, source receipt SHA256-shaped digests, fail-closed missing/zero/unmetered checks. Integer-valued floats (e.g. 2.0) are accepted for whole token/test counts to match ResourceVector; fractional counts still fail. An asserted digest/flag is NOT authentication.
- [Per-action reconciliation](../src/ucode/metering_reconciliation.py): links one structurally checked five-vector to an appended shared session action, matched budget deltas, and pre/post public ledger traces; never accepts correctness priors or hidden oracle labels. All returned authorization/physical-cap booleans are false.
- [First-party bounded Linux subprocess smoke](../src/ucode/metering_attestation.py) only executes fixed Python fixtures with an integer-second CPU RLIMIT and a wall watchdog; it has NO network/filesystem namespace isolation, trusted GPU/token/test meter, robust process-specific CPU attribution or real-task approval.
- [Adversarial tests](../tests/test_metering_attestation.py) and [ledger-bound tests](../tests/test_metering_reconciliation.py) plus the [scientific caveats](METERING_ATTESTATION_CONTRACT_2026-10-27.md).
- **Verified intermediate CI:** [run 40380531997](https://github.com/Rocky5502/U-CODE/actions/runs/40380531997) passed **619 first-party offline tests on Python 3.10 and 3.12**, including structural metering and ledger parity. Later manuscript/README/handoff commits must be checked against their own current HEAD CI.
- Updated [prospective Springer Methods](../paper/overleaf/main.tex) to describe limitations; **live Overleaf was not edited**. No third-party PR code, model inference, sealed independent oracles, signed physical meter, cgroup isolation, or validated reliability gain resulted.
- **Next concrete blocker:** create independent verifiable per-process/cgroup CPU and wall enforcement, controlled engine token and dispatcher test metering, GPU attribution, tamper-evident counter receipts and independently audited rootless network-off test infrastructure; bind those trusted receipts to admitted real tasks, but do not execute untrusted code until all rights/oracle/containment gates pass. In parallel, plan train-only fitting for joint priors and dependence kernels.

---

## 27 OCTOBER 2026 ADDENDUM — LATEST ALGORITHM MILESTONE

**This addendum supersedes historical checkpoint counts and next-step claims
elsewhere in this October 26 handoff.** Always refresh actual main HEAD and CI
before doing further work.

- [Verified algorithm/test run 40362950959](https://github.com/Rocky5502/U-CODE/actions/runs/40362950959):
  **575/575 offline tests on Python 3.10 and 575/575 on Python 3.12**
  at commit `c89ee49c3dfdd2ab8af910172b6a08040e2e3112`.
  The README/manuscript/handoff commits after this test milestone must
  be checked against their own final HEAD workflow.
- The **primary uncertainty-free comparator** now uses a shared
  target-aware action menu, via `src/ucode/matched_opportunities.py`
  and `matched_session.baseline_shared_decision`; it is not allowed
  Bayesian forecasts or evaluator-only labels.
- `src/ucode/joint_conditional_bes.py` supports finite-horizon
  multi-candidate diagnostic/generation/repair planning under an explicitly
  candidate-factorized frozen synthetic transition model.
- The new `src/ucode/correlated_archive_bes.py` is an **optional,
  finite, correlation-aware joint-truth sensitivity-analysis reference**:
  exact Bayes updates over latent candidate acceptability vectors,
  repair-parent-dependent hypothetical production transitions,
  five-dimensional nominal budgets, state/support caps, and a public
  producer-receipt digest to fail closed on accidental reuse of an
  unacknowledged production history. The digest is NOT a certificate of
  correctly refitted joint priors.
- The [correlated algorithm research ledger](CORRELATED_JOINT_TRUTH_2026-10-27.md)
  includes a **constructed same-marginal three-patch counterexample**:
  independent versus anti-correlated truths reverse the selected first
  diagnostic, with synthetic expected utilities 0.50 versus 0.90.
  This is mathematical test evidence, NOT observed software reliability.
- Updated `paper/overleaf/main.tex` contains joint-archive and
  correlation-aware Bayesian equations, symbolic-branch semantics,
  sensitivity analysis and limitations. `references.bib` contains
  published methodological references. GitHub CI exports source-only
  `ucode-overleaf-sources`; **live external Overleaf has not been edited**.
- **No real model execution, no admitted executable tasks, no verified
  independent sealed oracle, no attested five-resource metering, no
  trained/calibrated joint priors, no RQ effectiveness results.**
- **Next falsifiable code gate:** build a policy-neutral, first-party
  *metering attestation contract* and controlled subprocess test harness
  without executing third-party repositories; distinguish independently
  measured wall/CPU counters from model-reported token/test/GPU metrics,
  and fail closed on missing or non-enforced resource dimensions.
  Then prepare train-only fitting/calibration protocol for joint priors
  and cross-candidate residual diagnostic dependence.

---

## A. EXACT NEW-CHAT ACTIVATION INSTRUCTION

ACTIVATE **U-CODE SCIENTIFIC PRINCIPAL-INVESTIGATOR AND ENGINEERING EXECUTION MODE**. You are continuing an existing, actively developed empirical software-engineering research project, NOT starting from scratch. The canonical and already-user-authorized code repository is https://github.com/Rocky5502/U-CODE, branch main. First READ THIS COMPLETE HANDOFF, then the **latest** GitHub README, current commit, CI results, all relevant code/test files, experimental protocol, issue tracker, paper sources and newest research logs. The initial verified checkpoint was main 4d6b9f8f9431e6dd15ce7d0b2766e9be5a2af2f6 with 426 passing Python offline tests; refresh because this document's commit and later work change HEAD.

Work as an integrated *virtual* research team (roles R0–R16 below). Think like an unusually demanding *Automated Software Engineering* editor and SBSE researcher. Do concrete work in THIS request: inspect → identify one highest-value scientific blocker → develop the algorithm or evaluation/data work → implement source and adversarial tests → update manuscript/README/research ledger where justified → commit on GitHub main through connected tools → inspect actual Python 3.10/3.12 CI logs and ZIP artifact → clearly report what is verified and what is not. Never claim background asynchronous work or use fabricated data. A passing offline CI, synthetic oracle, merged Copilot PR, provider model card or unchecked root license cannot be presented as an independent scientific result.

**IMMEDIATE NEXT PRIORITY:** Design and implement a **strong search-optimized uncertainty-free comparator**, not just our already implemented fixed-schedule blind negative control. This search competitor must receive the SAME tasks, candidate-generation opportunities, tools, controller horizon and five-dimensional budgets as U-CODE; it must not consume predicted patch correctness, posterior probabilities, evaluator gold, or hidden tests. Introduce a policy interface and candidate/archive accounting that supports genuinely fair paired comparison with BES (without unintentionally allowing uncertainty through heuristic weights), and prove parity, deterministic seeds, nonleakage and resource caps with adversarial tests. Do not rebrand fixed-schedule blind_search.py as the strong baseline. Then prioritize the separately gated FIRST SAFE REAL TASK: independently cleared file-level rights + frozen pre-fix specification + independently authored hidden oracle + audited rootless network-disabled resource-limited sandbox. No third-party code execution until these preconditions are met. Report realistic limitations.

Maintain the six user-selected LLM checkpoints as prospective inclusions, but model rights, terms, runtime, weight integrity, checkpoint IDs and GPU feasibility are NOT verified. Do not purchase compute or access gated assets without permission. Keep all synthetic fixtures and experiments explicitly labeled. The manuscript Results section stays empty until independently validated outcomes exist.

---

## B. RESEARCH OBJECTIVE AND DEFENSIBLE SCIENTIFIC NOVELTY

### One-sentence hypothesis

At matched allowed coding actions and five independent resource caps, **can calibrated, history-dependent evidence-acquisition and coding-search decisions improve independently verified full-repository-task patch success and selective reliability at nontrivial release coverage, versus a strong optimized search policy that does not use calibrated uncertainty?**

This is a falsifiable hypothesis, NOT an established advantage.

- Inputs: immutable pre-fix repository issue and task context, policy-visible source/retrieval, optional current patch candidate(s), historical visible diagnostics, action/tool menu, remaining budgets and frozen training-only predictive models.
- Nonterminal actions: GENERATE, REPAIR, TEST, RETRIEVE, STATIC_ANALYSIS; terminal actions: RELEASE or ABSTAIN. No action may see hidden evaluator tests, gold patches, post-treatment labels or later PR content.
- True evaluator-only correctness of released patch: Y_i(x) in {0,1}; optional separately verified security condition G_i(x). Do not combine security with functional correctness unless both gold oracles independently exist.
- Five resource components B = (LLM tokens, test calls, GPU seconds, CPU seconds, wall seconds); enforce every dimension componentwise, using **actual measured** costs in real trials. Arbitrary scalar cost prices are only predeclared planning preferences, NOT a substitute for hard bounds.
- Full-task independently verified success S(pi) = E[1(release) * Y]; release coverage C(pi)=Pr(release); wrong-release conditional risk R(pi)=E[1(release)*(1-Y)]/C(pi) for C(pi)>0. Risk is **undefined** at zero coverage. Require a meaningful coverage floor C_min>0 and transparent risk/coverage tradeoff.
- Baseline priority: conditional BES vs strong UNCERTAINTY-FREE OPTIMIZED SEARCH; additional independence/no-search/fixed-testing/selective-verification/MCTS/replay and credible fidelity-audited external methods.
- Valuation nuance: tests/static analysis/retrieval can convey information (EVSI) but DO NOT add fictitious candidate hypervolume. Generate/repair can add/replace candidates. EHVI candidate creation is limited to generation/repair.
- Reference Bellman/EVSI is established mathematics. Ordinary optional Bayes value of information is nonnegative; a **mandatory posterior-gated release** can exhibit negative *signed* EVSI, as worked mathematically in the code/docs. Neither observation is an empirical result.
- Correlated diagnostics: multiplying marginal likelihoods as if independent can double-count correlated tests. Existing conditional likelihood table is a reference for one candidate and must be fitted to genuinely independent, train-only data before claims.
- Risk thresholds alone are not statistical risk certificates; optional stopping, distribution shift, adaptivity, nonexchangeable repositories and selection bias matter.
- Distinguish from user's concurrent **OpenCoderX-E** (correlation-aware candidate search/evidence graphs) and **CALM-SE** (coding-agent sequential interventions), documented at docs/PROJECT_BOUNDARIES.md. Avoid duplicate submissions, leaked/shared held-out cohorts, copied claims, and text recycling.

### Research questions (RQ1–RQ6)

RQ1: Real attributable AI-code correctness/security/quality failure landscape, repository/fork grouped.  
RQ2: Calibrated pre-outcome uncertainty and prediction transfer across repositories/languages/models (Brier, ECE, AUROC, AURC, risk-coverage).  
RQ3 (**primary**): Paired independent verified full-task success and cost for uncertainty-guided BES vs **strong equal-budget uncertainty-free optimized search**.  
RQ4: Which intervention type is valuable and when? Separate evidence acquisition from candidate creation; trace costs, selection bias and controls.  
RQ5: Out-of-distribution cross-project, language and model-family generalization; cluster-based intervals and observed attrition.  
RQ6: Causal/mechanism ablations — conditional vs independent diagnostics, calibration, search/beam/archives, retrieval, repairs, release gate and abstention; calibrated vs shuffled/noninformative predictions.

A serious research article needs negative-result reporting, exact leakage-safe task scope, fair competitor tuning and independent oracles, not merely many green unit tests.

---

## C. VERIFIED REPOSITORY STATUS AT HANDOFF

- **GitHub main at start of handoff:** 4d6b9f8f9431e6dd15ce7d0b2766e9be5a2af2f6.
- **CI:** 40179406607, passed 426 first-party offline unit tests **on EACH Python version** (3.10, 3.12). The source-only Overleaf ZIP artifact is generated. The handoff commit should trigger a later run; inspect its result.
- **Repo source tree:** about 208 Git tree entries at this checkpoint; important dirs src/ucode/, tests/, scripts/, docs/, data/, configs/, paper/overleaf/, literature/, examples/. Use live tree to determine exact current status, not this number forever.
- **24-item primary-source dated novelty matrix** literature/novelty_matrix_2026-10-24.csv; several later primary references were added to paper/overleaf/references.bib. Review citation keys via actual bibliography; the historical README mentions an older "16 references" figure that may be stale.
- **GitHub README** has a camera-ready scalable SVG at docs/figures/ucode-framework.svg. Arrow-direction validator and tests verify 5 policy arrows, return loop, lower evaluator lane and strict role boundaries. Figure depicts **prospective architecture**, not an implemented fully integrated deployed SE agent.
- **Code after previous baseline block:** fixed-schedule uncertainty-blind control, static action parity audit, synthetic replay config/examples are implemented, documented, unit-tested, in README and Springer main.tex; **NOT an optimized uncertainty-free search policy**.

### Concrete code map (READ implementations, not just labels)

**Algorithms and policy:**  
- src/ucode/voi.py — one-step binary diagnostic Bayes value (toy analytical reference).
- src/ucode/acquisition.py — EHVI only for generate/repair, not test/retrieval/static-analysis as invented candidate solutions.
- src/ucode/vector_policy.py — forecast-based single-step decision with five independent hard budgets and planning-only scalar resource prices.
- src/ucode/budgeted_belief_search.py — finite-horizon one-active-candidate BES; generate/repair may replace it; independently declared marginal diagnostic model; explicit conditional independence assumption when multi-probe.
- src/ucode/conditional_bes.py — history-conditional diagnostic likelihoods for ONE current candidate, diagnostic actions only; not yet a joint conditional generator+repair+retrieval multi-candidate planner.
- src/ucode/belief_session.py — closed-loop policy-visible planning reference with visible observations.
- src/ucode/conditional_fit.py and diagnostic_fit.py — training-only diagnostic likelihood estimation and group checks; prior success probability calibration/real trained kernels still not established.
- src/ucode/blind_search.py — **implemented deterministic uncertainty-BLIND fixed schedule**, actions generate/retrieve/test/static_analysis/repair then release/abstain; candidate SHA256; single-use tools; visible boolean diagnostics; on repair old patch observations invalidated; no probability/hidden label fields. Useful NEGATIVE CONTROL, NOT strong primary search comparator.
- src/ucode/matched_action_inventory.py — static action ID, kind, five-cost and initial-budget parity with BES; sorted deterministic SHA256 digest excludes BES-only forecasts and blind-only priorities. Does NOT prove prompts, checkpoint IDs or actual real inference parity.
- src/ucode/agent.py, search.py, uncertainty.py, simulation.py, ollama.py, cli.py — older research scaffold; inspect before integration or public claims.
- src/ucode/spec_ambiguity.py — explicit first-party mathematical nonunique Go odd-payout witness; NOT test of Go repository code or evidence of bug.

**Task/data integrity and evaluator:**  
- src/ucode/audit.py and scripts/summarize_audit.py — canonical read-only PR metadata screening (NO external repo source execution).
- src/ucode/review_queue.py and scripts/triage_review_queue.py — 62 source-path hits ranked into manual review leads; never marks an experiment eligible.
- src/ucode/task_admission.py and scripts/check_task_admission.py — eight fail-closed admission evidence gates; even a complete self-reported dossier requires separate independent sign-off.
- src/ucode/evaluator_boundary.py and scripts/check_evaluator_boundary.py — strict agent-visible metadata allowlist, evaluator-only prospective gold references, no PR-authored tests admitted as hidden oracles. Metadata separation does NOT guarantee physical OS isolation.
- src/ucode/experiment_contract.py — frozen task x model x seed x budget x policy matrix, policy receipts with no correctness labels, evaluator verdicts tied to exact released patch hash, matched pre-fix base/model/toolset/environment, five measured caps, no dropped runs.
- src/ucode/evaluation.py — full-task verified success, release coverage, conditional wrong-release risk, paired repository/fork cluster bootstrap for qualified results.
- src/ucode/attrition_bounds.py — worst/best paired success bounds when infrastructure outcome unknown; abstain/timeout/safety stop count zero full-task success separately; **bounds are NOT confidence intervals**.
- src/ucode/model_readiness.py — gate for the six selected checkpoints, immutable model/tokenizer revision, license/terms, engine, VRAM and sandbox checks. Currently none is ready.
- src/ucode/task_gate.py — earlier provenance/executability input gate; reconcile with newer dossier contract without bypasses.

**Reproducibility / examples:**  
- examples/bes_lookahead_smoke.py, conditional_dependence_smoke.py, blind_search_smoke.py, action_parity_smoke.py, pilot_oracle_boundary_smoke.py — SYNTHETIC/analytical, not real model task benchmark outcomes.
- configs/blind_search_synthetic_schedule_2026-10-25.json — synthetic generate→retrieve→test(fail)→repair→test(pass)→release trace, no actual oracle.
- scripts/validate_sbse_protocol.py — validates six-model/eight-policy PROSPECTIVE setup and no fake completed outcomes.
- scripts/export_overleaf.py — produces deterministic, source-only Springer LaTeX ZIP with hashes; excludes third-party class, secret/model/data files.
- .github/workflows/ci.yml — first-party offline tests on 3.10/3.12, figure/model/audit/admission/evaluator/plan integrity checks, smoke examples, source-only Overleaf ZIP upload.

### Data and real provenance screen — EXACT observed counts

Frozen discovery file: data/discovery/agent_pr_candidates_120.csv — 12 GitHub repository-primary-language search strata x 10 PR links associated with Copilot SWE agent. These are **links, not 120 independent AI-generated repositories/tasks**.

**120 attempted; 119 metadata retrieved; 1 inaccessible (#26).** Of the 119 retrieved:  
- **62** production SOURCE **path** hints (suffix/path classification, NOT proven bot-authored code or executable solutions);  
- **10** test-only source PR changes;  
- **45** non-source changes;  
- **2** empty changed-file lists requiring review.  
Among 119 retrieved metadata records: **62** recognized repository-level SPDX tags, **12** forks. Repository license is NOT file-level redistribution authorization. No merged PR is independent correctness evidence.

All source audit JSONL: data/audits/2026-10-24/ (later rows still in that frozen folder); full summary docs/logs/2026-10-25_complete_120_pr_screen.md. First-pass manual queue finds **14** leads under heuristics, not 14 qualified tasks; 2 deep commit/patch cases in data/audits/2026-10-25/deep_pr_manual_review_2.jsonl, neither eligible. Other possible public datasets (AIDev, SWE-chat gated, DroidCollection, SWE-rebench, EffiBench-X) have different units/licenses; do not merge as a 120-task trial.

**Two real pinned pre-fix PILOT DOSSIERS, ZERO admitted tasks:**  
1. candidate #104: https://github.com/mvdbos/php-spider/pull/172 — PHP persistence/cache file layout. Original issue https://github.com/mvdbos/php-spider/issues/168; base 25e9b1cf855669c24ba1609c7d4cfcda17ac6217; head 40cdfdb4d7b6eb8afebbd548ea87c7ed4805808a; merge e676149d0b7b61cee61424dfa849d03ceffb7070. Root MIT observed; file-specific rights not approved. PHP >=8.2, PHPUnit 11 dev declared in original composer, not a pinned tested installation. The original public issue URL is mutable; no independently verified immutable pre-PR spec blob.
2. candidate #43: https://github.com/PlayHuai/eighty-point-huai-an/pull/30 — Go game settlement/scoring, ranks and DB writes. Original issue https://github.com/PlayHuai/eighty-point-huai-an/issues/29; base ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a; head e06b7e5fad881f4d34752eaf98615f84dbf57db3; merge e409eb6d91507dff78bc7bcfb54d4da828e02a53. Root MIT observed; file-specific rights pending. Pre-fix docs/design.md blob b566ca7627b6518670a866a6a637bd5257e947f4 gives some human-facing requirements. Odd recovered-pool winner residual assignment is not uniquely fixed by zero-sum and nonnegative loser balances: for pool 5, even imposing an added hypothetical near-equal fairness restriction, both (2,3) and (3,2) are viable. An independent domain reviewer must approve a tie-break or acceptable-output set; do not copy the PR author's chosen answer into "gold". DB idempotency/transactions are not validated by a narrow numeric microtask.

Canonical pending dossiers: data/admission/2026-10-25/pilot_dossiers.jsonl. Prospective evaluator registrations: data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl. **All 16/16 evidence-gate instances PENDING across the two candidates**: pre-fix reconstruction, agent/human line attribution, file rights, independent functional oracle, hidden oracle/split, sandbox isolation, pinned toolchain, resource caps.

We HAVE NOT cloned/executed those external repos in GitHub Actions, downloaded full model weights, fitted real model risk oracles, verified task success, purchased GPU, or obtained signed independent review. **Scientifically admitted real task count = ZERO.**

### Six accepted LLM checkpoints — exactly these, five publisher families

1. Qwen/Qwen2.5-Coder-7B-Instruct
2. Qwen/Qwen3-Coder-30B-A3B-Instruct (MoE: active params ≠ total stored weights; high memory feasibility gate)
3. mistralai/Devstral-Small-2-24B-Instruct-2512
4. deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
5. google/codegemma-1.1-7b-it
6. meta-llama/Llama-3.1-8B-Instruct

Canonical selections: configs/accepted_six_model_study_2026-10-25.json; requirements docs/SIX_MODEL_STUDY_PLAN_2026-10-25.md. These were ACCEPTED BY RESEARCHER **FOR STUDY PLANNING**, not downloaded or run. Distinguish Apache-2.0 advertised Qwen/Mistral cards from DeepSeek-specific license, Gemma and Llama access/license terms. Check actual provider cards afresh; full license text, approval/access, weight integrity, snapshot revision, inference engine and measured peak VRAM required. Six checkpoints count as FIVE publisher families because both Qwen models are Qwen. No pay-per-token API or rented GPU is approved by this project merely because models were selected.

### Prospective eight-policy comparison

Canonical configs/confirmatory_sbse_protocol_2026-10-25.json; docs/SBSE_CONFIRMATORY_EVALUATION_AND_FALSIFIERS_2026-10-25.md.

- Primary **ucode_conditional_bes** vs **no_uncertainty_search** (the latter MUST become a genuinely competitive search-optimized baseline; current blind_search is only an extra fixed-schedule control).
- Controls/ablations: ucode_unconditional_bes, uncertainty_only, fixed_testing, selective_verification, mcts_search, replay_search.
- External very close verifier methods RETRACE, Dockerless and SWE-Verifier require *faithful audited adapters* before using names as actual benchmarks; no such external adapters have been run.
- Illustrative ONLY proposed pilot resource ceiling: 30,000 tokens; 20 test calls; 3,600 GPU seconds; 1,800 CPU seconds; 3,600 wall seconds. **Not approved, measured or frozen**. Example seeds [11,29,47] are also NOT locked experimental assignments.
- Compare identical pre-fix task, frozen model checkpoint, seed, allowed tools, execution environment, candidate-generation opportunities and five independent resource caps. Different actual consumption is an outcome; no hidden oracle to either policy. Explicitly report infrastructure missingness, safety stops, timeouts and all exclusions.
- Primary intention-to-treat verified full-task correctness; also release coverage, wrong-release risk among releases, resource use and paired effect with independent repository/fork-group uncertainty. The current synthetic "improvement" in unit tests is mathematically invented and MUST never appear in Results.

---

## D. Springer MANUSCRIPT / OVERLEAF STATE

Canonical version-controlled manuscript: paper/overleaf/main.tex (roughly 52.6k characters at verified checkpoint), paper/overleaf/references.bib, paper/overleaf/README.md. Companion paper/OUTLINE.md and researcher report docs/DEEP_RESEARCH_SYNTHESIS_2026-10-24.md.

The LaTeX starts with \documentclass[pdflatex,sn-basic]{sn-jnl}; Springer official submission guidance: https://link.springer.com/journal/10515/submission-guidelines; official publisher template: https://www.overleaf.com/latex/templates/springer-nature-latex-template/myxmhdsbzkyd. It has Introduction, Related Work, Problem Formulation, Prospective U-CODE Method, Data Provenance and Experimental Design, empty Results, Discussion/Threats and Conclusion. It includes formal release risk/coverage, Bellman/EVSI, history-dependence, metadata PR attrition table, a PHP/Go pilot case distinction, evaluator-only boundary, Go ambiguity equation, six-model/eight-policy plan, matched policy receipts, missingness bounds, and the blind negative control/action-parity equation. Most recent paper update includes blind-search limitations.

**DO NOT insert fabricated measurements or claim Springer compilation.** Official publisher sn-jnl.cls/BST files are not vendored; from a bare repo the journal LaTeX source has not been confirmed to compile into a final PDF. No authenticated live Overleaf edit has occurred. GitHub Actions instead attaches a **source-only** ucode-overleaf-sources ZIP; verified latest successful prehandoff run's artifact: https://github.com/Rocky5502/U-CODE/actions/runs/40179406607/artifacts/12593740402. This ZIP is **not** an Overleaf account sync, not a camera-ready compiled paper, and is not a validated submission.

Related literature MUST respect novelty threats and include primary citations, e.g. SWE-Search (MCTS), GA4GC, SWE-Replay, SWE-Verifier, negative uncertainty-only correction, SWE-Critix, Teaching Agents to Code Reliably, RETRACE, Dockerless (EMNLP 2026), SWE-Bench Pro Verified. The 24-item CSV is dated and newer manuscript references may not appear in it; synchronize and verify source metadata before formal related-work claims. Prefer original papers, correct publication/preprint designations, protect BibTeX keys.

Target Springer journal research standards: substantial algorithmic contribution and/or novel generalizable empirical insight, appropriate multiple baselines, real reproducible tasks, sensitivity and confidence/statistical audit, ethics, source rights, author disclosures. Real results are required before deciding submission readiness. No fictitious reviewers.

---

## E. PEOPLE, HARDWARE AND WORKFLOW ASSUMPTIONS

**Lead researcher:** Chandan Kumar Sah, PhD researcher at Beihang University, School of Computer Science and Engineering; author listed in main.tex. Human coauthor/supervisor commitments must be verified directly; virtual reviewer personas are NOT actual coauthors or signed referees.

Potential local resources described in earlier chats (NOT remotely accessible by default): Windows PC1 with RTX 5070 Ti 16 GB / ~64 GB RAM, a Windows+WSL2 Ubuntu 22.04 PC2 with GPU/Docker, and an Apple M2 8 GB Mac for offline analysis; optional separately approved A100-80 GB resource. **Never assume an attached live shell on these physical machines**, an available API key, downloads of model weights, access to external project directories, GPU affordability or ability to rent/buy resources. Confirm actual state and approval before requiring machine execution. The user values direct GitHub main commits and auditable work; no background execution promises.

CLI on a trustworthy local clone with Python package installed (do not run third-party project source):
    python -m pip install -e .
    python -m unittest discover -s tests -v
    python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --manifest data/discovery/agent_pr_candidates_120.csv
    python -m scripts.triage_review_queue --limit 12
    python -m scripts.check_task_admission
    python -m scripts.check_evaluator_boundary
    python -m scripts.validate_sbse_protocol
    python -m examples.bes_lookahead_smoke
    python -m examples.conditional_dependence_smoke
    python -m examples.blind_search_smoke
    python -m examples.action_parity_smoke
    python -m scripts.export_overleaf --output dist/UCODE_Overleaf_sources.zip

CI workflow .github/workflows/ci.yml supplies the authoritative git-commit-specific offline test count and Overleaf ZIP; inspect logs instead of inferring tests from filenames. Never force-push, remove prior experiments, leak keys or silently change core held-out cohort.

---

## F. VIRTUAL RESEARCH TEAM: R0–R16

These are simulated perspectives of one assistant, not real independent human approvals.

| ID | Responsibility / mandatory deliverable |
|---|---|
| R0 PI / scientific director | Own falsifiable novelty, prioritize blockers and go/no-go decisions; dated evidence log |
| R1 senior SBSE algorithm theorist | Policy state/action/constraint formalism, genuine search method vs baselines, complexity and falsifiers |
| R2 uncertainty/calibration lead | Risk estimator, Brier/ECE/AURC, dependency, train/validation/eval group separation |
| R3 agent architect | Honest code generation/retrieval/diagnosis/repair pipeline with typed traces |
| R4 multilingual SE lead | Language-appropriate toolchains, no mixing repository-primary and changed-source languages |
| R5 AI authorship/provenance forensics | Issue/base/head/merge and line-level human-vs-agent evidence, data exclusion reasons |
| R6 licensing/ethics and governance | File-specific rights, model/provider terms, privacy and artifact release checks |
| R7 sandbox/threat modeling lead | Disposable rootless network-off container, host mount and secret isolation, measured caps |
| R8 statistician & experimental design | Paired primary estimand, clustered uncertainty, missingness, coverage, multiple testing |
| R9 GPU/LLM systems engineer | Six checkpoint identity/loader/license/hardware validation and real cost telemetry |
| R10 reproducibility engineer | Immutable manifests, CI, determinism, replay, artifact IDs/checksums |
| R11 research librarian / novelty auditor | Live recent primary-source prior art and comparisons, accurate BibTeX |
| R12 Springer paper editor | Strong SE contribution narrative, validated equations/tables/figures/citations/template |
| R13 skeptical SBSE algorithm reviewer | Challenge novelty, tuned competitor strength, fairness and search state design |
| R14 skeptical empirical-SE reviewer | Challenge unit of analysis, causality, sample and oracle completeness |
| R15 skeptical stats/security reviewer | Challenge confidence and risk guarantees, selection bias, leakage and sandbox claims |
| R16 associate editor / meta-reviewer | Decide reject/major revision/ready based only on reproducible real evidence |

Role order: R0/R1/R8 plan; R5/R6/R7 approve evidence and safety; R2/R3/R4/R9 engineer/execute; R10 independently verify reproducibility; R11/R12 document; R13–R16 issue adversarial critique. Never self-label role-play as an independent audit.

---

## G. WHAT IS DONE VS NOT DONE — VERY IMPORTANT

**DONE and auditable at last prehandoff GitHub checkpoint:**
- Scholarly novelty/formal work, ~24-entry dated primary-source map, Springer prospective paper, GitHub project and issue tracker.
- Full **120/120 PR links** attempted and canonical metadata attrition 62/10/45/2/1; 14 first-pass *manual* leads; 2 pinned authentic PHP/Go task dossiers.
- Multi-stage first-party research code: VOI, vector policy, one-candidate BES, conditional correlated-diagnostic reference, training-only likelihood fitting scaffolds, exact offline search math, blind fixed-schedule negative control, action-inventory static parity, provenance/rights/evaluator metadata gates, paired study receipt/attrition statistics.
- Original SVG framework figure embedded in README, vector/camera geometry checks.
- Six prospectively selected checkpoints/five publisher families and prospective eight-policy study protocol.
- **426 green offline Python tests per version** at commit 4d6b9f8f9431e6dd15ce7d0b2766e9be5a2af2f6, run 40179406607; manuscript source-only ZIP artifact.

**NOT DONE — DO NOT IMPLY IT IS:**
- Independently rights-cleared, sealed-oracle, safely executable actual code-repair benchmark tasks (currently **zero**).
- Signed human reviewer/legal/independent oracle attestation and physical sandbox security audit (0 of 16 pending gates passed).
- Fully trained/evaluated patch prior risk model and conditional diagnostic kernel on disjoint real data.
- Unified multi-candidate end-to-end coding agent with real candidate archive and calibrated multi-step generation/repair transitions.
- **Strong tuned uncertainty-free search baseline** (blind_search is a fixed-schedule control), faithful MCTS/replay/RETRACE/Dockerless/SWE-Verifier adapters.
- Real full six-model weights/checkpoint revision pins, provider terms, verified loaders, measured GPU feasibility, actual task run outputs.
- Measured success, risk, coverage, calibration or cost improvement, confidence/significance statements or valid distribution-free selective guarantees.
- Authenticated live Overleaf update, publisher-class compiled final PDF, real journal submission or acceptance.

**Do not infer project completion percentage** from unit tests or number of source files. Code correctness and experimental evidence are distinct.

---

## H. IMMEDIATE ROADMAP IN STRICT SCIENTIFIC PRIORITY

### Next code work block (highest executable, no external-source risk)
1. Refresh HEAD, CI, README, scripts, current action parity, release gates and manuscript (do not rely on this handoff's SHA if main advanced).
2. Implement stronger **search-optimized uncertainty-free primary comparator** on equal candidate/tool opportunities and budgets. Include a candidate archive when truly supported, deterministic action ranking on uncertainty-independent observables, beam/MCTS/heuristic variants only when scientifically warranted, no access to latent success probabilities, diagnostic forecast sensitivities/specificities, post-outcome oracle or gold patch. Distinguish weak blind fixed schedule from strong optimized search policy in API, docs, config and paper.
3. Harden shared action *execution* interface and matched-resource budget telemetry in first-party tests; encode candidate SHA and evidence invalidation correctly; explicit static-vs-actual parity limits. Compare conditional BES and control on a first-party *synthetic* simulator for algorithm debugging only; add counterexamples where U-CODE fails so optimistic assumptions are visible.
4. Commit implementation, tests, updated README/manuscript, update GitHub issue #4 and #6. Validate latest CI 3.10 and 3.12 plus source-only manuscript export.

### First authentic experiment prerequisites (CRITICAL scientific bottleneck)
5. From the 14 human-review leads and PHP #104 / Go #43 dossiers, independently verify changed file licensing, pre-fix historical spec, actual AI/human line attribution, fork-group separation and no hidden gold contamination. Exclude unsuitable tasks transparently.
6. Have an **independent** task reviewer design and attest a held-out functional oracle from pre-fix requirements; resolve Go payout odd-remainder ambiguity and clarify microtask/full-PR equivalence. Seal oracle artifacts outside policy-visible task space. Do not use PR-authored tests as gold.
7. Have a separately audited sandbox with no host/network/credentials and rootless execution, write/resource/time caps and reset attestation. The ordinary first-party CI is NOT such a sandbox. Execute no external program before proper authorization.
8. Review six model licenses/access; freeze real HF model/tokenizer snapshots and engines; benchmark actual memory, tokens/sec and GPU/CPU/wall resource costs in the authorized environment, starting with a realistic smaller model. Never claim every selected model fits RTX 5070 Ti 16 GB.
9. Fit prior patch-success model and conditional diagnostic likelihoods **using training labels only**, separate calibration/validation from untouched held-out repository/fork evaluation.
10. Freeze true paired task-model-seed-budget-policy experiment; start with the smallest independently cleared real pilot. Report full assigned denominator, terminated/abstained/failure cases, actual five-vector costs and evaluator-only outcomes. Add strong controls and ablations if pilot justifies scale-up.
11. Only after results: determine realistic independent-task sample size and hierarchical confidence/uncertainty analysis, replicate across languages and all six model checkpoints, perform R13–R16 critique, complete Springer template/package/ethics/overlap checks, and submit if science supports it.

### Go / no-go rules
- If no approved file-level rights or isolated runner, STOP third-party execution, but continue first-party algorithm and review tooling.
- If no independent hidden oracle, STOP correctness claims.
- If optimally tuned uncertainty-free search matches or dominates BES, report it; change scientific theory only based on legitimate evidence.
- If coverage collapses to zero, DO NOT call conditional risk zero or state U-CODE is safe.
- If an improved result exists only because BES used more tokens/tests/tools, reject comparability and rerun fairly.
- If no realistic sample or model hardware, report scope limits; do not manufacture 80–120 eligible repositories, 2–5 GB dataset or complete six-model experiments.

---

## I. 30-MINUTE WORK-BLOCK FORMAT AND REQUIRED LAST ANSWER

Execute one focused, user-triggered block at a time (not silently in the background):

1. CURRENT STATE: date, HEAD SHA, CI run and actual test count by Python version, key files read, prior gate status.
2. HYPOTHESIS / WHY THIS STEP: which reviewer concern or scientific blocker it resolves.
3. ACTION: actual source/tests/data read or written and live/authorized external tool calls.
4. VALIDATION: source and actual CI logs, unit count, seeded synthetic vs real data, exact action/resource and oracle limitations.
5. RESEARCH INTEGRITY: note all assumptions, safety and rights gates, no fake model inference or real-paper results.
6. COMMIT and ARTIFACT: GitHub SHA/link, issue changes, actual Overleaf source export link, live Overleaf status.
7. NEXT FALSIFIABLE BLOCK: one concrete next task and exact inputs/gates, not vague assurances.

Answer directly, keep links useful, do not repeatedly ask for information already established in this document. You may obtain fresh GitHub status and literature through supported tools and make best-effort advances in one turn. Do not promise autonomous continuous work when no scheduled task has been created.

**YOUR FIRST NEW-CHAT RESPONSE SHOULD BEGIN:** "I have resumed U-CODE from the October 27 addendum. I am verifying the latest main branch and Python 3.10/3.12 CI, then addressing the next scientifically falsifiable blocker while preserving all prior synthetic tests, the matched uncertainty-free comparator, and the factorized/correlated joint Bayesian planners." Then carry out the work, not just offer a plan.
