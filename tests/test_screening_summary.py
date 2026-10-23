import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from scripts.summarize_audit import load_manifest, audit_files, load_records, summarize


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/discovery/agent_pr_candidates_120.csv"
AUDIT_DIR = ROOT / "data/audits/2026-10-24"


class ScreeningSummaryTests(unittest.TestCase):
    def test_reads_canonical_files_without_duplicate_partial_batches(self):
        files = audit_files(AUDIT_DIR)
        self.assertTrue(any("stratified_24_" in p.name for p in files))
        self.assertTrue(all(not p.name.startswith("batch_") for p in files))

    def test_canonical_screening_record_invariants(self):
        manifest = load_manifest(MANIFEST)
        rows = load_records(AUDIT_DIR, manifest)
        self.assertEqual(len(manifest), 120)
        self.assertGreaterEqual(len(rows), 48)
        self.assertEqual(len(rows), len({x["candidate_id"] for x in rows}))
        self.assertTrue(all(x["dataset_eligible"] is False for x in rows))
        self.assertTrue(all(x["repository"] == manifest[x["candidate_id"]]["repository"]
                            for x in rows))

    def test_summary_cross_checks_discovery_and_source_units(self):
        manifest = load_manifest(MANIFEST)
        rows = load_records(AUDIT_DIR, manifest)
        out = summarize(rows, manifest)
        self.assertEqual(out["screened"] + out["not_screened"], 120)
        self.assertEqual(sum(out["source_status_counts"].values()), out["screened"])
        self.assertEqual(out["independently_eligible_units"], 0)
        self.assertIn(14, out["language_mismatch_candidate_ids"])

    def test_manifest_repo_mismatch_fails_closed(self):
        manifest = load_manifest(MANIFEST)
        with TemporaryDirectory() as td:
            p = Path(td) / "stratified_offset4_ids04_14_24.jsonl"
            p.write_text(json.dumps({
                "candidate_id": 4, "repository": "wrong/example",
                "pr_url": manifest[4]["agent_pr_url"],
                "triage_status": "non_source_change", "dataset_eligible": False,
            }) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(td, manifest)

    def test_duplicate_record_ids_fail_closed(self):
        manifest = load_manifest(MANIFEST)
        with TemporaryDirectory() as td:
            p = Path(td) / "stratified_offset4_ids04_14_24.jsonl"
            row = {
                "candidate_id": 4, "repository": manifest[4]["repository"],
                "pr_url": manifest[4]["agent_pr_url"],
                "triage_status": "non_source_change", "dataset_eligible": False,
            }
            p.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n",
                         encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(td, manifest)


if __name__ == "__main__":
    unittest.main()
