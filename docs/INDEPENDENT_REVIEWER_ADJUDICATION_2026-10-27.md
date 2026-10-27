# U-CODE: two-independent-reviewer evidence preparation (27 October 2026)

**Stage: reviewer assignment forms only; no human evaluations performed.**

This artifact extends the preexisting 12-candidate/96-gate reviewer packet.
The [canonical candidate screen](../data/curated/2026-10-27/frozen_cleaning_summary.json)
contains 120 GitHub-PR metadata records and 62 production-source-path
leads, but **no independently admitted runnable task**. The
[12 pending evidence packets](../src/ucode/pending_review_packets.py) are
reviewer-only, not agent-visible inputs. All six LLMs remain unexecuted.

## Completed engineering

[Independent-review validator](../src/ucode/reviewer_adjudication.py) and
[reproducible offline exporter](../scripts/export_independent_review_forms.py):

```bash
python -m scripts.export_independent_review_forms \
    --output-dir dist/ucode-independent-reviewers-only
```

The exporter creates two **separate blank forms**, one for reviewer A
and one for reviewer B. Each contains 12 candidates × 8 substantive
independent task admission gates, i.e. **96 gate assessments per
reviewer; 192 blank gate forms total**. Form records include canonical
immutable PR identifiers, packet SHA256, reviewer slot, a pending
verdict, empty evidence refs/digest, empty reviewer identity and note.
All records have `independent_approval=false`.
A third file reports **zero completed pairs** and hence an
*undefined* agreement rate (not an invented 100% agreement).
A fourth file records the SHA256 of each exported form/report.

**Eight independent gates:** pinned pre-fix snapshot; code-line
authorship; modified-file permissions; independent functional oracle;
oracle secrecy/split; sandbox isolation; reproducible runtime; and
independently enforced resource caps.

### After independent humans submit their work

The validator accepts `PENDING`, `INSUFFICIENT_INFORMATION`,
`REJECTED_WITH_REASON`, or
`EVIDENCE_PRESENT_NOT_ATTESTED`. It enforces:

- Complete 12 × 8 records and immutable PR/packet digests, one
  record per (candidate, gate, reviewer slot).
- Different real reviewer identities for populated A and B forms;
  evidence references and 64-character digest for any positive
  *evidence-present but unattested* observation.
- An explicit rationale for each non-pending judgment.
- Reviewer disagreement summaries and agreement fraction **only
  among gates that both reviewers actually assessed**.
- **Never automatic admission**, even when both reviewers agree.
  A separately authenticated adjudicator must assess evidence and
  approve task build, rights, independent hidden oracle and runner.
  This validator is a structural workflow aid, NOT proof reviewer
  identity, data independence, source authenticity or approved rights.

Both forms are shipped in **one CI artifact only for logistical
convenience**. To preserve independent human evaluation, distribute
the A form to reviewer A and B form to reviewer B *separately*,
do not share completed notes until both finish, and retain raw
timestamps and signed reviewer attestations outside this system.
The scripts do not establish human blinding or signed authorship.

### Boundary to the ASE model experiment

The worksheets contain post-fix PR URLs and metadata, so **never
pass them to a patch-generating coding agent**. Admission requires
an independently reconstructed pre-fix task visible without gold
patch, post-fix commit, test patches, oracle labels or reviewer notes.
The frozen six-model comparative protocol is still blocked at
task rights, execution environment and genuine independent oracle.

This improves methods reproducibility and technical-quality process
for a future data resource, but a blank reviewer form is **not**
an independently validated annotation dataset and cannot support
a `Scientific Data` Data Descriptor claim of completed validation.
