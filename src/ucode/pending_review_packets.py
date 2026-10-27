"""Generate auditable pending-only admission forms for 12 U-CODE PR leads.

This output is REVIEWER-ONLY metadata. It is never an executable task,
never an actual human signature, and never an agent-visible input.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR
from scripts.summarize_audit import load_manifest, load_records
from ucode.audit import is_source_path, is_test_path
from ucode.dataset_curation import build_dataset
from ucode.task_admission import (
    REQUIRED_GATES, assess_dossier, parse_dossier,
    validate_dossier_against_metadata, dossier_sha256,
)


def create_pending_review_packets(*, manifest_path=SOURCE,
                                  audit_dir=AUDIT_DIR, limit=12):
    if type(limit) is not int or limit != 12:
        raise ValueError("frozen 12-record review queue required")
    manifest_path = Path(manifest_path)
    manifest = load_manifest(manifest_path)
    records = load_records(audit_dir, manifest)
    clean = build_dataset(
        manifest, records,
        sha256(manifest_path.read_bytes()).hexdigest(), max_review=limit)
    if len(clean.review_queue) != 12:
        raise ValueError("review queue size drifted; new registration required")
    by_id = {r["candidate_id"]: r for r in records}
    packets = []
    summaries = []
    for index, short in enumerate(clean.review_queue):
        cid = short["candidate_id"]
        rec = by_id[cid]
        if rec.get("triage_status") != "production_source_path_detected":
            raise ValueError("non-production metadata cannot enter reviewer packet")
        prod = rec.get("production_files") or []
        tests = rec.get("test_files")
        if tests is None:
            tests = [p for p in (rec.get("changed_paths") or [])
                     if is_source_path(p) and is_test_path(p)]
        payload = {
            "candidate_id": cid,
            "repository": rec["repository"],
            "pr_url": rec["pr_url"],
            "base_sha": rec["base_sha"],
            "head_sha": rec["head_sha"],
            "merge_commit_sha": rec["merge_commit_sha"],
            "changed_production_paths": sorted(set(prod)),
            "changed_test_paths": sorted(set(tests)),
            "repository_spdx": rec.get("repository_license_spdx"),
            "evidence_stage": "MANUAL_REVIEW_ONLY",
            "narrative": (
                "Candidate for independent manual review only; no source "
                "rights, AI line authorship, pre-fix build, sandbox or "
                "sealed external oracle has been verified."
            ),
            "gates": [{
                "gate": name, "status": "PENDING", "evidence_refs": [],
                "note": "Independent evidence and reviewer adjudication required."
            } for name in REQUIRED_GATES],
        }
        typed = parse_dossier(payload)
        validate_dossier_against_metadata(typed, rec, manifest)
        result = assess_dossier(typed)
        if result.stage != "NEEDS_EVIDENCE" or result.eligible_for_experiment:
            raise ValueError("review-only templates cannot authorize task")
        if set(result.open_gates) != set(REQUIRED_GATES):
            raise ValueError("all eight admission gates must stay open")
        packets.append(payload)
        summaries.append({
            "review_order": index+1, "candidate_id": cid,
            "repository": rec["repository"], "search_language": short["search_language"],
            "pending_gate_count": len(result.open_gates),
            "packet_sha256": dossier_sha256(payload),
            "eligible_for_experiment": False,
            "independent_reviewer_signatures": 0,
        })
    return tuple(packets), {
        "schema_version": "1.0",
        "status": "TWELVE_REVIEWER_ONLY_PENDING_DOSSIERS_NOT_TASKS",
        "reviewer_packets": len(packets),
        "pending_eight_gate_checks": 12*len(REQUIRED_GATES),
        "independent_review_approvals": 0,
        "scientifically_admitted_executable_tasks": 0,
        "third_party_code_executed": False,
        "model_inference_executed": False,
        "packet_index": summaries,
    }


def export_pending_review_packets(directory, *, manifest_path=SOURCE,
                                  audit_dir=AUDIT_DIR):
    packets, summary = create_pending_review_packets(
        manifest_path=manifest_path, audit_dir=audit_dir)
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    entries = {
        "review_packet_12_PENDING.jsonl": "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"))+"\n"
            for row in packets),
        "review_packet_summary.json": json.dumps(
            summary, sort_keys=True, indent=2)+"\n",
    }
    for name, body in entries.items():
        (dest/name).write_text(body, encoding="utf-8")
    digests = {
        "stage": "REVIEW_ONLY_METADATA_NOT_APPROVED",
        "source_manifest_sha256": sha256(Path(manifest_path).read_bytes()).hexdigest(),
        "files_sha256": {
            name: sha256(body.encode("utf-8")).hexdigest()
            for name, body in sorted(entries.items())
        },
        "no_executable_tasks": True,
        "no_oracle": True,
    }
    (dest/"review_packet_integrity.json").write_text(
        json.dumps(digests, sort_keys=True, indent=2)+"\n",
        encoding="utf-8")
    return summary
