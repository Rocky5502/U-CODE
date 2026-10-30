"""Audit prospective evaluator separation without external code execution."""
import argparse
import json
from pathlib import Path

from scripts.check_task_admission import DEFAULT_DOSSIERS
from scripts.summarize_audit import load_manifest, load_records
from ucode.evaluator_boundary import (
    evaluate_registration, policy_visible_registration, registration_from_json,
)
from ucode.task_admission import parse_dossier, validate_dossier_against_metadata
from ucode.pre_fix_spec_binding import (
    verify_go43_document_tree_binding, verify_php104_mutable_issue_quarantine,
)

DEFAULT_REGISTRATIONS = (
    "data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl"
)
DEFAULT_GO43_DOCUMENT_SNAPSHOT = (
    "data/admission/2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json"
)
DEFAULT_PRE_FIX_TREES = (
    "data/admission/2026-10-27/two_candidate_pre_fix_tree_inventory.json"
)


def check_registrations(
    registrations_path: str | Path = DEFAULT_REGISTRATIONS,
    dossiers_path: str | Path = DEFAULT_DOSSIERS,
    audit_path: str | Path = "data/audits/2026-10-24",
    manifest_path: str | Path = "data/discovery/agent_pr_candidates_120.csv",
    spec_snapshot_path: str | Path = DEFAULT_GO43_DOCUMENT_SNAPSHOT,
    source_trees_path: str | Path = DEFAULT_PRE_FIX_TREES,
) -> list[dict]:
    manifest = load_manifest(manifest_path)
    canonical = {int(x["candidate_id"]): x for x in load_records(audit_path, manifest)}
    dossiers = [parse_dossier(json.loads(line)) for line in Path(
        dossiers_path).read_text(encoding="utf-8").splitlines() if line]
    by_id = {d.candidate_id: d for d in dossiers}
    if len(by_id) != len(dossiers):
        raise ValueError("duplicate original admission dossier")
    seen = set()
    registered = {}
    checked = []
    for line in Path(registrations_path).read_text(
            encoding="utf-8").splitlines():
        if not line:
            continue
        reg = registration_from_json(json.loads(line))
        if reg.candidate_id in seen or reg.candidate_id not in by_id:
            raise ValueError("evaluator registration duplicate or not in admitted dossier inventory")
        seen.add(reg.candidate_id)
        registered[reg.candidate_id] = reg
        dos = by_id[reg.candidate_id]
        validate_dossier_against_metadata(dos, canonical[reg.candidate_id], manifest)
        if (reg.repository != dos.repository or
                reg.task_base_sha != dos.base_sha or
                set(reg.pr_authored_test_paths) != set(dos.changed_test_paths)):
            raise ValueError("evaluator declaration disagrees with original PR dossier")
        if reg.issue_ref.startswith("https://github.com/") is False:
            raise ValueError("invalid issue reference")
        report = evaluate_registration(reg)
        if report["independently_admitted"]:
            raise ValueError("metadata registration may never authorize scientific execution")
        visible = json.dumps(policy_visible_registration(reg), sort_keys=True)
        if any(secret in visible for secret in reg.evaluator_only_oracle_refs):
            raise ValueError("evaluator-only reference exposed to policy")
        checked.append(report)
    if seen != set(by_id):
        raise ValueError("each prospective dossier needs a matching oracle-boundary registration")
    # A 40-hex blob string ALONE is not enough to bind a visible document
    # to the pre-fix Git source tree. Check the exact Go base tree entry and
    # quarantine the historical mutable PHP issue independently of claims.
    if set(registered) != {43, 104}:
        raise ValueError("unexpected historical PHP/Go evaluator roster")
    snapshot = json.loads(Path(spec_snapshot_path).read_text(encoding="utf-8"))
    original_trees = json.loads(Path(source_trees_path).read_text(encoding="utf-8"))
    go_result = verify_go43_document_tree_binding(
        snapshot, registered[43], original_trees,
    )
    php_result = verify_php104_mutable_issue_quarantine(registered[104])
    by_checked = {x["candidate_id"]: x for x in checked}
    by_checked[43]["source_spec_binding"] = go_result["status"]
    by_checked[104]["source_spec_binding"] = php_result["status"]
    if any(x["independently_admitted"] for x in checked):
        raise ValueError("document metadata must not authorize trial admission")
    return sorted(checked, key=lambda z: z["candidate_id"])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registrations", default=DEFAULT_REGISTRATIONS)
    p.add_argument("--dossiers", default=DEFAULT_DOSSIERS)
    p.add_argument("--go-spec-snapshot", default=DEFAULT_GO43_DOCUMENT_SNAPSHOT)
    p.add_argument("--source-trees", default=DEFAULT_PRE_FIX_TREES)
    args = p.parse_args(argv)
    report = check_registrations(
        args.registrations, args.dossiers,
        spec_snapshot_path=args.go_spec_snapshot,
        source_trees_path=args.source_trees,
    )
    print(json.dumps({
        "status": "POLICY_EVALUATOR_BOUNDARY_NOT_ATTESTED",
        "candidate_count": len(report),
        "records": report,
        "approved_external_executions": 0,
        "independent_oracle_results": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
