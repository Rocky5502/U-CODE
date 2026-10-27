"""Conservative metadata provenance graph for U-CODE candidate leakage review.

Graph edges flag POTENTIAL repository/task overlap only. A common owner,
fork-parent hint or shared git commit does not prove two coding tasks are
duplicates. No automatic train/test assignment or executable task approval.
Uses only the canonical source-free 120-PR audit ledger.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
import io
from collections import defaultdict

from .dataset_curation import CuratedDataset

RELATIONS = (
    "SAME_FORK_PARENT_HINT",
    "CROSS_RECORD_GIT_SHA",
    "SAME_REPOSITORY_OWNER_HINT",
)
COMPONENT_FIELDS = (
    "candidate_id", "repository", "potential_lineage_component_sha256",
    "potential_lineage_component_size",
    "strong_provenance_links", "owner_only_warning_links",
    "lineage_review_status", "train_test_split_status",
    "experiment_eligible",
)
EDGE_FIELDS = (
    "first_candidate_id", "second_candidate_id",
    "relation", "source_role", "evidence_label", "split_action",
    "independently_adjudicated",
)


@dataclass(frozen=True)
class LeakageGraph:
    components: tuple[dict, ...]
    edges: tuple[dict, ...]
    summary: dict


def _csv(rows, fields):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields,
                            extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_graph_csv(graph: LeakageGraph):
    return {
        "possible_lineage_components_NOT_SPLIT.csv":
            _csv(graph.components, COMPONENT_FIELDS),
        "potential_cross_task_links_REVIEW_ONLY.csv":
            _csv(graph.edges, EDGE_FIELDS),
    }


def build_lineage_risk_graph(clean: CuratedDataset, audits: list[dict]) -> LeakageGraph:
    if not isinstance(clean, CuratedDataset) or len(clean.rows) != 120:
        raise ValueError("requires complete 120-record curated dataset")
    if len(audits) != 120 or len({
            x.get("candidate_id") for x in audits}) != 120:
        raise ValueError("requires complete unique canonical audit")
    by_id = {r["candidate_id"]: r for r in clean.rows}
    by_audit = {a["candidate_id"]: a for a in audits}
    if set(by_id) != set(by_audit):
        raise ValueError("clean/audit identity join is incomplete")
    id_list = sorted(by_id)
    parent = {i: i for i in id_list}
    links = set()
    strong_counter = {i: 0 for i in id_list}
    owner_counter = {i: 0 for i in id_list}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def join(a, b):
        aa, bb = find(a), find(b)
        if aa != bb:
            parent[max(aa, bb)] = min(aa, bb)

    def edge(a, b, relation, *, role=""):
        if a == b:
            return
        a, b = sorted((a, b))
        if relation not in RELATIONS:
            raise ValueError("unknown metadata lineage link")
        key = (a, b, relation, role)
        if key in links:
            return
        links.add(key)
        if relation != "SAME_REPOSITORY_OWNER_HINT":
            join(a, b)
            strong_counter[a] += 1
            strong_counter[b] += 1
        else:
            owner_counter[a] += 1
            owner_counter[b] += 1

    # Validate identities before graph building. Otherwise forged rows might
    # create false overlap edges or obscure actual provenance.
    for i in id_list:
        row, audit = by_id[i], by_audit[i]
        if (row["repository"] != audit.get("repository")
            or row["pr_url"] != audit.get("pr_url")
            or row["lineage_group_review"] != "PENDING_INDEPENDENT_REVIEW"
            or row["experiment_eligible"] != "FALSE"
            or row["split_status"] != "NOT_SPLIT_LINEAGE_AND_TASK_ADMISSION_PENDING"):
            raise ValueError("unverified lineage audit or changed metadata identity")

    def grouped(mapping, relation, role=""):
        for _, members in sorted(mapping.items()):
            members = sorted(set(members))
            if len(members) < 2:
                continue
            # Star instead of quadratic clique; guarantees connectivity
            # while making edge size scale linearly with candidate count.
            for member in members[1:]:
                edge(members[0], member, relation, role=role)

    lineage = defaultdict(list)
    owners = defaultdict(list)
    commit_refs: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i in id_list:
        row = by_id[i]
        audit = by_audit[i]
        repo = row["repository"]
        owners[repo.split("/", 1)[0].casefold()].append(i)
        lineage[row["lineage_group_hint"]].append(i)
        for role in ("base_sha", "head_sha", "merge_commit_sha"):
            sha = row[role]
            if sha:
                if sha != (audit.get(role) or ""):
                    raise ValueError("forged commit identity")
                commit_refs[(role, sha)].append(i)

    grouped(lineage, "SAME_FORK_PARENT_HINT")
    for (role, sha), items in sorted(commit_refs.items()):
        grouped({"same_commit": items}, "CROSS_RECORD_GIT_SHA",
                role=role)
    grouped(owners, "SAME_REPOSITORY_OWNER_HINT")

    by_component = defaultdict(list)
    for i in id_list:
        by_component[find(i)].append(i)
    component_ids = {}
    for members in by_component.values():
        stable_members = ",".join(str(i) for i in sorted(members))
        group_hash = sha256(
            ("U-CODE-POTENTIAL-LINEAGE-V1:" + stable_members)
            .encode("ascii")).hexdigest()
        for i in members:
            component_ids[i] = (group_hash, len(members))
    components = [{
        "candidate_id": i, "repository": by_id[i]["repository"],
        "potential_lineage_component_sha256": component_ids[i][0],
        "potential_lineage_component_size": component_ids[i][1],
        "strong_provenance_links": strong_counter[i],
        "owner_only_warning_links": owner_counter[i],
        "lineage_review_status": "PENDING_INDEPENDENT_ADJUDICATION",
        "train_test_split_status": "BLOCKED",
        "experiment_eligible": "FALSE",
    } for i in id_list]

    edges = [{
        "first_candidate_id": a, "second_candidate_id": b,
        "relation": relation, "source_role": role,
        "evidence_label": "SOURCED_METADATA_POTENTIAL_OVERLAP_NOT_PROVEN",
        "split_action": (
            "REVIEW_BEFORE_ANY_SPLIT"
            if relation != "SAME_REPOSITORY_OWNER_HINT"
            else "OWNER_ONLY_WARNING_DO_NOT_AUTO_GROUP"),
        "independently_adjudicated": "FALSE",
    } for a, b, relation, role in sorted(links)]
    groups = list(by_component.values())
    summary = {
        "schema_version": "1.0",
        "stage": "CONSERVATIVE_METADATA_LINEAGE_REVIEW_NOT_SPLIT",
        "canonical_candidates": len(components),
        "candidate_provenance_components": len(groups),
        "multi_candidate_provenance_components": sum(
            len(g) > 1 for g in groups),
        "candidates_with_nontrivial_provenance_links": sum(
            strong_counter[i] > 0 for i in id_list),
        "relation_counts": {
            relation: sum(x["relation"] == relation for x in edges)
            for relation in RELATIONS
        },
        "owner_only_edges_not_used_for_union": True,
        "fork_and_git_edge_signals_not_confirmed_task_duplicates": True,
        "independent_train_test_split_frozen": False,
        "independently_admitted_executable_tasks": 0,
        "source_code_fetched": False,
        "hidden_test_oracle_access": False,
    }
    return LeakageGraph(tuple(components), tuple(edges), summary)
