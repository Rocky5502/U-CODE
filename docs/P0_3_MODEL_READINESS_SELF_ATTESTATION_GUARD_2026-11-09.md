# P0-3 model-readiness self-attestation boundary — 9 November 2026

**Status: VERIFIED FIRST-PARTY SOURCE HARDENING ONLY. Zero external model approvals, zero real GPU observations, zero model inferences, zero eligible executable tasks.**

## The issue and the exact repair

Before this change, the model-readiness checker treated a self-edited planning JSON object as sufficient to set a model report's `runnable` property. A synthetic object with `full_license_review: APPROVED`, guessed 40-hex weight/tokenizer SHA strings, a 64-hex chat-template hash, an arbitrary engine label, a fabricated VRAM measurement and two `true` flags for model weights and sandbox could produce `runnable = true`. These are only **format checks on caller-provided fields**; none authenticates a weight file, a legal decision, an independently observed runtime or any professional reviewer.

The October model roster is a **prospective planning register**, not an execution trust store. Treating editable labels as runtime permission risks falsely claiming a qualified model or overstating empirical readiness in the Springer manuscript.

This change enforces the following hard boundary in [the planning validator](../src/ucode/model_readiness.py):

1. Every planning model receives an immutable **missing independent model/runtime attestation** blocker, regardless of what the JSON values assert.
2. The report's `runnable` property is **always false**, including when a caller manually constructs `ModelReadiness(model_id, True, ())`. This is deliberate: a **planning object is categorically not an execution certificate**. A separately controlled and independently authenticated runner must eventually use a different approval channel.
3. Fake positive flags in a source-controlled JSON add a separate `self_reported_approval_not_authenticated` warning; they cannot make a model executable.
4. A planning record that claims `inference_execution_status = COMPLETED_AND_AUDITED` or a nonzero number of authenticated real task runs is rejected, rather than treated as progress.
5. The [phase-0 preflight](../src/ucode/real_trial_phase0.py) and [research critical-path audit](../src/ucode/critical_path.py) reject an unverified model report whose mandatory independent-evidence blocker has disappeared, as well as claims of runnable models.

No new signed keys, attested GPU profiles or alternate approvals were created. This change closes one **source-code reporting bug**, not a runtime security boundary; someone able to modify and execute the Python application can still modify its code. Actual trusted enforcement belongs to a separately secured execution host, not GitHub CI.

## Reproducible regression tests (synthetic only)

```bash
python -m unittest discover -s tests -p 'test_model_readiness_self_attestation.py' -v
python -m unittest discover -s tests -p 'test_model_readiness.py' -v
python -m unittest discover -s tests -p 'test_real_trial_phase0.py' -v
python -m unittest discover -s tests -v
```

The new tests attempt all-six synthetic "fully approved" manifest flips; every individual fake license/weight/runner approval; forged direct dataclass instances without blockers; manually injected counterfeit preflight reports; a claimed completed real-model run; improper report types; bogus nonzero experiment counts and a changed model identity. They should all fail to create a model-execution permit. All invented test hashes and runtime flags are **first-party synthetic counterexamples**, not observed data or approved reviewer evidence.

## What remains for independently eligible real work

- Six exact approved model weight revisions, tokenizer revisions and chat-template byte hashes, with independently verified file integrity and full license/terms review.
- Gated access eligibility for CodeGemma and Llama as applicable, safe third-party custom-code handling and reproducible engine/precision/quantization.
- Trustworthy observed hardware measurements and sandbox/metering/security approval **outside** the editable planning manifest.
- A separate signed or otherwise authenticated approval process, reviewed by independent accountable operators, to permit controlled model loading on trusted hardware.
- Separate Go #43 / PHP #104 source-era task rights, independent hidden evaluator oracles and a secure authorized task runner before any *real* repair-policy trial.

Neither a public Hub model-card tag nor a plausible SHA proves any of these conditions. The planned six-model/eight-policy/five-budget-vector comparison remains intact; **all real experimental outcomes remain zero and pending**. See the [six-model public card audit](P0_3_PUBLIC_SIX_MODEL_CARD_AUDIT_2026-11-09.md) and [public SHA candidate workflow](P0_3_HF_SHA_REVISION_CANDIDATES_2026-11-09.md). The GitHub Springer LaTeX source is not proof that the live Overleaf has synced or the paper was compiled.
