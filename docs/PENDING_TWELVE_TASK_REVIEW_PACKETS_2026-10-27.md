# U-CODE: pending evidence packets for first twelve PR review leads

**Snapshot:** 27 October 2026. **No automatic task eligibility.**

This is a deterministic, source-free starting packet for human research
review. It is **not** a twelve-task executable benchmark.

The frozen clean 120-PR discovery set contains 62 production-path leads,
14 first-pass metadata-priority leads, and a diversity-aware twelve-item
manual queue. The new script

```bash
python -m scripts.export_pending_review_packets \
  --output-dir dist/ucode-admission-review-only
python -m scripts.check_task_admission \
  --dossiers dist/ucode-admission-review-only/review_packet_12_PENDING.jsonl
```

generates one metadata dossier for each of the **twelve** queue entries.
The existing [canonical admission validator](../src/ucode/task_admission.py)
independently checks its URL, immutable original base/head/merge SHAs,
changed source paths and test paths against the 120-row original audit.

Each dossier has **eight mandatory, explicitly PENDING gates**:

1. Reproducible immutable pre-fix snapshot
2. Independently supported changed-line AI authorship
3. Modified-file reuse permissions and attribution
4. Independent behavioral correctness oracle
5. Oracle secrecy and repository/task leakage-safe splits
6. Reviewed, safe, rootless, network-off execution sandbox
7. Reproducible pinned task build/runtime
8. Independently measured and enforced resource limits

That is **96 pending checks, zero approved checks, zero admitted
executables**, and zero third-party code executions. No reviewer
identity is fabricated; a template cannot self-approve. Source-path
metadata and existing PR-added tests are supplied for human audit only;
they are never an independent evaluator's hidden tests.

Three output files are created in a **separate** CI artifact
`ucode-admission-review-only-v1`:

- `review_packet_12_PENDING.jsonl`: twelve typed metadata forms.
- `review_packet_summary.json`: ordered queue and 96-gate status.
- `review_packet_integrity.json`: SHA256 source manifest and output digests.

The packet ZIP is strictly **reviewer-only** and must not be passed
to coding agents as a task prompt; it contains post-fix head/merge
SHAs and changed test-file paths that could leak information.
The agent-facing pre-fix task projection must be independently
constructed later from rights-cleared task-era information and must
exclude all post-fix/evaluator-only records.

The previous two detailed case studies (candidate IDs 43 and 104)
remain in `data/admission/2026-10-25/pilot_dossiers.jsonl`.
They contain additional read-only historical notes, but none passed
their eight independent gates. The newly generated packets are
intentionally more conservative and do not overwrite those dossiers.

**Actual next manual work:** for every queued candidate, independently
review source-era issue/specification, file permissions, changed-line
authorship, oracle independence, safe execution and leaks. Preserve
failed and excluded tasks in the attrition record rather than
retroactively defining them out of the denominator.

A one-week feasibility pilot is possible **only after** enough
tasks have passed all external approvals and the six A100-compatible
model runtimes have been verified. A newly created review packet
is not evidence of a tested task.
