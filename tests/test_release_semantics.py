"""Resigned manifest attack tests: hashes alone cannot establish data meaning.

Every test starts from actual 120 PR metadata only; no repository source,
oracle labels, real model inference or external network.
"""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from hashlib import sha256

from scripts.audit_dataset_quality import audit_release
from scripts.verify_dataset_release import verify_dataset_release


def resign(folder: Path, name: str, raw: bytes):
    """Simulate an adversary recomputing internally consistent file SHA."""
    (folder/name).write_bytes(raw)
    manifest_path=folder/"release_integrity.json"
    manifest=json.loads(manifest_path.read_text("utf-8"))
    manifest["output_digests"][name]={
        "sha256":sha256(raw).hexdigest(),"bytes":len(raw)}
    manifest_path.write_text(json.dumps(manifest),encoding="utf-8")


def rewrite_csv(folder: Path, filename: str, editor):
    p=folder/filename
    with p.open(newline="",encoding="utf-8") as h:
        reader=csv.DictReader(h)
        fields=reader.fieldnames
        rows=list(reader)
    editor(rows)
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    resign(folder,filename,out.getvalue().encode("utf-8"))


class MetadataReleaseSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        audit_release(output_dir=cls.root)
        cls.original={p.name:p.read_bytes() for p in cls.root.iterdir()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        for name,data in self.original.items():
            (self.root/name).write_bytes(data)

    def test_real_metadata_snapshot_is_semantically_consistent(self):
        result=verify_dataset_release(self.root)
        self.assertEqual(result["metadata_record_count"],120)
        check=result["semantic_audit"]
        self.assertEqual(check["metadata_retrieved"],119)
        self.assertEqual(check["production_source_path_leads"],62)
        self.assertEqual(check["shortlisted_manual_review"],12)
        self.assertEqual(check["approved_executable_tasks"],0)
        self.assertFalse(check["actual_changed_language_coverage_verified"])

    def test_self_resigned_false_oracle_flag_is_rejected(self):
        def corrupt(rows):
            rows[0]["sealed_independent_oracle_verified"]="TRUE"
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"falsely promoted"):
            verify_dataset_release(self.root)

    def test_self_resigned_duplicate_candidate_is_rejected(self):
        def corrupt(rows):
            rows[1]["candidate_id"]=rows[0]["candidate_id"]
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            verify_dataset_release(self.root)

    def test_self_resigned_retrieval_promotion_is_rejected(self):
        def corrupt(rows):
            failed=next(row for row in rows
                         if row["metadata_source_status"]!="retrieved")
            failed["metadata_source_status"]="retrieved"
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"retrieval"):
            verify_dataset_release(self.root)

    def test_self_resigned_wrong_search_language_is_rejected(self):
        def corrupt(rows):
            rows[0]["search_language"]="InventedLanguage"
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"language"):
            verify_dataset_release(self.root)

    def test_self_resigned_shortlist_inflation_is_rejected(self):
        def corrupt(rows):
            row=next(x for x in rows if x["review_shortlist"]=="FALSE")
            row["review_shortlist"]="TRUE"
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"shortlist"):
            verify_dataset_release(self.root)

    def test_self_resigned_forged_review_queue_is_rejected(self):
        def corrupt(rows):
            rows[0]["repository"]="counterfeit/repo"
        rewrite_csv(self.root,"manual_review_12_NOT_EXECUTABLE.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"review queue"):
            verify_dataset_release(self.root)

    def test_self_resigned_forged_language_summary_is_rejected(self):
        def corrupt(rows):
            rows[0]["source_path_leads"]="99"
        rewrite_csv(self.root,"language_strata.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"language-stratum"):
            verify_dataset_release(self.root)

    def test_self_resigned_report_changed_counts_is_rejected(self):
        p=self.root/"cleaning_report.json"
        obj=json.loads(p.read_text("utf-8"))
        obj["production_source_path_leads"]=75
        resign(self.root,p.name,json.dumps(obj).encode("utf-8"))
        with self.assertRaisesRegex(ValueError,"totals"):
            verify_dataset_release(self.root)

    def test_self_resigned_quality_stage_upgrade_is_rejected(self):
        p=self.root/"quality_report.json"
        obj=json.loads(p.read_text("utf-8"))
        obj["approved_executable_tasks"]=1
        resign(self.root,p.name,json.dumps(obj).encode("utf-8"))
        with self.assertRaisesRegex(ValueError,"counts|disagreement|task admission"):
            verify_dataset_release(self.root)

    def test_self_resigned_schema_mutation_is_rejected(self):
        p=self.root/"dataset_schema.json"
        obj=json.loads(p.read_text("utf-8"))
        obj["scientific_task_admission"]="APPROVED"
        resign(self.root,p.name,json.dumps(obj).encode("utf-8"))
        with self.assertRaisesRegex(ValueError,"dataset schema"):
            verify_dataset_release(self.root)

    def test_self_resigned_source_path_lead_mismatch_is_rejected(self):
        def corrupt(rows):
            row=next(x for x in rows
                     if x["audit_status"]=="production_source_path_detected")
            row["changed_production_file_count"]="0"
        rewrite_csv(self.root,"clean_metadata_120.csv",corrupt)
        with self.assertRaisesRegex(ValueError,"production path"):
            verify_dataset_release(self.root)

    def test_release_verifier_does_not_authenticate_upstream_sources(self):
        result=verify_dataset_release(self.root)
        self.assertFalse(result["physical_source_claims_authenticated"])
        self.assertEqual(result["independently_verified_tasks"],0)


if __name__=="__main__":
    unittest.main()
