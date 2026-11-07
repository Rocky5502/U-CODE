"""Adversarial filled-review privacy/triage tests with invented reviewer data.

All sample reviewer names, notes, evidence URLs and SHA values are
SYNTHETIC. No external person reviewed or independently approved a task.
"""
from copy import deepcopy
from hashlib import sha256
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_private_review_forms import (
    audit_private_review_forms, main as audit_cli, read_private_review_rows,
)
from ucode.pending_review_packets import create_pending_review_packets
from ucode.reviewer_adjudication import (
    adjudicate_review_disagreement, blank_independent_forms,
)


class LocalReviewerInboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets, _ = create_pending_review_packets()

    def make_forms(self):
        forms = blank_independent_forms(self.packets)
        return deepcopy(list(forms["A"])), deepcopy(list(forms["B"]))

    @staticmethod
    def mark(row, slot, *, verdict="EVIDENCE_PRESENT_NOT_ATTESTED",
             digest=None, reference=None):
        row["reviewer_identity"] = "SYNTHETIC_REVIEWER_" + slot
        row["verdict"] = verdict
        row["reviewer_note"] = "SYNTHETIC_PRIVATE_REVIEWER_NOTE_DONT_PUBLISH"
        row["evidence_refs"] = [
            reference or "SYNTHETIC_PRIVATE_EVIDENCE_URL_DONT_PUBLISH"
        ]
        row["evidence_sha256"] = (
            digest if digest is not None else sha256(b"SYNTHETIC_EVIDENCE").hexdigest()
        )

    @staticmethod
    def dump(folder, a, b):
        paths = []
        for slot, rows in (("A", a), ("B", b)):
            p = Path(folder, slot + "_review.jsonl")
            p.write_text("".join(json.dumps(r, sort_keys=True) + "\n"
                                 for r in rows), encoding="utf-8")
            paths.append(p)
        return paths

    def test_blank_forms_preserve_96_pending_and_zero_authority(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            out = audit_private_review_forms(x, y)
            self.assertEqual(out["gate_pairs"], 96)
            self.assertEqual(out["pending_gate_pairs"], 96)
            self.assertEqual(out["paired_nonpending_claims"], 0)
            self.assertIsNone(out["verdict_agreement_fraction_on_paired_claims"])
            self.assertEqual(out["independently_admitted_executable_tasks"], 0)
            self.assertFalse(out["reviewer_identity_authenticated"])

    def test_same_positive_verdict_but_different_artifact_is_NOT_agreement(self):
        a, b = self.make_forms()
        self.mark(a[0], "A")
        self.mark(b[0], "B", digest="f"*64)
        raw = adjudicate_review_disagreement(self.packets, a, b)
        self.assertEqual(raw.summary["completed_gate_pairs"], 1)
        self.assertEqual(raw.summary["positive_evidence_digest_mismatches"], 1)
        self.assertEqual(raw.summary["disagreements_on_completed_pairs"], 1)
        self.assertEqual(raw.summary["agreement_fraction_completed_pairs"], 0)
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            report = audit_private_review_forms(x, y)
        self.assertEqual(
            report["statuses_public_only"][0]["triage_status"],
            "EVIDENCE_DIGEST_MISMATCH_NEEDS_ADJUDICATION")
        self.assertFalse(report["statuses_public_only"][0]["adjudicated"])
        self.assertFalse(report["statuses_public_only"][0]["eligible_for_experiment"])

    def test_identical_artifact_different_reference_requires_reconciliation(self):
        a, b = self.make_forms()
        self.mark(a[0], "A")
        self.mark(b[0], "B", reference="SYNTHETIC_ALT_PRIVATE_SOURCE")
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            r = audit_private_review_forms(x, y)
        self.assertEqual(r["positive_evidence_reference_mismatch_pairs"], 1)
        self.assertEqual(r["disagreement_pairs"], 1)
        self.assertIn("REFERENCES_DIFFER", r["statuses_public_only"][0]["triage_status"])

    def test_same_artifact_and_verdict_is_only_not_adjudicated_agreement(self):
        a, b = self.make_forms()
        self.mark(a[0], "A")
        self.mark(b[0], "B")
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            r = audit_private_review_forms(x, y)
        self.assertEqual(r["paired_nonpending_claims"], 1)
        self.assertEqual(r["verdict_agreement_fraction_on_paired_claims"], 1)
        self.assertEqual(r["disagreement_pairs"], 0)
        self.assertEqual(r["independently_admitted_executable_tasks"], 0)
        self.assertEqual(r["statuses_public_only"][0]["triage_status"],
                         "REVIEWERS_AGREE_NOT_ADJUDICATED")

    def test_complete_positive_96_pairs_cannot_admit_a_single_task(self):
        a, b = self.make_forms()
        for row in a:
            self.mark(row, "A")
        for row in b:
            self.mark(row, "B")
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            r = audit_private_review_forms(x, y)
        self.assertEqual(r["paired_nonpending_claims"], 96)
        self.assertEqual(r["pending_gate_pairs"], 0)
        self.assertEqual(r["independently_admitted_executable_tasks"], 0)
        self.assertFalse(r["reviewer_independence_authenticated"])
        self.assertFalse(r["evidence_contents_authenticated"])
        self.assertTrue(all(not x["eligible_for_experiment"]
                            for x in r["statuses_public_only"]))

    def test_redacted_output_never_exposes_names_notes_or_evidence(self):
        a, b = self.make_forms()
        self.mark(a[0], "A")
        self.mark(b[0], "B", digest="e"*64)
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            report = audit_private_review_forms(x, y)
            public = json.dumps(report, sort_keys=True)
            self.assertNotIn("SYNTHETIC_REVIEWER_", public)
            self.assertNotIn("SYNTHETIC_PRIVATE_", public)
            self.assertNotIn("e"*64, public)
            self.assertNotIn("evidence_sha256", public)
            out = Path(tmp, "redacted.json")
            with redirect_stdout(io.StringIO()) as captured:
                self.assertEqual(audit_cli([
                    "--reviewer-a", str(x),
                    "--reviewer-b", str(y),
                    "--output", str(out),
                ]), 0)
            self.assertEqual(captured.getvalue(), out.read_text())
            self.assertNotIn("SYNTHETIC_REVIEWER_", out.read_text())
            self.assertNotIn("SYNTHETIC_PRIVATE_", out.read_text())

    def test_unknown_gold_or_self_approval_is_rejected(self):
        a, b = self.make_forms()
        for key, value in (("independent_approval", True),
                           ("oracle_passed", True)):
            bad = deepcopy(a)
            bad[0][key] = value
            with TemporaryDirectory() as tmp:
                x, y = self.dump(tmp, bad, b)
                with self.assertRaisesRegex(ValueError, "approve|schema"):
                    audit_private_review_forms(x, y)

    def test_same_reviewer_identity_between_slots_is_refused(self):
        a, b = self.make_forms()
        self.mark(a[0], "A")
        self.mark(b[0], "A")
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            with self.assertRaisesRegex(ValueError, "identities must differ"):
                audit_private_review_forms(x, y)

    def test_duplicate_json_keys_are_fail_closed(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            lines = x.read_text().splitlines()
            lines[0] = lines[0][:-1] + ',"verdict":"PENDING"}'
            x.write_text("\n".join(lines) + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                read_private_review_rows(x)

    def test_missing_inventory_or_duplicate_review_is_rejected(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a[:-1], b)
            with self.assertRaisesRegex(ValueError, "96-row"):
                audit_private_review_forms(x, y)
        a, b = self.make_forms()
        a[1] = deepcopy(a[0])
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                audit_private_review_forms(x, y)

    def test_symlink_and_same_input_file_refused(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            with self.assertRaisesRegex(ValueError, "distinct local"):
                audit_private_review_forms(x, x)
            link = Path(tmp, "fake_A.jsonl")
            try:
                link.symlink_to(x)
            except (OSError, NotImplementedError):
                return
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                audit_private_review_forms(link, y)

    def test_bound_oversized_json_lines_and_nonstandard_nan(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            lines = x.read_text().splitlines()
            lines[0] = lines[0][:-1] + ',"fake_bad":NaN}'
            x.write_text("\n".join(lines)+"\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "NaN/Infinity"):
                read_private_review_rows(x)
            x.write_bytes(b"x"* (2*1024*1024 + 1))
            with self.assertRaisesRegex(ValueError, "size"):
                read_private_review_rows(x)

    def test_redacted_output_cannot_overwrite_private_input(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            before = x.read_bytes()
            with redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    ValueError, "must not overwrite private"):
                audit_cli([
                    "--reviewer-a", str(x),
                    "--reviewer-b", str(y),
                    "--output", str(x),
                ])
            self.assertEqual(x.read_bytes(), before)

    def test_reader_rejects_invalid_unicode_and_private_summary_wont_contain_raw(self):
        a, b = self.make_forms()
        with TemporaryDirectory() as tmp:
            x, y = self.dump(tmp, a, b)
            data = x.read_bytes().splitlines()
            data[0] = b"\xff" + data[0]
            x.write_bytes(b"\n".join(data)+b"\n")
            with self.assertRaisesRegex(ValueError, "UTF-8"):
                read_private_review_rows(x)


if __name__ == "__main__":
    unittest.main()
