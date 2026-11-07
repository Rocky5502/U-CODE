# U-CODE focused M4 code review: fit provenance, leakage, validation estimand

**Review date:** 7 November 2026. **Scope:** first-party source for `joint_frequency_fit.py`, `joint_frequency_controls.py`, their synthetic tests and the immediate dependency contracts in `joint_validity_acquisition.py` / `diagnostic_fit.py`. This is not a review of every repository file, a penetration test, third-party license approval, a signed code audit or independent experimental reproduction. No external repos, model weights or evaluator tests were executed.

## Review findings and code changes

| Review ID | Severity for scientific claims | Before repair | After repair | Evidence / test |
|---|---|---|---|---|
| M4-R01 | **High — label leakage / pseudoreplication** | One training candidate per declared `task_id` was enforced, but the **same proposal ID or pre-outcome public snapshot** could be repeated under a different task identity. Validation checked only task hash overlap. | Reject repeated candidate/proposal IDs or exact public snapshot digests within each fitted fold, and reject all three identifiers' overlap between training and validation. Frozen model stores **sorted unique** task, proposal and snapshot digests, checked structurally at construction. | `test_training_candidate_identity_cannot_repeat_under_new_task`, `test_training_snapshot_cannot_repeat_under_new_candidate`, `test_validation_cannot_reuse_training_candidate_or_snapshot`, `test_frozen_provenance_ledgers_must_be_unique_and_sorted` |
| M4-R02 | **High — model-revision confounding** | `model_id` alone could group examples from different model-weight/tokenizer revisions using the same name. The four-way comparator checked the name but not immutable checkpoint identity. | Require a **lower-case SHA-256 checkpoint identifier** on each training/validation row and frozen predictor; fit rejects mixed revisions; comparison requires the exact same checkpoint ID across candidate arms. An additional consistency check rejects contradictory frozen fits for the same model/action/context. | `test_training_checkpoint_drift_is_rejected`, `test_mismatched_checkpoint_revision_refused`, `test_same_context_cannot_stealthily_use_different_training_fit` |
| M4-R03 | **Moderate — validation target mismatch** | The training distribution gives one total vote to each declared repository/fork lineage, but validation provided only task-micro-averaged Brier/log/marginal scores. A large validation repository could dominate the reported metric. | Preserve existing task-weighted numbers for backwards interpretation, and **add distinct equal-lineage macro averages** for categorical Brier, log loss and marginal Brier, plus the average of each lineage's per-marginal absolute gap. Validate with uneven and equal group-size synthetic oracles. | `test_lineage_macro_scores_do_not_hide_repository_size_imbalance`, `test_validation_macro_and_micro_equal_with_equal_group_sizes` |
| M4-R04 | **Moderate — candidate-specific retraining confound** | Two candidates in the **same** frozen public context could silently carry different `training_fingerprint_sha256` and smoothed distributions. | Refuse incompatible fits for an identical action/context/labeling protocol in the same matched acquisition menu. Different predeclared contexts may still have different training fits. | `test_same_context_cannot_stealthily_use_different_training_fit` |
| M4-R05 | **Remaining — not resolved by code-only checks** | Hashes, timestamps, IDs and declared group disjointness are caller-supplied claims. Repositories may share ancestry under different group strings, and a supplied SHA does not authenticate real model weights or labels. | Retain **no-execution / unqualified** status. Require independent ancestry review, actual revision-pinned model/tokenizer artifacts, privately sealed training and evaluation labels, and an attested sandbox. | G5 blocked preflight and open M4/G5 issues, not a CI-passable scientific approval |

## Design notes and scientific guardrails

- **Strict checkpoint digest versus physical checkpoint proof:** the new `model_checkpoint_sha256` is a required **identity assertion** in first-party data schemas. It neither fetches nor hashes actual remote weights. Actual artifact identity and tokenizer/template combinations require a separately reviewed manifest and loading receipts. Synthetic smoke uses a deliberately fake digest with a plainly labeled name.
- **Candidate scope:** repeated proposal/snapshot identities are rejected *within a fitted context/fold*, plus against validation after fit. A future dataset-wide admission stage must also detect cross-context or cross-action duplicates and repository ancestry overlap; this module does **not** solve global ancestry resolution.
- **Validation macros versus true calibration:** task-micro and lineage-macro Brier/log values are proper scoring summaries on supplied validation labels, but neither proves calibration or generalization to target repositories. Report both, include task and group counts, and avoid calling a single mean absolute marginal gap an ECE or formal risk certificate.
- **Candidate validity and missing labels:** `V=0` can coincide with undefined `R,S`. The input contract still correctly rejects absent three-way outcomes rather than silently setting false reliability/safety labels. Before real use, obtain an independent joint estimand or a censoring/missingness model.
- **Fair policy comparisons:** all four source-only acquisitions still use the same pre-outcome marginal probabilities, candidate supports, public Pareto archive, prices and **five hard caps**. Strictly separate them from the registered eight real-policy arms. No actual repo candidate has been verified.
- **Scope limitation:** the fit is a smoothed eight-category **frequency control**; a strong task-conditioned fitted joint model and a more general continuous-outcome baseline remain missing. Nothing in this review converts invented fixtures into results.

## How to reproduce the reviewed code

```bash
python -m unittest discover -s tests -p 'test_joint_frequency_controls.py' -v
python -m scripts.smoke_joint_frequency_controls
python -m scripts.compile_pilot_preflight --require-ready
# The last command MUST return 2 while real external task admission is blocked.
python -m unittest discover -s tests -v
python -m scripts.audit_overleaf_sources
```

All test labels in the reviewed fixtures are invented; the smoke does not measure correctness, robustness, calibrated risk or source authorization. CI pass means the *implemented contract* behaved as tested—not that an external evaluator attested to code quality.

**Next scientific milestone:** independently approved PHP/Go source-era task definitions, rights and actual train/test lineage ancestry; complete task-level R/S/V labels with privacy boundary; immutable verifiable checkpoint/tokenizer references and a five-resource sandbox. Only after this should one freeze and compare a genuinely trained joint predictor against 2-way and 3-way DRPA.
