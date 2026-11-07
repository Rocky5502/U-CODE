# G5 M8: detached Ed25519 evidence integrity for independent pilot admission

**Status: source-only, tested against invented signatures, NO human review and NO task admission.**

**Date:** 7 November 2026. **Scope:** existing PHP #104 / Go #43 source-era pilot candidate dossiers. This extends, rather than replaces, the prospective [pilot preflight](G5_M4_REAL_PILOT_ACTIVATION_2026-11-06.md) and the [private two-reviewer worksheet triage](G5_PRIVATE_REVIEW_TRIAGE_2026-11-07.md). This implementation is not the separate, independently governed task-admission authority.

## What new code actually does

- `src/ucode/external_admission_receipt.py`: represents a **single immutable task binding** with exact GitHub source identity (repo, PR, pre-fix base SHA40, declared full PR vs microtask scope, original dossier SHA256) and separate 64-hex **commitments** to source-era specification, independently authored oracle, file-specific rights, frozen repository-lineage split, toolchain and five-resource meter, plus `sha256:<64hex>` OCI image digest. The typed binding yields a deterministic SHA256 of the canonical sorted JSON message.
- Each of eight admission categories requires **two detached Ed25519 signatures** (reviewer slots A/B) over a domain-separated, versioned canonical JSON message containing the binding SHA256, candidate ID, gate, slot, evidence digest, key ID and UTC validity window. Cryptography is standard Ed25519 specified by [RFC 8032](https://www.rfc-editor.org/info/rfc8032/); it is **not** a novel research algorithm.
- The offline verifier requires 16/16 signatures, verifies signature bytes under the separately supplied **trusted public-key registry**, enforces different public keys for slots/roles, restricts key authorization to category-specific roles, refuses changed task bindings or frozen metadata mismatches, duplicate slots, invalid times, reused public keys and unsupported schemas. A cryptographically valid key proves only that the corresponding private key signed those message bytes, **not** that the purported human reviewer is independent or legally authorized.
- `scripts/check_external_review_receipts.py`: accepts three private local JSON files—binding, claim signatures and separately approved trust policy—plus explicit UTC verification time. Enforces bounded/syntax-checked JSON, no duplicate object fields, no unknown approval fields, no symlink inputs and no overwriting inputs with a public summary. It prints only the **redacted summary** (candidate ID, aggregate count and binding hash; never signatures, names, evidence references/digests, private key or oracle contents). The optional `--require-authorized` flag exits **2 even after all 16 signatures verify**.

### Review roles and separation

| Gates | Required key-policy review role | Reviewer slots |
|---|---|---|
| `immutable_prefixed_snapshot` | `source_provenance` | A+B |
| `line_level_authorship` | `source_authorship` | A+B |
| `file_specific_reuse_rights` | `rights` | A+B |
| `independent_functional_oracle`, `oracle_secrecy_and_split` | `oracle` | A+B |
| `sandbox_isolation`, `reproducible_toolchain` | `runner_security` | A+B |
| `resource_limits` | `resource_meters` | A+B |

A key is tied to exactly one declared slot and role in the externally approved trust policy, with no public-key aliases across IDs. Two different public keys do **not** prove they belong to different humans; externally responsible institutional reviewers must establish real identity, authority and independence. The source-only code cannot verify that a claim's evidence SHA matches an actual file without holding/reading that file. This is intentional to keep private reviewer oracles and rights details outside agent-visible code.

## Local-only verification

Install the extra dependency in a **trusted offline environment**:

```bash
python -m pip install -e '.[admission]'
python -m unittest discover -s tests -p 'test_external_admission_receipt.py' -v
```

When **real external review is later completed**, a separate authorized custodian can run:

```bash
python -m scripts.check_external_review_receipts \
  --binding /private/ucode/candidate_binding.json \
  --receipts /private/ucode/detached_gate_signatures.json \
  --trusted-public-keys /private/ucode/independently_approved_signer_policy.json \
  --verification-time-utc 2026-11-07T12:00:00Z \
  --output /private/ucode/redacted_signature_status.json \
  --require-authorized
# EXIT 2 IS CORRECT. Crypto verification alone never admits tasks.
```

The local paths above are *illustrative*, not files that have been created or signers who exist. The signer policy MUST be independently maintained, pinned and approved; **do not trust a key list delivered in the same email as the claimed signatures**. Review signatures locally only. Do not upload private A/B evidence, trust policy, hidden oracle data or signed receipts to GitHub or public CI, and do not use ChatGPT to read hidden oracle answers.

The module's deliberately conservative return values include:

```
stage: OFFLINE_EXTERNAL_SIGNATURE_CHECK_ONLY_NOT_ADMITTED
signed_claims_verified: 16  # ONLY for synthetically generated unit tests so far
scientific_task_admitted: false
external_code_execution_authorized: false
external_human_identity_independently_attested: false
sealed_oracle_independently_attested: false
physical_sandbox_independently_attested: false
```

These are **schema illustration and fictional test outcomes**, not real evidence. No third-party PHP or Go code has been run, no independently sealed evaluator exists, and 16/16 PHP/Go admission gates remain pending. The official implementation does not contain a transition from `PENDING` to `APPROVED`; nor does it expose a runner-side execute command.

## Scientific purpose and manuscript integration

The Springer `paper/overleaf/main.tex` methods now describe the immutable digest binding, detached Ed25519 evidence claims, category/slot role enforcement and explicit non-admission boundary. `references.bib` includes the verified authors/date/DOI of RFC 8032. These are **reproducibility and study integrity scaffolds**, not empirical outcomes or an independent contribution beyond published signature standards.

The registered six model identities, eight confirmatory policy arms, primary `ucode_conditional_bes` versus `no_uncertainty_search` contrast and sample-size planning remain unchanged. Only a real independent spec/rights/oracle/sandbox approval can unlock an actually executable benchmark. Updating source-only GitHub LaTeX files does **not** sync or compile the separate live Overleaf project. CI republishes the updated `ucode-overleaf-sources` ZIP.

## What still remains

1. For PHP #104, independent archive of the **actual pre-PR** issue/specification and file-specific reuse/attribution.
2. For Go #43, independently confirm the exact *microtask* semantic scope and its historical design/odd-remainder interpretations.
3. Collect genuine external reviewer A/B evidence; independently enroll and authenticate public verification keys, never fake signatures.
4. Independently author and seal hidden functional tests outside the policy-visible environment.
5. Have a separate external security reviewer attest the real network-disabled rootless runner and measured five-resource limits.
6. Independently pin all six model/checkpoint/tokenizer/engine combinations and confirm licenses before real experiments.
7. Separate runner-side execution authorization, trace recording, paired policy trials, and postterminal evaluator verdict joins.

Tests and public CI validate code behavior and source integrity only, not the truth of reviewer evidence or runtime isolation.
