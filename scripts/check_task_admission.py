"""Validate prospective task admission dossiers against immutable PR metadata.

No execution, network calls, source cloning, paid compute or admission
promotion. Exit nonzero on forged identity or a claimed approved task.
"""
import argparse
import json
from pathlib import Path

from scripts.summarize_audit import load_manifest, load_records
from ucode.task_admission import (
    assess_dossier, dossier_sha256, parse_dossier,
    validate_dossier_against_metadata,
)

DEFAULT_DOSSIERS = "data/admission/2026-10-25/pilot_dossiers.jsonl"


def validate_prospective_dossiers(
    records: list[dict], manifest: dict[int, dict],
    path: str | Path = DEFAULT_DOSSIERS,
) -> list[dict]:
    by_id = {int(r["candidate_id"]): r for r in records}
    out = []
    seen = set()
    for num, line in enumerate(Path(path).read_text(
            encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        task = parse_dossier(payload)
        if task.candidate_id in seen:
            raise ValueError("duplicate dossier candidate")
        seen.add(task.candidate_id)
        if task.candidate_id not in by_id:
            raise ValueError("dossier candidate absent from canonical audit")
        validate_dossier_against_metadata(task, by_id[task.candidate_id],
                                          manifest)
        report = assess_dossier(task)
        if report.eligible_for_experiment:
            raise ValueError("offline dossier must never authorize execution")
        out.append({
            "candidate_id": task.candidate_id,
            "repository": task.repository,
            "status": report.stage,
            "open_gates": list(report.open_gates),
            "reported_evidence": list(report.reported_evidence),
            "failed_gates": list(report.failed_gates),
            "external_adjudication_required":
                report.requires_independent_adjudication,
            "eligible_for_experiment": report.eligible_for_experiment,
            "dossier_sha256": dossier_sha256(payload),
        })
    if not out:
        raise ValueError("no review dossiers")
    return sorted(out, key=lambda r: r["candidate_id"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dossiers", default=DEFAULT_DOSSIERS)
    p.add_argument("--audit-dir", default="data/audits/2026-10-24")
    p.add_argument("--manifest", default="data/discovery/agent_pr_candidates_120.csv")
    args = p.parse_args(argv)
    manifest = load_manifest(args.manifest)
    records = load_records(args.audit_dir, manifest)
    summary = validate_prospective_dossiers(records, manifest, args.dossiers)
    print(json.dumps({
        "status": "PREEXPERIMENTAL_EVIDENCE_INVENTORY_ONLY",
        "dossiers": summary,
        "scientifically_admitted_tasks": 0,
        "third_party_executions": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
