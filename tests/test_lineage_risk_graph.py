"""Provenance graph regressions: no imaginary task deduplication or split."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import unittest

from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR
from scripts.summarize_audit import load_manifest, load_records
from ucode.dataset_curation import build_dataset
from ucode.lineage_risk_graph import (
    RELATIONS, build_lineage_risk_graph, export_graph_csv,
)

MANIFEST = load_manifest(SOURCE)
AUDIT = load_records(AUDIT_DIR, MANIFEST)
CLEAN = build_dataset(MANIFEST, AUDIT, sha256(SOURCE.read_bytes()).hexdigest())


class LineageRiskTests(unittest.TestCase):
    def test_graph_preserves_all_120_candidates(self):
        g = build_lineage_risk_graph(CLEAN, AUDIT)
        self.assertEqual(len(g.components), 120)
        self.assertEqual([x["candidate_id"] for x in g.components],
                         list(sorted(MANIFEST)))
        self.assertEqual(sum(x["relation"] in RELATIONS for x in g.edges),
                         len(g.edges))

    def test_graph_deterministic_when_raw_audit_reordered(self):
        original = build_lineage_risk_graph(CLEAN, AUDIT)
        other = build_lineage_risk_graph(CLEAN, list(reversed(AUDIT)))
        self.assertEqual(original, other)

    def test_never_assert_train_test_safety(self):
        graph = build_lineage_risk_graph(CLEAN, AUDIT)
        self.assertFalse(graph.summary["independent_train_test_split_frozen"])
        self.assertTrue(all(x["train_test_split_status"] == "BLOCKED"
                            for x in graph.components))
        self.assertTrue(all(x["experiment_eligible"] == "FALSE"
                            for x in graph.components))

    def test_star_graph_does_not_quadratically_expand_owner_groups(self):
        graph = build_lineage_risk_graph(CLEAN, AUDIT)
        self.assertLess(len(graph.edges), 3*120)
        self.assertTrue(all(x["split_action"] in (
            "REVIEW_BEFORE_ANY_SPLIT",
            "OWNER_ONLY_WARNING_DO_NOT_AUTO_GROUP")
            for x in graph.edges))

    def test_fork_group_link_creates_potential_component_only(self):
        rows = deepcopy(CLEAN.rows)
        rows[0]["lineage_group_hint"] = "shared/upstream"
        rows[1]["lineage_group_hint"] = "shared/upstream"
        modified = replace(CLEAN, rows=tuple(rows))
        graph = build_lineage_risk_graph(modified, AUDIT)
        self.assertEqual(graph.components[0]["potential_lineage_component_sha256"],
                         graph.components[1]["potential_lineage_component_sha256"])
        self.assertTrue(any(x["relation"] == "SAME_FORK_PARENT_HINT"
                            and x["first_candidate_id"] == 1
                            and x["second_candidate_id"] == 2
                            for x in graph.edges))
        self.assertEqual(graph.components[0]["lineage_review_status"],
                         "PENDING_INDEPENDENT_ADJUDICATION")

    def test_shared_commit_link_preserves_evidence_role(self):
        rows = deepcopy(CLEAN.rows)
        audits = deepcopy(AUDIT)
        src_sha = rows[0]["base_sha"]
        self.assertEqual(len(src_sha), 40)
        rows[1]["base_sha"] = src_sha
        audit_idx = next(i for i, x in enumerate(audits)
                         if x["candidate_id"] == 2)
        audits[audit_idx]["base_sha"] = src_sha
        modified = replace(CLEAN, rows=tuple(rows))
        graph = build_lineage_risk_graph(modified, audits)
        self.assertTrue(any(x["relation"] == "CROSS_RECORD_GIT_SHA"
                            and x["source_role"] == "base_sha"
                            for x in graph.edges))

    def test_cross_role_head_to_base_shared_commit_is_flagged(self):
        rows = deepcopy(CLEAN.rows)
        audits = deepcopy(AUDIT)
        shared_sha = rows[0]["head_sha"]
        rows[1]["base_sha"] = shared_sha
        for record in audits:
            if record["candidate_id"] == 2:
                record["base_sha"] = shared_sha
                break
        graph = build_lineage_risk_graph(
            replace(CLEAN, rows=tuple(rows)), audits)
        edges = [e for e in graph.edges
                 if e["relation"] == "CROSS_RECORD_GIT_SHA"
                 and {e["first_candidate_id"], e["second_candidate_id"]}
                 == {1, 2}]
        self.assertTrue(edges)
        self.assertTrue(any("head_sha" in e["source_role"]
                            and "base_sha" in e["source_role"]
                            for e in edges))
        self.assertEqual(
            graph.components[0]["potential_lineage_component_sha256"],
            graph.components[1]["potential_lineage_component_sha256"])
        self.assertFalse(graph.summary["independent_train_test_split_frozen"])

    def test_forged_sha_link_rejected(self):
        rows = deepcopy(CLEAN.rows)
        rows[1]["base_sha"] = rows[0]["base_sha"]
        modified = replace(CLEAN, rows=tuple(rows))
        with self.assertRaisesRegex(ValueError, "forged commit"):
            build_lineage_risk_graph(modified, AUDIT)

    def test_modified_repo_record_rejected(self):
        rows = deepcopy(CLEAN.rows)
        rows[1]["repository"] = "different/synthetic"
        with self.assertRaisesRegex(ValueError, "changed metadata identity"):
            build_lineage_risk_graph(replace(CLEAN, rows=tuple(rows)), AUDIT)

    def test_duplicate_audit_id_rejected(self):
        audits = deepcopy(AUDIT)
        audits[0]["candidate_id"] = audits[1]["candidate_id"]
        with self.assertRaisesRegex(ValueError, "unique canonical"):
            build_lineage_risk_graph(CLEAN, audits)

    def test_owner_only_warning_does_not_join_components(self):
        rows = deepcopy(CLEAN.rows)
        rows[0]["repository"] = "same-owner/alpha"
        rows[1]["repository"] = "same-owner/beta"
        audits = deepcopy(AUDIT)
        aud = {r["candidate_id"]: r for r in audits}
        aud[1]["repository"] = "same-owner/alpha"
        aud[2]["repository"] = "same-owner/beta"
        graph = build_lineage_risk_graph(replace(CLEAN, rows=tuple(rows)), audits)
        self.assertTrue(any(x["relation"] == "SAME_REPOSITORY_OWNER_HINT"
                            and x["first_candidate_id"] == 1
                            and x["second_candidate_id"] == 2
                            for x in graph.edges))

    def test_source_free_exports_are_compact(self):
        graph = build_lineage_risk_graph(CLEAN, AUDIT)
        exports = export_graph_csv(graph)
        self.assertEqual(len(exports), 2)
        self.assertLess(sum(len(x) for x in exports.values()), 200_000)
        self.assertTrue(all("NOT_SPLIT" in name or "REVIEW_ONLY" in name
                            for name in exports))

    def test_component_labels_consistent(self):
        graph = build_lineage_risk_graph(CLEAN, AUDIT)
        sizes = {}
        for r in graph.components:
            digest = r["potential_lineage_component_sha256"]
            self.assertEqual(len(digest), 64)
            sizes[digest] = sizes.get(digest, 0) + 1
        for r in graph.components:
            self.assertEqual(
                r["potential_lineage_component_size"],
                sizes[r["potential_lineage_component_sha256"]])


if __name__ == "__main__":
    unittest.main()
