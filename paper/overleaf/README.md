# U-CODE: Springer Nature / Overleaf working draft (updated 2026-11-07)

**Prospective LaTeX manuscript skeleton, NOT a submission-ready paper.**

## Official journal requirement

- Automated Software Engineering specifically requires LaTeX with
  \documentclass{sn-jnl}:
  https://link.springer.com/journal/10515/submission-guidelines
- Abstract: 150--250 words once results exist.
- Index keywords: 4--6; the current shell has six.
- Single-blind review: use proper identified author data, but confirm final
  authorship and their contributions with the humans involved.
- Springer Nature template:
  https://www.overleaf.com/latex/templates/springer-nature-latex-template/myxmhdsbzkyd
- Submission CFP and deadline (2027-01-30):
  https://link.springer.com/collections/jjcfecffai

## How to use in Overleaf

1. Open the **official Springer Nature** Overleaf template linked above and
   create a project in the user's Overleaf account.
2. Retain the publisher-supplied sn-jnl.cls and bibliography style files.
3. Replace the template's main manuscript file with this main.tex and place
   references.bib beside it.
4. Compile using pdfLaTeX; check errors, missing figures, bibliography,
   publisher macros and declarations.
5. Keep one canonical manuscript source and review conflicts before syncing.
   The GitHub files are the canonical project archive until a sync direction
   and an authenticated Overleaf project are explicitly established.
6. Do not remove verified references or rewrite results without checking logs.

## Limitations

The repository does **not** vendor Springer Nature's publisher class, so
main.tex alone cannot compile from a bare empty Overleaf project; start from
the official template. The current abstract is explicitly prospective, Results contains no empirical
findings, and author declarations remain placeholders. Each must be replaced
or verified before submission.
No direct write to a user's actual Overleaf project has occurred.

## Scientific and manuscript integrity checks (27 October 2026)

The canonical LaTeX manuscript now has a tightened ~200-word
prospective abstract, explicit contributions/falsifiers, corrected
novelty boundaries (SWE-Search, SWE-Verifier, PATSSEL),
history-conditioned evidence equations, and a **one-step
joint-scenario diagnostic-versus-generation allocation equation**
covering the same alternative model scenarios and five measured
resource dimensions. **This is an offline algorithmic reference,
not a fully deployed code-repair agent or a real verified task result.**

The manuscript provides status-only methodological observations
in the Results section; no claims of actual repair-rate gains,
a population risk certificate, completed six-model inference,
or executable 120-repository benchmark are permitted.

Run the source audit before exporting:

```bash
python -m scripts.audit_overleaf_sources
python -m unittest discover -s tests -v
python -m examples.joint_scenario_action_smoke
```

The audit checks Springer `sn-jnl` class declaration, 150--250
abstract-word target, six indexed keywords, every in-text bibliography
key, all equation/figure/table cross-references, balanced LaTeX
environments and unaltered prospective-results integrity.
**Source lint does not compile LaTeX, validate bibliography facts,
read the formatted PDF, confirm peer-review readiness, or sync to a
live Overleaf project.** Existing GitHub CI generates a source-only
bundle after passing the audit. Import that bundle into the official
Springer Nature project, preserve publisher class files and run an
actual Overleaf PDF compile and visual inspection.

The observed dataset stage remains only 120 audited PR metadata
records (12 GitHub query-language strata), **0 independently
admitted executable tasks**. Model weights and GPU inference are
not verified. Paper declarations and contributions still require
human author confirmation.

## Reproducible Overleaf source export from this monorepo

The canonical paper files are `paper/overleaf/main.tex` and
`paper/overleaf/references.bib`. After pulling the current main branch run:

```bash
python -m scripts.export_overleaf --output dist/UCODE_Overleaf_sources.zip
```

This creates a source-only ZIP with the manuscript files at the archive **root**
and SHA-256 checksums; it intentionally excludes third-party source, model data,
Git metadata, secrets, and the publisher's external `sn-jnl.cls`. Within the
**official Springer Nature Overleaf template**, upload/replace `main.tex` and
`references.bib`. Retain the original publisher class and bibliography
style. Source checks and GitHub CI do **not** equal an actual Overleaf compile.

## 6 November 2026: DRPA and real-pilot activation additions

The tracked `main.tex` now includes a restricted dependence-robust
Pareto acquisition (DRPA) derivation, plus a **source-data-grounded**
PHP/Go pilot activation procedure and a two-row, *not-yet-admitted*
gate-status table. The added methods **do not** claim experimental
success, a risk guarantee, source rights clearance or an independently
sealed functional oracle. DRPA is explicitly exploratory and does not
silently alter the registered six-model/eight-policy confirmatory study.

The matching first-party script is:

