"""Dataset data-quality audit: deterministic real-metadata checks + falsifiers.

Only checks published PR metadata. These tests do not execute third-party
repositories or claim licenses, correctness labels or gold patch validity.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR
from scripts.summarize_audit import load_manifest, load_records
from scripts.audit_dataset_quality import audit_release
from ucode.dataset_curation import build_dataset
from ucode.dataset_quality import (
    dataset_schema, release_integrity_manifest,
    source_file_digests, validate_release,
)


class MetadataQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load_manifest(SOURCE)
        cls.audits = load_records(AUDIT_DIR, cls.original)
        cls.data = build_dataset(cls.original, cls.audits,
                                 sha256(SOURCE.read_bytes()).hexdigest())

    def test_complete_quality_gate(self):
        result = validate_release(self.data, self.audits)
        self.assertEqual(result.report["candidate_pr_count"], 120)
        self.assertEqual(result.report["audit_joined_rows"], 120)
        self.assertFalse(result.report["scientific_data_submission_ready"])
        self.assertEqual(result.report["approved_executable_tasks"], 0)

    def test_each_original_search_language_has_ten_links(self):
        report = validate_release(self.data, self.audits).report
        self.assertEqual(set(report["query_language_strata"]), {
            "Python", "JavaScript", "TypeScript", "Java", "Go",
            "Rust", "C++", "C", "C#", "Kotlin", "PHP", "Ruby",
        })
        self.assertEqual(set(report["query_language_strata"].values()), {10})

    def test_review_flags_do_not_claim_acceptance(self):
        result = validate_release(self.data, self.audits)
        self.assertTrue(result.reviewer_leakage_flags)
        self.assertTrue(all(not x["task_eligible"]
                            for x in result.reviewer_leakage_flags))

    def test_raw_to_clean_identity_join_fails_closed(self):
        audit = deepcopy(self.audits)
        audit[0]["repository"] = "forged/other"
        with self.assertRaisesRegex(ValueError, "identity join"):
            validate_release(self.data, audit)

    def test_no_forged_task_success_label(self):
        rows = list(deepcopy(self.data.rows))
        rows[0]["hidden_tests"] = {"oracle_passed": True}
        changed = type(self.data)(tuple(rows), self.data.review_queue,
                                  self.data.language_summary, self.data.report)
        with self.assertRaisesRegex(ValueError, "schema drift"):
            validate_release(changed, self.audits)

    def test_no_false_license_privilege(self):
        rows = list(deepcopy(self.data.rows))
        rows[0]["source_rights_verified"] = "TRUE"
        changed = type(self.data)(tuple(rows), self.data.review_queue,
                                  self.data.language_summary, self.data.report)
        with self.assertRaisesRegex(ValueError, "privileged approvals"):
            validate_release(changed, self.audits)

    def test_no_fake_split_approval(self):
        rows = list(deepcopy(self.data.rows))
        rows[0]["split_status"] = "TEST_VERIFIED"
        changed = type(self.data)(tuple(rows), self.data.review_queue,
                                  self.data.language_summary, self.data.report)
        with self.assertRaisesRegex(ValueError, "train/test split"):
            validate_release(changed, self.audits)

    def test_no_duplicate_primary_key(self):
        rows = list(deepcopy(self.data.rows))
        rows[1]["candidate_id"] = rows[0]["candidate_id"]
        changed = type(self.data)(tuple(rows), self.data.review_queue,
                                  self.data.language_summary, self.data.report)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_release(changed, self.audits)

    def test_missing_join_record_rejected(self):
        with self.assertRaisesRegex(ValueError, "120-link"):
            validate_release(self.data, self.audits[:-1])

    def test_commit_sha_drift_rejected(self):
        rows = list(deepcopy(self.data.rows))
        rows[0]["base_sha"] = "f"*40 if rows[0]["base_sha"] != "f"*40 else "a"*40
        # Even a syntactically valid, tampered SHA must be rejected.
        changed = type(self.data)(tuple(rows), self.data.review_queue,
                                  self.data.language_summary, self.data.report)
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            validate_release(changed, self.audits)

    def test_schema_documents_pre_and_post_change_shas(self):
        s = dataset_schema()
        self.assertIn("head_sha", s["columns"])
        self.assertIn("must NEVER", s["field_notes"]["head_sha"])
        self.assertEqual(s["scientific_task_admission"], "NONE")

    def test_same_file_source_digest_stable(self):
        p = SOURCE
        a = source_file_digests(p, [])
        b = source_file_digests(p, [])
        self.assertEqual(a, b)
        self.assertEqual(a[p.as_posix()], sha256(p.read_bytes()).hexdigest())

    def test_repeated_provenance_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "repeated source"):
            source_file_digests(SOURCE, [SOURCE])

    def test_release_receipt_has_bytes_and_sha256(self):
        data = {"meta.csv": b"task_id,eligible\n1,FALSE\n"}
        source = {str(SOURCE): sha256(SOURCE.read_bytes()).hexdigest()}
        receipt = release_integrity_manifest(data, source)
        self.assertEqual(receipt["output_digests"]["meta.csv"]["bytes"],
                         len(data["meta.csv"]))
        self.assertEqual(receipt["output_digests"]["meta.csv"]["sha256"],
                         sha256(data["meta.csv"]).hexdigest())
        self.assertTrue(receipt["no_independently_verified_tasks"])

    def test_file_path_traversal_in_release_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "relative"):
            release_integrity_manifest({"../escape.csv": b"unsafe"}, {})

    def test_bad_source_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            release_integrity_manifest({"clean.csv": b""}, {"source": "fake"})

    def test_full_eight_file_source_only_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_release(output_dir=Path(tmp))
            self.assertEqual(report["file_count"], 8)
            self.assertEqual(report["experiment_eligible"], 0)
            self.assertFalse(report["scientific_data_submission_ready"])
            data = json.loads((Path(tmp)/"quality_report.json").read_text())
            assert not data["scientific_data_submission_ready"]
            self.assertEqual(len(list(Path(tmp).iterdir())), 8)
            manifest = json.loads((Path(tmp)/"release_integrity.json").read_text())
            for name, info in manifest["output_digests"].items():
                content = (Path(tmp)/name).read_bytes()
                self.assertEqual(info["sha256"], sha256(content).hexdigest())
            self.assertLess(sum(p.stat().st_size for p in Path(tmp).iterdir()),
                            500_000)


if __name__ == "__main__":
    unittest.main()
