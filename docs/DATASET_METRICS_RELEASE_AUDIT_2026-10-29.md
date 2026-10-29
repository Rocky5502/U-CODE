# U-CODE | Data, evaluation metrics and reproducibility audit

**Date:** 29 October 2026  
**Scientific stage:** source-free PR discovery data; software references,
**not** a qualified repository repair benchmark or demonstrated RQ effect.

## Executive evidence snapshot

| Unit, cohort or readiness dimension | Verified / documented value | Interpretation |
|---|---:|---|
| PR-link/repository-name discovery records | **120** | Every discovered link remains in the denominator |
| Successfully retrieved PR metadata | **119** | One retrieval failure; not missing at random by assumption |
| Query-language strata | **12**, ten per stratum | GitHub search filters, **not** proof of changed-code language |
| Production-source path leads | **62** | Extension/path screening only, not executable test tasks |
| First-pass manual review leads | **14** | Metadata ranking; not source rights clearance |
| Manual-review queue | **12** | Still pending independent assessment |
| Independently approved executable tasks | **0** | No task has passed admission |
| Independent functional correctness oracles | **0** | No real release may be scored yet |
| Models selected for planning | **6 names** | No verified frozen weight revisions or inference |
| Experimental policy slots | **8** | Not eight faithful, tested real algorithms |
| Actual mixed-policy effectiveness estimate | **N/A** | Not zero; no eligible empirical denominator |
| Authenticated OCI execution | **0 runs** | Only an unexecuted launch configuration and first-party smoke |

The 120-record snapshot is grounded in
[`frozen_cleaning_summary.json`](../data/curated/2026-10-27/frozen_cleaning_summary.json),
the canonical discovery/audit provenance, and the
[confirmatory protocol](../configs/confirmatory_sbse_protocol_2026-10-25.json).
Our **task grain is not the same as our data grain**: a discovered PR
may not have a pre-fix specification, legally reusable source, a
reproducible environment, or a sealed independent oracle.

## 1. Provenance and dataset semantic checks

The normal release path is:

```text
120 manifest entries and per-link audit records
  -> deterministic metadata clean (preserves failed links)
  -> 12-stratum report and 12-candidate review queue
  -> schema and reviewer-rights warning report
  -> seven SHA256 digests + snapshot-source digest references
  -> independently run release verifier
  -> cross-file semantic consistency audit
```

`src/ucode/release_semantics.py` rejects self-consistent digests if the
**content** disagrees: duplicate candidate keys, missing records,
altered retrieval statuses, reclassified production paths, invented
source-language strata, inflated shortlist, different shortlist
identities, changed reporting totals, tampered schema or unauthorized
task/oracle/rights flags. Its adversarial tests re-hash modified CSV/JSON
files on purpose; simply verifying that hashes match would not catch
those alterations.

The digest receipt and semantic consistency still do **not** constitute
cryptographically authenticated upstream GitHub evidence: an attacker
who rewrites the entire snapshot, including source artifacts, can
invent a coherent alternate history. Independently pin the source
commit/manifest and review file-specific rights before release.

## 2. Frozen metric dictionary

Do **not** combine denominators across discovery metadata, task-level
experiments and release-only subsets.

| Metric | Definition | Denominator and reporting rule |
|---|---|---|
| Full-task success (primary ITT) | `sum(released AND independent_oracle_passed) / N_assigned` | All assigned task/model/seed/budget cells. Abstain, timeout and safety-stop are non-success; uncertain infrastructure failures need bounds |
| Release coverage | `N_release / N_assigned` | Same assigned denominator, not only successfully executed tasks |
| Conditional wrong-release risk | `N_released_and_oracle_failed / N_released_and_verified` | Undefined/null if no released patches, **not 0%** |
| Paired ITT effect | `mean(success_UCODE(i)-success_control(i))` | Exactly matching task/model/seed/budget; treatment and control share caps/tool opportunities |
| Realized cost vector | `(tokens, test_calls, gpu_s, cpu_s, wall_s)` | Preserve all five components per assigned run; use independently enforced meters, never a forecast |
| Infra-failure sensitivity | Worst/best feasible paired effect when infrastructure failure labels are missing | Bounds on assigned-cell effect, **not** a 95% confidence interval |

The executable definitions, with units and zero-denominator rules, are
in [`research_readiness.py`](../src/ucode/research_readiness.py).
For prospective empirical accounting see
[`evaluation.py`](../src/ucode/evaluation.py),
[`experiment_contract.py`](../src/ucode/experiment_contract.py)
and [`attrition_bounds.py`](../src/ucode/attrition_bounds.py).

**At the current evidence stage every empirical metric is N/A.**
A null metric is an important scientific outcome of the readiness
audit: it prevents a preregistration, a demo, or metadata rows from
being promoted to measured program correctness.

## 3. Reproduce on Python 3.10 or 3.12

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m scripts.audit_dataset_quality \
  --output-dir dist/ucode-pr-metadata-clean
python -m scripts.verify_dataset_release \
  dist/ucode-pr-metadata-clean
python -m scripts.export_research_readiness \
  --output-dir dist/ucode-research-readiness
python -m scripts.audit_overleaf_sources
```

Outputs:
- **Eight-file metadata release:** curated CSV and JSON with SHA256 receipt.
- **`research_readiness.json`:** machine-readable observational limits,
  model/policy planning counts and six explicit N/A metric values.
- **`RESEARCH_METRICS_AND_STATUS.md`:** reviewer-facing dataset and
  metric definitions generated from the same auditable inputs.
- **Overleaf sources:** Springer draft and references, **not** a checked
  compiled PDF or an automatically synchronized Overleaf project.

The CI matrix independently runs the same checks on both supported
Python versions and publishes the status as a separate artifact. The
snapshot is deliberately conservative; it does not call hosted LLM
APIs, download model weights, execute discovered repository code,
use a model/benchmark evaluator or spend paid GPU time.

## 4. Reviewer-facing admission and study gates

1. Independently sign off the source-era task specification, original
   pre-fix source, file-specific reuse rights and author attribution.
2. Seal an independently authored functional oracle outside policy
   inputs. Disentangle PR-authored tests from evaluator-only tests.
3. Verify a genuinely isolated, independently inspected, no-network
   sandbox and true five-resource enforcement on a dedicated runtime.
4. Freeze actual model/tokenizer revisions, seeds, tool permissions,
   artifact image and same candidate-generation opportunities.
5. Validate predicted probabilities on disjoint training repo families;
   **do not fit uncertainty on held-out correctness labels**.
6. Fidelity-audit all eight policy implementations; report the exact
   intended treatment and budget-matched control.
7. Preserve all randomized assignments, including failures,
   abstentions, timeouts, system errors and their missingness.
8. Only after those gates compute paired success, grouped uncertainty,
   release coverage/risk, cost and careful failure analyses for RQ1--RQ6.

This is a reproducible methodological and software contribution at
present, **not evidence that U-CODE beats prior coding-agent systems**.
