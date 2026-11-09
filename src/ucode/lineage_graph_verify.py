"""Verify extracted four-file U-CODE provenance WARNING bundle.

Checks immutable file hashes and structure, NOT independent repository
ancestry or absence of task contamination. No third-party code execution.
"""
import csv
from hashlib import sha256
import json
from pathlib import Path
from .lineage_risk_graph import RELATIONS, COMPONENT_FIELDS, EDGE_FIELDS

EXPECTED = frozenset({
    "possible_lineage_components_NOT_SPLIT.csv",
    "potential_cross_task_links_REVIEW_ONLY.csv",
    "lineage_graph_report.json",
    "lineage_graph_integrity.json",
})


def verify_lineage_review(folder):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("missing metadata overlap-review folder")
    paths = {p.name: p for p in root.iterdir()}
    if (set(paths) != EXPECTED
        or any(not p.is_file() or p.is_symlink() for p in paths.values())):
        raise ValueError("unexpected, missing or linked overlap-review file")
    provenance = json.loads(
        paths["lineage_graph_integrity.json"].read_text("utf-8"))
    required = EXPECTED - {"lineage_graph_integrity.json"}
    if (provenance.get("stage") != "REVIEW_ONLY_NO_CONFIRMED_DUPLICATES_OR_SPLIT"
        or provenance.get("experiment_eligible") != 0
        or provenance.get("records") != 120
        or set(provenance.get("output_sha256", {})) != required):
        raise ValueError("unexpected graph metadata contract")
    for name in required:
        digest = sha256(paths[name].read_bytes()).hexdigest()
        if provenance["output_sha256"][name] != digest:
            raise ValueError("SHA256 mismatch for metadata overlap-review file")
    with paths["possible_lineage_components_NOT_SPLIT.csv"].open(
            newline="", encoding="utf-8") as f:
        components = list(csv.DictReader(f))
    with paths["potential_cross_task_links_REVIEW_ONLY.csv"].open(
            newline="", encoding="utf-8") as f:
        links = list(csv.DictReader(f))
    stats = json.loads(paths["lineage_graph_report.json"].read_text("utf-8"))
    # A SHA256 digest in the SAME editable folder proves byte integrity
    # against this manifest, NOT that graph claims are internally coherent
    # or independently authenticated. Check semantic provenance invariants
    # even if an adversary rewrites BOTH the CSV and its self-hash manifest.
    if (any(set(row) != set(COMPONENT_FIELDS) for row in components)
            or any(set(row) != set(EDGE_FIELDS) for row in links)):
        raise ValueError("lineage CSV schema or hidden fields changed")
    by_id = {row["candidate_id"]: row for row in components}
    if set(by_id) != {str(i) for i in range(1, 121)}:
        raise ValueError("candidate IDs missing, duplicated or forged")
    component_members = {}
    for row in components:
        digest = row["potential_lineage_component_sha256"]
        size = row["potential_lineage_component_size"]
        if (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                or not size.isdecimal() or int(size) < 1
                or row["lineage_review_status"] !=
                    "PENDING_INDEPENDENT_ADJUDICATION"
                or not row["repository"].strip()):
            raise ValueError("invalid pending-review component declaration")
        component_members.setdefault(digest, []).append(row)
    if any(int(row["potential_lineage_component_size"]) != len(members)
           for members in component_members.values() for row in members):
        raise ValueError("lineage component counts do not match members")
    if (stats.get("candidate_provenance_components") != len(component_members)
            or stats.get("multi_candidate_provenance_components") !=
                 sum(len(rows) > 1 for rows in component_members.values())):
        raise ValueError("lineage component summary conflicts with CSV members")
    edge_keys = set()
    observed_counts = {relation: 0 for relation in RELATIONS}
    for edge in links:
        a, b, relation, role = (
            edge["first_candidate_id"], edge["second_candidate_id"],
            edge["relation"], edge["source_role"]
        )
        if (a not in by_id or b not in by_id
                or int(a) >= int(b) or relation not in RELATIONS):
            raise ValueError("invalid, reversed or unknown lineage graph edge")
        key = (a, b, relation, role)
        if key in edge_keys:
            raise ValueError("duplicate lineage evidence edge")
        edge_keys.add(key)
        observed_counts[relation] += 1
        if (edge["evidence_label"] !=
                "SOURCED_METADATA_POTENTIAL_OVERLAP_NOT_PROVEN"
                or edge["split_action"] != (
                    "OWNER_ONLY_WARNING_DO_NOT_AUTO_GROUP"
                    if relation == "SAME_REPOSITORY_OWNER_HINT"
                    else "REVIEW_BEFORE_ANY_SPLIT"
                )):
            raise ValueError("lineage edge improperly claims independent adjudication")
        # A strong provenance edge MUST be within the same candidate
        # component; an owner-only warning is explicitly insufficient.
        if (relation != "SAME_REPOSITORY_OWNER_HINT"
                and by_id[a]["potential_lineage_component_sha256"] !=
                    by_id[b]["potential_lineage_component_sha256"]):
            raise ValueError("strong lineage edge crosses recorded components")
    if stats.get("relation_counts") != observed_counts:
        raise ValueError("edge relation summary does not match actual edge types")
    if (stats.get("owner_only_edges_not_used_for_union") is not True
            or stats.get("fork_and_git_edge_signals_not_confirmed_task_duplicates")
               is not True):
        raise ValueError("source-only lineage caution flags were changed")
    if (len(components) != 120
        or len({r["candidate_id"] for r in components}) != 120
        or any(r["experiment_eligible"] != "FALSE" or
               r["train_test_split_status"] != "BLOCKED"
               for r in components)
        or stats.get("canonical_candidates") != 120
        or stats.get("independent_train_test_split_frozen") is not False
        or stats.get("independently_admitted_executable_tasks") != 0
        or sum(stats.get("relation_counts", {}).values()) != len(links)
        or any(r["independently_adjudicated"] != "FALSE"
               for r in links)):
        raise ValueError("overlap graph falsifies completeness or split status")
    return {
        "status": "HASH_CHECKED_POTENTIAL_LINEAGE_WARNING_ONLY",
        "candidate_records": 120,
        "review_warning_edges": len(links),
        "verified_duplicate_tasks": 0,
        "approved_executable_tasks": 0,
        "verified_leakage_free_split": False,
    }
