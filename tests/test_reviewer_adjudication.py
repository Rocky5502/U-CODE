"""Adversarial two-reviewer protocol tests; no reviewer work is implied."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.export_independent_review_forms import export_blank_reviewer_forms
from ucode.pending_review_packets import create_pending_review_packets
from ucode.reviewer_adjudication import (
    REQUIRED_GATES, adjudicate_review_disagreement, blank_independent_forms,
)


class IndependentReviewerProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets, _ = create_pending_review_packets()

    def work(self):
        forms = blank_independent_forms(self.packets)
        return deepcopy(list(forms["A"])), deepcopy(list(forms["B"]))

    @staticmethod
    def mark(row, name, verdict="EVIDENCE_PRESENT_NOT_ATTESTED"):
        row["reviewer_identity"] = name
        row["verdict"] = verdict
        row["reviewer_note"] = "Reviewed metadata path and identified pending evidence."
        if verdict == "EVIDENCE_PRESENT_NOT_ATTESTED":
            row["evidence_refs"] = ["https://github.com/source/project/issues/1"]
            row["evidence_sha256"] = "c"*64

    def test_twelve_by_eight_by_two_blank_reviews(self):
        forms = blank_independent_forms(self.packets)
        self.assertEqual(set(forms), {"A", "B"})
        for slot in ("A", "B"):
            self.assertEqual(len(forms[slot]), 12*len(REQUIRED_GATES))
            self.assertTrue(all(r["verdict"] == "PENDING"
                                and r["independent_approval"] is False
                                and not r["reviewer_identity"]
                                for r in forms[slot]))

    def test_neither_same_decision_nor_blank_sheet_admits_a_task(self):
        a, b = self.work()
        blank = adjudicate_review_disagreement(self.packets, a, b)
        self.assertEqual(blank.summary["pending_gate_pairs"], 96)
        self.assertIsNone(blank.summary["agreement_fraction_completed_pairs"])
        self.mark(a[0], "Reviewer A")
        self.mark(b[0], "Reviewer B")
        result = adjudicate_review_disagreement(self.packets, a, b)
        self.assertEqual(result.summary["completed_gate_pairs"], 1)
        self.assertEqual(result.summary["agreement_fraction_completed_pairs"], 1)
        self.assertEqual(result.summary["independently_admitted_executable_tasks"], 0)
        self.assertFalse(result.statuses[0]["independently_adjudicated"])

    def test_disagreement_recorded_and_not_auto_resolved(self):
        a, b = self.work()
        self.mark(a[0], "Reviewer A")
        self.mark(b[0], "Reviewer B", "REJECTED_WITH_REASON")
        out = adjudicate_review_disagreement(self.packets, a, b)
        self.assertEqual(out.summary["disagreements_on_completed_pairs"], 1)
        self.assertEqual(out.statuses[0]["status"],
                         "REVIEWER_DISAGREEMENT_NEEDS_ADJUDICATION")
        self.assertEqual(out.summary["independently_admitted_executable_tasks"], 0)

    def test_same_reviewer_cannot_fill_both_independent_slots(self):
        a, b = self.work()
        self.mark(a[0], "Single reviewer")
        self.mark(b[0], "Single reviewer")
        with self.assertRaisesRegex(ValueError, "must differ"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_evidence_positive_requires_digest_and_reference(self):
        a, b = self.work()
        self.mark(a[0], "Reviewer A")
        a[0]["evidence_sha256"] = ""
        with self.assertRaisesRegex(ValueError, "refs and SHA256"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_immutable_pr_and_source_packet_identity_protected(self):
        a, b = self.work()
        a[0]["packet_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "altered immutable"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_pending_must_have_no_pretend_review_notes(self):
        a, b = self.work()
        a[0]["reviewer_note"] = "Looked at all the code yesterday"
        with self.assertRaisesRegex(ValueError, "pending review"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_missing_or_duplicate_gate_is_rejected(self):
        a, b = self.work()
        with self.assertRaisesRegex(ValueError, "full 12"):
            adjudicate_review_disagreement(self.packets, a[:-1], b)
        a[1] = a[0]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_unknown_completion_authority_fields_rejected(self):
        a, b = self.work()
        a[0]["oracle_passed"] = True
        with self.assertRaisesRegex(ValueError, "schema drift"):
            adjudicate_review_disagreement(self.packets, a, b)

    def test_export_carries_no_claimed_human_findings(self):
        with TemporaryDirectory() as folder:
            summary = export_blank_reviewer_forms(Path(folder))
            self.assertEqual(summary["completed_gate_pairs"], 0)
            self.assertEqual(summary["independently_admitted_executable_tasks"], 0)
            files = {p.name for p in Path(folder).iterdir()}
            self.assertEqual(files, {
                "reviewer_A_96_PENDING.jsonl",
                "reviewer_B_96_PENDING.jsonl",
                "review_agreement_PENDING.json",
                "reviewer_forms_integrity.json",
            })
            index = json.loads(
                (Path(folder)/"reviewer_forms_integrity.json").read_text())
            self.assertTrue(index["two_reviewer_independence_not_authenticated"])


if __name__ == "__main__":
    unittest.main()
