# U-CODE: real-task admission work package

**Date:** 2026-10-25. **Scope:** 120/120 completed metadata screening; two read-only real-source leads; **zero executable tasks independently admitted**. No third-party code, Python/PHP/Go build, hidden oracle or LLM was executed.

## Eight-gate protocol (first-party code)

The new [task_admission.py](../src/ucode/task_admission.py) enforces exactly eight evidence categories: immutable pre-fix snapshot, line-level AI/human authorship, file-specific reuse rights, independent functional oracle, oracle secrecy/holdout split, sandbox isolation, reproducible toolchain, and enforceable resource limits.

Each gate is PENDING, FAILED or EVIDENCE_PRESENT_NOT_ATTESTED. A claim of reviewed evidence requires a reference, SHA256 fingerprint and named reviewer; a digest or reviewer string does **not** cryptographically validate provenance or authorization. Even eight filled evidence claims yield EXTERNAL_ADJUDICATION_REQUIRED: this code has no self-service way to set eligible_for_experiment true. Experimental authorization must be handled separately after genuine independent review and runner attestations.

[Two machine-readable pending dossiers](../data/admission/2026-10-25/pilot_dossiers.jsonl) are tied to the original frozen discovery ID, base/head/merge commit and changed filename sets. [Offline verifier](../scripts/check_task_admission.py) checks them against the canonical 120-link audit and reports the sixteen open gates, with no downloads or source execution.

## First lead: PHP file persistence and cache layout

[Original PR: mvdbos/php-spider #172](https://github.com/mvdbos/php-spider/pull/172). Immutable pre-fix base **25e9b1cf855669c24ba1609c7d4cfcda17ac6217**, PR head **40cdfdb4d7b6eb8afebbd548ea87c7ed4805808a**, merge **e676149d0b7b61cee61424dfa849d03ceffb7070**. Three production PHP source paths and two PHPUnit test paths were changed.

[Pre-PR issue #168](https://github.com/mvdbos/php-spider/issues/168) was created October 22, 2026 at 22:53:10 UTC; PR created 22:55:42. The issue calls for one shared URI-to-file layout policy with compatibility for encoded names, spider-ID isolation and extension hooks. Read-only patch review found new FilePersistenceLayout.php functionality and PR-authored tests, but those tests are **not independent held-out functional oracles**.

Root MIT LICENSE has observed Git blob SHA **9d2375c29942233e3b646d51210ebc67235df873**; individual file rights not reviewed. Three PR commits use the Copilot account, two contain human co-author trailers: line-level autonomous authorship **not established**.

Pre-fix composer.json has blob SHA **8924dc7ca160eecf5aa98500b7c20a0ed3d865d5** and specifies PHP >=8.2, ext-dom, ext-pcntl, Guzzle, Symfony components and PHPUnit 11 dev dependencies. Actual pinned transitive versions, installed environment and safe sandbox are **not verified**.

**Proposed but unbuilt oracle:** independently specified file-path/URI encoding compatibility, scratch-directory persistence and cache lookup; isolate filesystem, disable all network access, and never reuse PR-added test cases as unseen oracle evidence. Post-hoc reviewers have already seen the patch and cannot claim blinded oracle derivation.

## Second lead: Go settlement points and ranks

[Original PR: PlayHuai/eighty-point-huai-an #30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30). Base **ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a**, head **e06b7e5fad881f4d34752eaf98615f84dbf57db3**, merge **e409eb6d91507dff78bc7bcfb54d4da828e02a53**. Two production Go paths and two added/changed Go test paths.

[Pre-PR issue #29](https://github.com/PlayHuai/eighty-point-huai-an/issues/29) was created October 23, 2026 12:18:50 UTC, eight seconds before the PR, but its brief request is underspecified. A **pre-fix base revision** of docs/design.md (blob SHA **b566ca7627b6518670a866a6a637bd5257e947f4**) explicitly describes scoring tiers, spring outcomes, hall multipliers and rank thresholds. This is a genuine chronological specification *lead*, not a sealed oracle.

Read-only diff inspection identified proposed scoring/rank functions and PR-authored boundary tests, alongside database settlement changes. A pure scoring microtask is potentially feasible but **not equivalent to the full PR functional correctness**; transactional idempotency and database replay must be independently verified.

Root MIT LICENSE blob SHA **c15f68715092a3b55253f80bd1fa6af08d6b0879**; file-specific rights remain PENDING. Four commits use bot author metadata, three contain human co-author trailers; fraction of lines autonomously AI-authored cannot be inferred.

## Go/no-go

Both leads remain MANUAL_REVIEW_ONLY with **8/8 open admission gates each**. Relative ease of running PHP scratch-path tests vs Go pure numeric tests is a feasibility hypothesis, not empirical success. The next real milestone is independently verified file-level rights, task/oracle authorship separation, a sealed evaluator not visible to agent policy, and rootless/network-off resource-capped execution. No routine GitHub CI should execute third-party source.

To reproduce with only first-party code: run **python -m scripts.check_task_admission**, then **python -m unittest discover -s tests -v**. Admission script must report PREEXPERIMENTAL_EVIDENCE_INVENTORY_ONLY and 0 scientifically admitted tasks.

This memo is grounded in publicly accessible GitHub issue/spec/commit/patch metadata. The Springer source in GitHub may describe these leads, but no real task-level LLM results exist yet.
