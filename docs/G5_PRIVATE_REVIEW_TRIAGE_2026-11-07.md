# G5 independent reviewer inbox: private evidence triage, never task approval

**Date:** 7 November 2026. **Scope:** U-CODE's **12 real GitHub PR metadata leads** in its frozen pending review queue, each with **8 independent admission evidence gates**, assessed by two separate reviewer slots (A/B) = **192 form rows**, paired as **96 candidate/gate comparisons**.

**Experimental status:** 0 independently admitted executable tasks, 0 authenticated independent oracle seals, 0 real model or third-party executable runs. This document and its code do not change those facts. The reviewer comments and source evidence that would be needed to advance these gates have **not** been collected by this ChatGPT task.

## What changed, and why it matters

Previous `src/ucode/reviewer_adjudication.py` considered two **EVIDENCE_PRESENT_NOT_ATTESTED** verdicts sufficient for the status `REVIEWERS_AGREE_NOT_ADJUDICATED`, even when the two reviewers cited *different artifact checksums or evidence references*. Such mismatched supporting artifacts are not automatically evidence of a false reviewer finding, but they are **not yet evidence-level agreement**, either.

The new logic distinguishes:

| A/B situation | Redacted per-gate classification | What it means |
|---|---|---|
| One or both reviewers pending | `PENDING_REVIEWS` | No paired finding yet |
| Different verdict categories | `REVIEWER_DISAGREEMENT_NEEDS_ADJUDICATION` | Category conflict |
| Both positive, different SHA256 evidence digests | `EVIDENCE_DIGEST_MISMATCH_NEEDS_ADJUDICATION` | Potential version/content mismatch; independent reconciliation required |
| Both positive, same digest but different refs | `EVIDENCE_REFERENCES_DIFFER_NEEDS_ADJUDICATION` | Source-path/reference mismatch; independent reconciliation required |
| Same verdict and evidence references (if positive) | `REVIEWERS_AGREE_NOT_ADJUDICATED` | Agreement **only** on supplied form claims; still **no authorization** |

The input validator additionally prevents self-approval booleans, unknown privileged fields, same identity across reviewer slots, missing/duplicate/rewritten candidate and gate identities, JSON duplicate-key injection, NaN, oversized file or line, symlinked reviewer inputs, and overwriting private inputs with a public summary.

## Real-world local-only handoff

1. Independently distribute the existing **blank, canonical, source-screened** A/B forms. In a securely controlled copy of the repository, run:

   ```bash
   python -m scripts.export_independent_review_forms --output-dir /private/ucode-review-forms
   ```

   This creates **blank templates** and fingerprints, **not** actual reviewer work. Route the two copies *separately* to qualified external human reviewers. Never feed the post-fix PRs, reviewer private notes, hidden gold or evaluation answers to an agent policy.

2. Once **real** reviewers have independently supplied completed, source-backed JSONL files, store them on your own encrypted/offline machine, outside GitHub and outside any public CI artifact. Do not commit or paste their identities, evidence URIs, evidence hashes, legal notes or oracle artifacts to U-CODE.

3. Run the triage **locally**, never in a public GitHub Actions job:

   ```bash
   python -m scripts.audit_private_review_forms \
     --reviewer-a /private/ucode-review-forms/A_completed.jsonl \
     --reviewer-b /private/ucode-review-forms/B_completed.jsonl \
     --output /private/ucode-review-forms/review_redacted_status.json
   ```

4. Inspect only the status summary and disagreement categories. A/B evidence-content or reference mismatches require a separately responsible adjudicator to inspect original **private** artifacts, not the status-only report. This script **does not read, download or authenticate the referenced evidence content**.

5. Keep provenance/signature, specification/rights, independent hidden evaluator, runtime sandbox and physical resource-meters approval in a **separate authenticated offline channel**. This source-only code path **has no task-admission API**. Even if all 96 reviewer pairs agree positively, `independently_admitted_executable_tasks` remains hard-coded to **0**.

## Privacy and trust boundaries

The redacted summary contains only the **already-public PR candidate ID**, one of the eight generic evidence gate names, a review status category and aggregate counts. It intentionally **does not output** reviewer names, free-text notes, URLs, actual evidence SHA256 digests, label values, hidden oracles or file contents. The output still reveals whether a candidate's review workflow is complete; share it only under an appropriate study data-management plan. Never use the private inputs as GitHub Actions artifacts.

The tool's input paths are local non-symlink files; the parser enforces 96 JSONL records per reviewer and strict object fields via the original canonical source packet inventory. The public output path may not overwrite an input file.

- **SHA256 equality** proves at most equality of the hashes *provided by reviewers*, not actual artifact custody.
- **Recorded distinct names** do not authenticate independent human identities or prevent collusion.
- **A completed human worksheet** is neither an independently verified executable task nor a sealed oracle.
- **Two positive verdicts** have no direct bearing on correctness, novelty, five-resource costs or publication viability.

## Verification

```bash
python -m unittest discover -s tests -p "test_private_review_inbox.py" -v
python -m unittest discover -s tests -v
python -m scripts.compile_pilot_preflight --require-ready
# The final command must still exit 2: PHP/Go approval is blocked.
```

The new tests generate completely **fictional** reviewer identities, evidence digests and notes. The tests assert that a populated 96/96 positive evidence report still has **0 admitted tasks**, malformed/private payloads are refused and no sensitive reviewer strings survive the report.

**Research benefit:** this is a reproducible, privacy-aware *reviewer handoff and disagreement audit*, removing a methodological blind spot in the transition from public PR leads to independently adjudicated tasks. It does not fabricate or substitute for independent adjudication.

See [the real-task activation protocol](G5_M4_REAL_PILOT_ACTIVATION_2026-11-06.md), [the earlier reviewer forms](../src/ucode/reviewer_adjudication.py), [issue G5](https://github.com/Rocky5502/U-CODE/issues/7), and [prospective Springer manuscript source](../paper/overleaf/main.tex).