```bash
python -m scripts.compile_pilot_preflight
python -m scripts.compile_pilot_preflight --require-ready
# The second command must exit status 2 while independent admission is blocked.
```

GitHub Actions' `offline-tests` job now publishes a public-only
`ucode-g5-pilot-blocked-readiness-v1` artifact, and already publishes
the current `ucode-overleaf-sources` ZIP artifact. Both are source
or metadata outputs—not code execution results or automatically
synced live Overleaf edits. Import `main.tex` and `references.bib`
from the ZIP into a publisher-class-backed Overleaf project and
recompile and visually review there.

See [G5/M4 activation requirements](../../docs/G5_M4_REAL_PILOT_ACTIVATION_2026-11-06.md)
and [DRPA assumptions](../../docs/DRPA_DEPENDENCE_ROBUST_ACQUISITION_2026-11-06.md).

## 7 November 2026: exact three-way DRPA validity sensitivity

The source-controlled Springer `main.tex` and `references.bib` now include
the separate exploratory **reliability–safety–validity coupling** formulation,
an independent 2022 SIAM optimal-transport prior-art citation, and a
mathematical source-only action-reversal witness. The new finite LP eliminates
the previous assumption that a prospective candidate's validity is
independent of its reliability and safety. It does **not** prove better
software reliability or security, qualify any previously unapproved
PHP/Go task, or alter the six-model/eight-policy confirmatory registry.

Code and tests are in `src/ucode/joint_validity_acquisition.py`,
`tests/test_joint_validity_acquisition.py` and
`scripts/smoke_joint_validity_acquisition.py`.
See [three-way derivation and limits](../../docs/THREE_WAY_VALIDITY_COUPLING_2026-11-07.md).

**Live Overleaf limitation:** changes are in the GitHub-tracked LaTeX
sources and the CI-produced `ucode-overleaf-sources` ZIP. The separate
cloud Overleaf editor still requires an authenticated project sync or
carefully reviewed upload and publisher-class-backed PDF compilation.

## 7 November 2026: training-only joint-frequency comparator

GitHub `main.tex` now contains an additional **prospective**
group-balanced eight-atom categorical joint model over R/S/V outcomes,
lineage-disjoint train/validation guards, and a fair four-way acquisition
comparison with identical marginal predictions, candidate menus and five
resource caps. `references.bib` adds Gneiting and Raftery (2007) on
proper probabilistic scoring rules.

This controls for simple joint dependence but is **not** a
high-capacity trained neural model or a calibrated coding-agent
benchmark. All current test labels and policy disagreements are
synthetic; the registered primary eight-arm study remains unchanged.
The full modeling limits, including the risk that reliability/security
is undefined for an invalid patch, are documented in
[the M4 joint-frequency methods note](../../docs/M4_TRAIN_ONLY_JOINT_FREQUENCY_CONTROLS_2026-11-07.md).

**Import/sync note:** this updates only the GitHub-tracked LaTeX
source. The GitHub Actions `ucode-overleaf-sources` artifact contains
the latest `main.tex` and `references.bib` bundle; the separate live
Overleaf project is **not** automatically edited or compiled.

## 7 November 2026: M4 joint-frequency code-review corrections

The version-controlled Springer source now records fixes for candidate
pseudoreplication and train/validation overlap, explicit model checkpoint
SHA256 identity checks, and separate **task-weighted versus equal-lineage**
validation Brier and log scoring. These revisions follow the
[focused source review](../../docs/M4_JOINT_CODE_REVIEW_2026-11-07.md)
and are backed by synthetic regression tests.

**Critical limitation:** declared SHA256 identities are not independently
authenticated artifact hashes. Real labelled tasks, a secure evaluator,
true repository ancestry verification and actual model weights remain
unavailable. The new manuscript paragraph describes methodology, not a
measured improvement or acceptance-ready experiment.

The updated `main.tex` and `references.bib` are committed to GitHub and
exported as `ucode-overleaf-sources` by CI. They have **not** been written
into, compiled in or visually checked inside a separate live Overleaf project.

## 7 November 2026: offline A/B reviewer evidence reconciliation

The canonical `main.tex` now includes a methodological paragraph on
**12 candidate PRs × eight admission gates × two independent reviewer
slots** (192 source-review worksheet rows, 96 paired gate categories).
The new local-only review audit distinguishes matching reviewer verdict
categories from matching evidence digests or supporting references,
and refuses to turn agreement into experiment admission.

**No real reviewer submissions have been received or authenticated.**
The mathematical/form validation tests use invented reviewer identities
and fictional evidence; they do not verify ownership, legal rights,
source-era task eligibility, independent oracle sealing or genuine
execution. The separate cloud Overleaf project is **not** edited
by the GitHub source update. CI exports only public manuscript
sources, never private reviewer forms.

