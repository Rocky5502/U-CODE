"""No-execution 12-candidate task evidence packet tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR
from scripts.summarize_audit import load_manifest, load_records
from scripts.check_task_admission import validate_prospective_dossiers
from ucode.pending_review_packets import (
    create_pending_review_packets, export_pending_review_packets,
)
from ucode.task_admission import REQUIRED_GATES, parse_dossier


class PendingReviewPacketTests(unittest.TestCase):
    def test_all_twelve_review_only_packets_have_8_open_gates(self):
        packets, report = create_pending_review_packets()
        self.assertEqual(len(packets), 12)
        self.assertEqual(report["pending_eight_gate_checks"], 96)
        self.assertEqual(report["independent_review_approvals"], 0)
        self.assertEqual(report["scientifically_admitted_executable_tasks"], 0)
        for p in packets:
            self.assertEqual({g["gate"] for g in p["gates"]},
                             set(REQUIRED_GATES))
            self.assertTrue(all(g["status"] == "PENDING" for g in p["gates"]))
            self.assertEqual(p["evidence_stage"], "MANUAL_REVIEW_ONLY")
            self.assertEqual(parse_dossier(p).candidate_id, p["candidate_id"])

    def test_stable_distinct_candidate_ids(self):
        a, ra = create_pending_review_packets()
        b, rb = create_pending_review_packets()
        self.assertEqual(a, b)
        self.assertEqual(ra, rb)
        self.assertEqual(len(set(x["candidate_id"] for x in a)), 12)

    def test_exports_do_not_claim_reviewers_or_correctness(self):
        with TemporaryDirectory() as path:
            status = export_pending_review_packets(path)
            files = {x.name for x in Path(path).iterdir()}
            self.assertEqual(files, {
                "review_packet_12_PENDING.jsonl",
                "review_packet_summary.json",
                "review_packet_integrity.json",
            })
            self.assertFalse(status["model_inference_executed"])
            self.assertFalse(status["third_party_code_executed"])
            saved = [json.loads(s) for s in (
                Path(path)/"review_packet_12_PENDING.jsonl").read_text(
                    "utf-8").splitlines() if s]
            self.assertEqual(len(saved), 12)
            self.assertFalse(any(
                g["status"] != "PENDING" for p in saved for g in p["gates"]))

    def test_existing_canonical_checker_accepts_all_pending_templates(self):
        with TemporaryDirectory() as path:
            export_pending_review_packets(path)
            manifest = load_manifest(SOURCE)
            records = load_records(AUDIT_DIR, manifest)
            result = validate_prospective_dossiers(
                records, manifest,
                Path(path)/"review_packet_12_PENDING.jsonl")
            self.assertEqual(len(result), 12)
            self.assertTrue(all(not x["eligible_for_experiment"]
                                and len(x["open_gates"]) == 8
                                for x in result))

    def test_can_not_change_number_of_queue_records_without_new_reg(self):
        with self.assertRaisesRegex(ValueError, "frozen 12"):
            create_pending_review_packets(limit=10)


if __name__ == "__main__":
    unittest.main()
