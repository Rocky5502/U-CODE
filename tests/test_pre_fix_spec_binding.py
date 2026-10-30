"""Go #43 pinned pre-fix Git document and PHP issue-boundary adversarial tests.

No external repository, network call, LLM, hidden oracle or third-party
source execution occurs in these authored source-metadata-only tests.
"""
from dataclasses import replace
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.check_evaluator_boundary import (
    DEFAULT_GO43_DOCUMENT_SNAPSHOT,
    DEFAULT_PRE_FIX_TREES,
    DEFAULT_REGISTRATIONS,
    check_registrations,
)
from ucode.evaluator_boundary import registration_from_json
from ucode.pre_fix_spec_binding import (
    verify_go43_document_tree_binding,
    verify_php104_mutable_issue_quarantine,
)


class PinnedSpecSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(Path(
            DEFAULT_GO43_DOCUMENT_SNAPSHOT).read_text("utf-8"))
        cls.trees = json.loads(Path(
            DEFAULT_PRE_FIX_TREES).read_text("utf-8"))
        raw = [json.loads(s) for s in Path(DEFAULT_REGISTRATIONS)
               .read_text("utf-8").splitlines() if s]
        cls.raw = raw
        objs = [registration_from_json(x) for x in raw]
        cls.go = next(x for x in objs if x.candidate_id == 43)
        cls.php = next(x for x in objs if x.candidate_id == 104)

    def audit(self, source=None, registration=None, trees=None):
        return verify_go43_document_tree_binding(
            self.snapshot if source is None else source,
            self.go if registration is None else registration,
            self.trees if trees is None else trees,
        )

    def test_go_source_era_document_is_immutable_identity_not_task_admission(self):
        out = self.audit()
        self.assertTrue(out["metadata_tree_entry_consistent"])
        self.assertEqual(out["pre_fix_document_path"], "docs/design.md")
        self.assertEqual(out["pre_fix_document_blob_sha"],
                         "b566ca7627b6518670a866a6a637bd5257e947f4")
        self.assertFalse(out["full_pr_behavioral_specification_approved"])
        self.assertFalse(out["eligible_for_real_experiment"])

    def test_historical_php_issue_is_mutable_and_unqualified(self):
        out = verify_php104_mutable_issue_quarantine(self.php)
        self.assertFalse(out["policy_input_authorized"])
        self.assertFalse(out["original_issue_body_at_pre_pr_cutoff_verified"])
        self.assertFalse(out["eligible_for_real_experiment"])

    def test_wrong_document_sha_or_wrong_base_path_cannot_pass(self):
        for changed in (
            replace(self.go, pre_fix_spec_blob_sha="f"*40),
            replace(self.go, policy_visible_spec_refs=(
                "https://github.com/"+self.go.repository+"/blob/"
                +self.go.task_base_sha+"/docs/other.md",)),
            replace(self.go, policy_visible_spec_refs=(
                "https://github.com/"+self.go.repository+"/issues/29",)),
            replace(self.go, policy_visible_spec_refs=()),
        ):
            with self.subTest(view=changed.policy_visible_spec_refs), self.assertRaisesRegex(
                ValueError,"unbound"):
                self.audit(registration=changed)

    def test_attacker_cannot_self_promote_historical_php_issue(self):
        with self.assertRaisesRegex(ValueError,"cannot be a pinned spec"):
            verify_php104_mutable_issue_quarantine(replace(
                self.php, pre_fix_spec_blob_sha="a"*40))
        with self.assertRaisesRegex(ValueError,"cannot be a pinned spec"):
            verify_php104_mutable_issue_quarantine(replace(
                self.php, policy_visible_spec_refs=(
                    "https://github.com/"+self.php.repository+"/blob/"
                    +self.php.task_base_sha+"/README.md",)))

    def test_blob_shape_size_and_immutability_are_exact(self):
        alterations = {
            "spec_blob_sha":"f"*40,
            "spec_blob_size_bytes":16053,
            "spec_blob_mode":"100755",
            "spec_blob_type":"tree",
            "spec_path":"docs/new-design.md",
            "base_tree_sha":"f"*40,
            "task_base_sha":"f"*40,
            "source_api":"GitHub REST /current/main",
            "repository":"other/repository",
        }
        for field,bad in alterations.items():
            row = deepcopy(self.snapshot)
            row[field] = bad
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError, "pinned source"):
                self.audit(source=row)

    def test_extra_or_missing_keys_are_not_evidence(self):
        row = dict(self.snapshot, gold_test="leak")
        with self.assertRaisesRegex(ValueError,"schema drift"):
            self.audit(source=row)
        row = dict(self.snapshot)
        del row["spec_blob_sha"]
        with self.assertRaisesRegex(ValueError,"schema drift"):
            self.audit(source=row)

    def test_source_meta_cannot_self_attest_rights_or_oracle(self):
        for field in (
            "source_tree_truncated", "source_content_executed",
            "pre_pr_issue_body_version_proven",
            "document_normatively_approved_as_full_pr_spec",
            "independent_oracle_sealed", "source_file_rights_cleared",
            "experiment_eligible",
        ):
            row = deepcopy(self.snapshot)
            row[field] = True
            with self.subTest(field=field),self.assertRaisesRegex(
                ValueError,"cannot approve"):
                self.audit(source=row)

    def test_source_tree_identity_must_match_original_dossier(self):
        for key in ("base_commit", "base_tree_sha", "repository"):
            trees = deepcopy(self.trees)
            entry = next(r for r in trees["records"] if r["candidate_id"]==43)
            entry[key] = "f"*40 if "sha" in key or key=="base_commit" else "other/repo"
            with self.subTest(key=key),self.assertRaisesRegex(
                ValueError,"contradicts"):
                self.audit(trees=trees)

    def test_duplicate_original_tree_identity_rejected(self):
        trees=deepcopy(self.trees)
        trees["records"][1]["candidate_id"]=43
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.audit(trees=trees)

    def test_bad_timestamp_and_retroactively_fake_observation_are_rejected(self):
        for t in ("2026-10-29","2026-02-30","2026-10-30T01:00:00Z",True):
            row=deepcopy(self.snapshot)
            row["observed_on"]=t
            with self.subTest(t=t),self.assertRaises(ValueError):
                self.audit(source=row)

    def test_evaluator_audit_binds_both_real_candidate_records(self):
        report=check_registrations()
        self.assertEqual({r["candidate_id"] for r in report},{43,104})
        source={r["candidate_id"]:r["source_spec_binding"] for r in report}
        self.assertEqual(
            source[43],"IMMUTABLE_BASE_DOCUMENT_IDENTITY_MATCHED_NOT_APPROVED_SPEC")
        self.assertEqual(
            source[104],"MUTABLE_HISTORICAL_ISSUE_BODY_QUARANTINED")
        self.assertTrue(all(x["independently_admitted"] is False for x in report))

    def test_mutated_go_registration_fails_integrated_audit(self):
        raws=deepcopy(self.raw)
        for row in raws:
            if row["candidate_id"]==43:
                row["pre_fix_spec_blob_sha"]="e"*40
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"mutated.jsonl"
            p.write_text("\n".join(json.dumps(x) for x in raws)+"\n","utf-8")
            with self.assertRaisesRegex(ValueError,"unbound"):
                check_registrations(registrations_path=p)

    def test_mutated_snapshot_fails_integrated_audit(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"mutated.json"
            row=dict(self.snapshot,spec_blob_size_bytes=16051)
            p.write_text(json.dumps(row),"utf-8")
            with self.assertRaisesRegex(ValueError,"pinned source"):
                check_registrations(spec_snapshot_path=p)


if __name__=="__main__":
    unittest.main()