Methods and privacy boundaries:
[G5 private reviewer triage](../../docs/G5_PRIVATE_REVIEW_TRIAGE_2026-11-07.md).

## 7 November 2026: independently auditable research critical-path status

The latest [U-CODE progress / remaining-work report](../../docs/UCODE_PROGRESS_CRITICAL_PATH_2026-11-07.md)
is generated from canonical source registries and a verified external-task
metadata preflight. It identifies the ten **full** scientific milestone
exit criteria still lacking independent verification, with four highest
priority P0 dependencies. The count is a **full-exit evidence count, not
an overall percentage of engineering work**.

This progress-management change does **not** insert fake experimental
results into the Springer manuscript, replace trial evidence, or
change the six-model/eight-policy registered primary contrast. The
GitHub LaTeX sources can be exported as `ucode-overleaf-sources` in
CI, but the separate live Overleaf cloud editor has **not** been
synchronized or publisher-template-compiled/visually inspected.

## 7 November 2026: M8 source-era reviewer signature integrity

The repository-tracked Springer `main.tex` now includes a prospective
**detached Ed25519 evidence/immutable-task-binding** protocol directly
after the independent A/B reviewer worksheet method. The code requires
two role-appropriate independent-key signatures for each of eight
source-era task review categories, bound to exact pre-fix repository
identity and declared opaque digest commitments to rights, historical
specification, hidden oracle, sandbox image, dependencies and five
resource meters. `references.bib` contains RFC 8032
(Josefsson and Liusvaara, 2017, DOI 10.17487/RFC8032).

This source-only method and its unit tests use **invented in-memory
reviewer keys and fictional evidence digests**. No human review has
been authenticated. A successful signature check **never** qualifies
a task for execution, opens a hidden evaluator, or changes the
existing six-model/eight-policy prospective design. The PHP/Go
admission report remains 16/16 open.

Verification in CI now installs the optional `[admission]` Ed25519
dependency, runs adversarial test cases and exports
`ucode-overleaf-sources`. This is **not** a LaTeX PDF compile or live
Overleaf edit. Source text was changed in GitHub; the separate online
Overleaf project has not been accessed.

[Read methods, private evidence-handling protocol and genuine blockers](../../docs/G5_SIGNED_EXTERNAL_EVIDENCE_CONTRACT_2026-11-07.md).

## 7 November 2026: complete 13-source dataset + code eligibility audit

The GitHub-tracked Springer `main.tex` now contains a narrowly
scoped **source-only dataset eligibility and configuration** paragraph.
It distinguishes the thirteen source entries (two naturalistic,
four repository task candidates, three snippet-attribution,
three auxiliary training, one efficiency) from the separate 120-PR
discovery metadata frame. It explains that no external source
has been independently rights-cleared, oracle-replayed or run in
the U-CODE evaluation sandbox, and none may populate empirical
effectiveness or cross-language outcome tables yet.

A new [all-source/code readiness report](../../docs/ALL_DATASETS_AND_CODE_READINESS_2026-11-07.md)
and [CLI](../../scripts/audit_all_dataset_readiness.py) verify catalog
grains, source/file identity, representative code scaffolds, and
the model/policy/pilot readiness registries. The old
`configs/experiment_matrix.json` **seven-arm/four-resource**
planning sketch is quarantined with a machine-readable
non-authoritative notice. The registered **eight-arm/five-resource**
confirmatory plan and primary comparison remain unchanged.

CI source lint and the updated `ucode-overleaf-sources` ZIP confirm
only that **GitHub LaTeX source files were updated**. The separate
live Overleaf cloud project was not accessed, synchronized,
publisher-class compiled or visually reviewed as a PDF.

## Direct Overleaf sync (not yet configured)

Overleaf offers authenticated Git integration and GitHub synchronization for
eligible premium accounts: see
https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization

Neither a project ID, Git remote, nor an authenticated Overleaf write connector
has been configured in this ChatGPT workflow. Therefore **GitHub commits here
are NOT automatic writes to the live Overleaf editor**. Overleaf's GitHub sync
requires a user-initiated synchronization; it cannot connect an **existing
Overleaf project** directly to an **existing GitHub repository**. Importing this
entire U-CODE monorepo as a new Overleaf project would copy unrelated code and
data and require main-document reconfiguration, so use the compact paper bundle
unless an authorized, paper-only Git workflow is explicitly set up.

Do not place Overleaf authentication tokens in GitHub files, issues or chat.
If an existing Overleaf document contains newer collaborator edits, reconcile
those before replacing its main.tex. Do not force-push or overwrite blindly.
