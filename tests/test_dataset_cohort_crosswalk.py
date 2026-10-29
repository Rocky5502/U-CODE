"""Cross-asset source-only dataset quality and leakage regression tests."""
from copy import deepcopy
import json
import unittest
from scripts.audit_dataset_cohort_crosswalk import (
    RAW, CLEAN, SOURCES, LEGACY, SUMMARY, read_csv, inspect_cohorts,
)

class DatasetCohortCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=read_csv(RAW)
        cls.clean=read_csv(CLEAN)
        cls.external=read_csv(SOURCES)
        cls.legacy=read_csv(LEGACY)
        cls.summary=json.loads(SUMMARY.read_text(encoding="utf-8"))

    def check(self, raw=None, clean=None, external=None, legacy=None, summary=None):
        return inspect_cohorts(
            self.raw if raw is None else raw,
            self.clean if clean is None else clean,
            self.external if external is None else external,
            self.legacy if legacy is None else legacy,
            self.summary if summary is None else summary,
        )

    def test_all_frozen_pr_and_external_catalog_rows_reconcile(self):
        x=self.check()
        self.assertEqual(x["source_discovery_rows"],120)
        self.assertEqual(len(x["search_language_strata"]),12)
        self.assertEqual(sum(x["search_language_strata"].values()),120)
        self.assertEqual(x["external_source_catalog_leads"],13)
        self.assertEqual(x["legacy_catalog_leads"],10)
        self.assertEqual(x["independent_executable_tasks"],0)
        self.assertEqual(x["retrieved_pr_metadata"],119)
        self.assertEqual(x["production_source_path_leads"],62)

    def test_no_identity_replacement_between_clean_and_original(self):
        clean=deepcopy(self.clean)
        clean[0]["pr_url"]="https://github.com/other/repo/pull/3"
        with self.assertRaisesRegex(ValueError,"identity"):
            self.check(clean=clean)

    def test_duplicate_or_missing_row_fails(self):
        raw=deepcopy(self.raw)
        raw[1]["id"]=raw[0]["id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.check(raw=raw)
        with self.assertRaisesRegex(ValueError,"120"):
            self.check(clean=self.clean[:-1])

    def test_cannot_promote_curated_row_to_task_or_split(self):
        for key,val in (("source_qualification","READY"),
                        ("task_admission","ADMITTED"),
                        ("independent_oracle","YES"),
                        ("split_status","TRAIN")):
            clean=deepcopy(self.clean)
            clean[0][key]=val
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"cannot claim"):
                self.check(clean=clean)

    def test_external_dataset_does_not_become_downloaded_by_edit(self):
        catalog=deepcopy(self.external)
        catalog[0]["local_execution"]="verified"
        with self.assertRaisesRegex(ValueError,"falsely qualified"):
            self.check(external=catalog)

    def test_reject_duplicate_and_non_https_source(self):
        catalog=deepcopy(self.external)
        catalog[1]["dataset"]=catalog[0]["dataset"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.check(external=catalog)
        catalog=deepcopy(self.external)
        catalog[0]["primary_url"]="http://untrusted.invalid"
        with self.assertRaisesRegex(ValueError,"non-HTTPS"):
            self.check(external=catalog)

    def test_preserve_source_search_language_even_if_modified_code_mismatched(self):
        clean=deepcopy(self.clean)
        clean[0]["search_language"]="Swift"
        with self.assertRaisesRegex(ValueError,"identity"):
            self.check(clean=clean)

    def test_upstream_rights_cannot_self_certify(self):
        raw=deepcopy(self.raw)
        raw[0]["license_status"]="CLEARED"
        with self.assertRaisesRegex(ValueError,"self-certify"):
            self.check(raw=raw)

    def test_summary_metadata_not_mistaken_for_oracle(self):
        summary=deepcopy(self.summary)
        summary["independently_approved_executable_tasks"]=2
        with self.assertRaisesRegex(ValueError,"inconsistent"):
            self.check(summary=summary)

if __name__=="__main__":
    unittest.main()
