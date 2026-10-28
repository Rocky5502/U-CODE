# U-CODE eight-policy evaluator-blind runner integration — 28 October 2026

**Status: FIRST-PARTY, SYNTHETIC-ONLY ORCHESTRATION.**
Not a real six-model trial, not eight faithfully implemented comparator algorithms, and not a source-code sandbox or certified resource meter.

## Implemented in this sprint

- `src/ucode/shadow_eight_arm_runner.py` connects a complete frozen `FrozenStudy` + M4 `AssignedOpportunity` matrix to the evaluator-blind `run_blind_policy` reference.
- The matrix must contain **exactly the eight registered policy names and six selected model names**. It must include every assigned policy/task/model/seed/budget combination.
- Before constructing even the first policy/tool adapter, the M4 checker validates common source base, visible task-spec digest, seed, tool access, environment, candidate archive, action opportunity catalogue, model checkpoint identity, and all five resource caps.
- `task_views` contain exactly the four pre-fix policy fields (`repository`, `base_sha`, `prefixed_spec`, `spec_sha256`). Input must be `AgentTaskView` and agree with assigned SHA fields. A Git digest is **not** proof that the historical text is authentic or spoiler-free.
- Every arm gets a fresh policy callback and public tool callback. The policy receives no sealed evaluator callback. The runner uses the existing typed `BlindSession` with pre-dispatch cost reservations; failures and overrun receipts are never converted into successes.
- Outputs contain terminal statuses, patch SHA256 fingerprints, schema-level accounting status, remaining five-resource vectors and deterministic **public-metadata-only** trace digests. No raw patches, free-text feedback, private tests or correctness labels appear in these summaries.

The current code accepts callback factories from its caller. **This is not runtime isolation.** A callback can in principle perform arbitrary side effects, and a free-text tool response may contain leaked information. Therefore the module must remain wired only to local synthetic references until a trusted rootless sandbox, public-feedback filter, independent meter, source-rights approval and sealed oracle have been separately attested. Hashes themselves are asserted fields, not trusted cryptographic identities of model-produced actions or authenticated resource readings.

## Exact offline reproduction

```bash
python -m scripts.smoke_shadow_eight_arm_runner
python -m unittest discover -s tests -v
```

The synthetic smoke has **48 shadow arm integrations** (one synthetic task, six *names* of selected models, eight *names* of registered policies, one illustrative seed and one budget). All policy factories are explicitly identical scripted placeholders (generate / visible-test / release). The scripted public tool returns fixed local text, no repository execution or hidden verdict. **No fair performance comparison is possible** from these smoke traces, and 48 is neither a sample size nor a reported task denominator for RQ3.

## Remaining P0 gates for an empirical runner

1. **External source-task admission:** verifiable task-era specification, independent source/file licensing decision, correct repository/fork lineage, pre-fix origin and signed genuine reviewer adjudication (PHP #104 still unqualified).
2. **Independent oracle:** hidden functional tests authored without PR-solution/PR-test reuse, sealed in a separate trusted store inaccessible to policy/tools; clear full-task versus prospective microtask specification, and confidentiality review of diagnostics.
3. **Sandbox:** isolated, non-networked, credential-free disposable PHP/Go execution with reviewed filesystem mounts, runtime/dependencies and CPU/time limits.
4. **Trusted metering:** enforce and independently record tokens, tool calls, CPU/GPU and wall seconds before runtime overruns can happen. A post-hoc callback `ResourceVector` is NOT a quota attestation.
5. **Real agent backends:** verifiably pinned six model weights/tokenizers/engines, access terms and runtime security, with calibrated diagnostic/generation models fitted only on independent training groups.
6. **Policy fidelity:** independent implementation/reproduction review for each of the eight registered algorithms. The current eight callback slots are *not those algorithms*, and simply giving them eight different labels would be pseudoreplication.
7. **Fair paired evaluation:** independently logged shared task and candidate opportunities, identical caps, frozen seeds, full assigned denominators, no model/oracle leakage; independent evaluator joins correctness only after policy termination. Existing `experiment_contract.py` supports post-hoc structural checks, not authenticated evidence.

**Do not merge synthetic diagnostics into Results tables** or claim this module produces end-to-end real coding success.
