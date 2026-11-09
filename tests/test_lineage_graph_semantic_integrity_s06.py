"""S06: structural lineage integrity despite an attacker updating self-hashes.

All candidate data are historical PR metadata, not executable tasks.
No clone, network, test oracle, independent ancestry proof or split occurs.
"""
import csv
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_lineage_risks import run as build_review_bundle
from ucode.lineage_graph_verify import verify_lineage_review


EDGES = "potential_cross_task_links_REVIEW_ONLY.csv"
COMPONENTS = "possible_lineage_components_NOT_SPLIT.csv"
STATS = "lineage_graph_report.json"
INTEGRITY = "lineage_graph_integrity.json"


class SemanticGraphIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        build_review_bundle(self.root)

    def _read(self, name):
        with (self.root/name).open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def _write_and_self_rehash(self, name, rows):
        path = self.root/name
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        data = json.loads((self.root/INTEGRITY).read_text("utf-8"))
        data["output_sha256"][name] = sha256(path.read_bytes()).hexdigest()
        (self.root/INTEGRITY).write_text(json.dumps(
            data, indent=2, sort_keys=True
        ) + "\n", encoding="utf-8")

    def test_authentic_first_party_export_is_only_a_warning(self):
        output = verify_lineage_review(self.root)
        self.assertEqual(output["candidate_records"], 120)
        self.assertEqual(output["approved_executable_tasks"], 0)
        self.assertFalse(output["verified_leakage_free_split"])

    def test_reversed_edge_endpoints_rejected_even_if_self_rehashed(self):
        rows = self._read(EDGES)
        self.assertTrue(rows)
        row = rows[0]
        row["first_candidate_id"], row["second_candidate_id"] = (
            row["second_candidate_id"], row["first_candidate_id"]
        )
        self._write_and_self_rehash(EDGES, rows)
        with self.assertRaisesRegex(ValueError, "reversed"):
            verify_lineage_review(self.root)

    def test_duplicate_edge_rejected_even_with_new_integrity_digest(self):
        rows = self._read(EDGES)
        rows.append(dict(rows[0]))
        self._write_and_self_rehash(EDGES, rows)
        with self.assertRaisesRegex(ValueError, "duplicate lineage"):
            verify_lineage_review(self.root)

    def test_fake_public_edge_adjudication_rejected_after_rehash(self):
        rows = self._read(EDGES)
        rows[0]["evidence_label"] = "INDEPENDENTLY_APPROVED"
        self._write_and_self_rehash(EDGES, rows)
        with self.assertRaisesRegex(ValueError, "improperly claims"):
            verify_lineage_review(self.root)

    def test_forged_relation_label_rejected_after_rehash(self):
        rows = self._read(EDGES)
        rows[0]["relation"] = "INFERRED_HIDDEN_DUPLICATE"
        self._write_and_self_rehash(EDGES, rows)
        with self.assertRaisesRegex(ValueError, "unknown lineage"):
            verify_lineage_review(self.root)

    def test_invented_candidate_identifier_rejected_after_rehash(self):
        rows = self._read(COMPONENTS)
        rows[0]["candidate_id"] = "121"
        self._write_and_self_rehash(COMPONENTS, rows)
        with self.assertRaisesRegex(ValueError, "candidate IDs"):
            verify_lineage_review(self.root)

    def test_declared_component_size_rejected_after_rehash(self):
        rows = self._read(COMPONENTS)
        rows[0]["potential_lineage_component_size"] = "999"
        self._write_and_self_rehash(COMPONENTS, rows)
        with self.assertRaisesRegex(ValueError, "component counts"):
            verify_lineage_review(self.root)

    def test_unchanged_edges_but_forged_relation_summary_rejected(self):
        obj = json.loads((self.root/STATS).read_text("utf-8"))
        relation = sorted(obj["relation_counts"])[0]
        obj["relation_counts"][relation] += 1
        p = self.root/STATS
        p.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n",
                     encoding="utf-8")
        integrity = json.loads((self.root/INTEGRITY).read_text("utf-8"))
        integrity["output_sha256"][STATS] = sha256(p.read_bytes()).hexdigest()
        (self.root/INTEGRITY).write_text(
            json.dumps(integrity, indent=2, sort_keys=True)+"\n",
            encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "edge relation summary"):
            verify_lineage_review(self.root)

    def test_forged_strong_link_cannot_cross_distinct_components(self):
        # The real 120-record metadata can have ZERO strong links. Do not
        # invent a real link merely to make a regression pass. Forge one
        # only inside a temporary first-party copy and rewrite its SHA.
        rows = self._read(EDGES)
        members = self._read(COMPONENTS)
        first = members[0]
        second = next(
            r for r in members if
            r["potential_lineage_component_sha256"] !=
            first["potential_lineage_component_sha256"]
        )
        template = dict(rows[0])
        template.update({
            "first_candidate_id": str(min(
                int(first["candidate_id"]), int(second["candidate_id"]))),
            "second_candidate_id": str(max(
                int(first["candidate_id"]), int(second["candidate_id"]))),
            "relation": "SAME_FORK_PARENT_HINT",
            "source_role": "",
            "evidence_label":
                "SOURCED_METADATA_POTENTIAL_OVERLAP_NOT_PROVEN",
            "split_action": "REVIEW_BEFORE_ANY_SPLIT",
            "independently_adjudicated": "FALSE",
        })
        rows.append(template)
        self._write_and_self_rehash(EDGES, rows)
        with self.assertRaisesRegex(
                ValueError, "strong lineage edge crosses recorded"):
            verify_lineage_review(self.root)

    def test_hash_without_external_signature_does_not_prove_split(self):
        output = verify_lineage_review(self.root)
        self.assertNotIn("independent_reviewer_signature", output)
        self.assertNotIn("verified_task_duplicate_count", output)
        self.assertEqual(output["verified_duplicate_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
