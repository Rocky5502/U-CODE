# U-CODE: conservative PR-overlap graph and split safety

**27 October 2026 · Offline metadata-only release, not task admission.**

This deterministic reference analyzes all 120 PR discovery records to
flag potential repository-family overlap **before** any model training
or evaluation split is created. It does **not** read source code, execute
third-party tasks, certify independent correctness or remove any PRs.

## Evidence and graph construction

Run:

```bash
python -m scripts.audit_lineage_risks --output-dir dist/ucode-lineage-review
```

Inputs are the immutable original 120-link manifest and the 120 canonical
audit records already tracked in GitHub. The [graph implementation](../src/ucode/lineage_risk_graph.py)
produces two edge classes with deliberately different consequences:

- **Candidate provenance links:** same recorded fork-parent hint or same
  Git commit SHA across any of `base_sha`, `head_sha` or
  `merge_commit_sha` (including cross-role `HEAD` of one PR equal to
  `BASE` of another). These form *potential* connected components that
  **must** be adjudicated before any split is declared safe.
- **Same GitHub owner warnings:** associated repository names have
  the same owner namespace, but do not automatically join their
  provenance components. They are reviewer signals, not evidence that
  two repositories share code or issues.

A deterministic star graph is used for each common-key group, avoiding
quadratic pair explosions. Component labels use SHA256 over sorted
record IDs; the hashes label *candidate groups* rather than certify
content uniqueness or evidence authenticity.

## Actual fixed-snapshot screening result

The frozen source-free 120-PR snapshot yielded:

| Check | Observed metadata outcome |
|---|---:|
| Discovery PR/repository-name records | 120 |
| Candidate provenance components | 120 |
| Components linked by same fork-parent hint | 0 edges |
| Components linked by shared Git SHA | 0 edges |
| Common GitHub owner warning links | 9 edges |
| Independent file-level duplicate adjudications | 0 |
| Qualified executable tasks | 0 |
| Frozen leakage-safe train/test groups | **None** |

These **negative metadata matches are not a clean bill of health**.
A single repository owner may operate wholly independent projects;
conversely, unrelated owners may fork, vendor or copy the same source
and share public benchmark tasks. Source files, Git object ancestry,
PR comments, issue labels, and patch-similarity fingerprints have NOT
been compared. Zero *metadata-linked* pairs therefore does not imply
zero cross-task contamination or justify any split.

## Output and reproducibility

The pipeline creates its own CI artifact,
`ucode-lineage-review-only-v1`, isolated from the eight-file
`ucode-pr-metadata-clean-v1` dataset bundle:

- `possible_lineage_components_NOT_SPLIT.csv`: all 120 immutable
  candidate IDs with conservative group labels, owner-only warnings
  and blocked task/split states.
- `potential_cross_task_links_REVIEW_ONLY.csv`: typed metadata edges,
  commit roles and explicit adjudication requirements.
- `lineage_graph_report.json`: aggregate counts and scientific caveats.
- `lineage_graph_integrity.json`: SHA256 hashes of graph outputs
  and the raw discovery manifest.

The graph is validated with adversarial tests for record-order
invariance, forged commit identities, cross-role Git SHA overlap,
fork-parent links, owner-only nonjoining, and false split promotion.

## Next reviewer gates

1. Independently inspect repository fork and Git ancestry, preserving
   exact commit timestamps and source-derived *pre-fix* snapshots.
2. Identify common upstream repositories, copied patches, duplicated
   issue text and test cases **without feeding post-fix labels to
   an agent**.
3. Cluster by independently adjudicated repository family and
   task content; document contested/dropped examples.
4. Freeze split assignments after pre-registration and verify no
   train/test or model/scorer/evaluator overlap.
5. Obtain task-level source rights, sealed oracle, reproducible
   sandbox and five-resource attestation before claiming an
   executable benchmark.

All findings are **metadata screening** evidence for the Springer ASE
Methods, not actual contamination rates or a Nature Scientific Data
technical validation of executable tasks.
