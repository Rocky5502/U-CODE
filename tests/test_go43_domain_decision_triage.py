"""Synthetic private Go rule-review triage tests: NO real human or oracle data."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.export_go43_spec_feasibility import compile_go43_spec_feasibility
from scripts.triage_go43_domain_decisions import (
    _read_private, go43_domain_review_check, main,
)
from ucode.go43_domain_decision_triage import (
    blank_go43_domain_decisions, triage_private_go43_domain_decisions,
)


class Go43IndependentDomainReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = compile_go43_spec_feasibility()

    def forms(self):
        forms = blank_go43_domain_decisions(self.packet)
        return deepcopy(list(forms["A"])), deepcopy(list(forms["B"]))

    @staticmethod
    def mark(row, slot, verdict="RULE_MEMO_PRESENT_NOT_ATTESTED",
             memo=None, ref="SYNTHETIC_PRIVATE_SOURCE_DO_NOT_PUBLISH"):
        row["reviewer_identity"] = "SYNTHETIC_REVIEWER_" + slot
        row["verdict"] = verdict
        row["reviewer_note"] = "SYNTHETIC_CONFIDENTIAL_RULE_INTERPRETATION"
        if verdict == "RULE_MEMO_PRESENT_NOT_ATTESTED":
            row["decision_memo_sha256"] = memo or sha256(
                b"FICTIONAL_RULE_MEMO_FROM_INDEPENDENT_HUMAN_REQUIRED").hexdigest()
            row["normative_source_refs"] = [ref]

    @staticmethod
    def dump(tmp, a, b):
        paths = []
        for slot, rows in (("A", a), ("B", b)):
            p = Path(tmp) / (slot + "_PRIVATE.jsonl")
            p.write_text("".join(
                json.dumps(x, sort_keys=True) + "\n" for x in rows), encoding="utf-8")
            paths.append(p)
        return paths

    def triage(self, a=None, b=None):
        if a is None or b is None:
            a, b = self.forms()
        return triage_private_go43_domain_decisions(self.packet, a, b)

    def test_blank_reviewer_inventory_contains_six_questions_per_slot(self):
        a, b = self.forms()
        self.assertEqual(len(a), 6)
        self.assertEqual(len(b), 6)
        self.assertEqual({x["ambiguity_id"] for x in a},
                         {x["ambiguity_id"] for x in b})
        self.assertTrue(all(x["verdict"] == "PENDING"
                            and x["independent_approval"] is False for x in a+b))

    def test_no_reviews_report_six_pending_and_zero_authority(self):
        s = self.triage()
        self.assertEqual(s["total_domain_questions"], 6)
        self.assertEqual(s["counts_by_status"],
                         {"PENDING_INDEPENDENT_DOMAIN_REVIEW": 6})
        self.assertFalse(s["task_admitted"])
        self.assertFalse(s["human_adjudication_completed"])
        self.assertFalse(s["specification_normatively_approved"])
        self.assertFalse(s["hidden_oracle_sealed"])
        self.assertEqual(s["remaining_php_go_admission_gates"], 16)

    def test_six_matching_memo_claims_still_grant_no_admission(self):
        a, b = self.forms()
        for x in a: self.mark(x, "A")
        for x in b: self.mark(x, "B")
        s = self.triage(a,b)
        self.assertEqual(s["counts_by_status"],
             {"MATCHING_UNVERIFIED_RULE_MEMO_CLAIMS_NOT_ADJUDICATED": 6})
        self.assertFalse(s["independent_human_identity_authenticated"])
        self.assertFalse(s["rule_memoranda_contents_authenticated"])
        self.assertFalse(s["task_admitted"])

    def test_divergent_memo_digest_not_a_matching_rule(self):
        a, b = self.forms()
        self.mark(a[0],"A")
        self.mark(b[0],"B",memo="a"*64)
        s = self.triage(a,b)
        self.assertEqual(s["statuses_public_ids_only"][0]["triage_status"],
             "DIVERGENT_MEMO_DIGEST_NEEDS_INDEPENDENT_ADJUDICATION")

    def test_same_memo_with_different_source_refs_needs_adjudication(self):
        a, b = self.forms()
        self.mark(a[0],"A")
        self.mark(b[0],"B",ref="SYNTHETIC_OTHER_REFERENT_NOT_PUBLIC")
        s = self.triage(a,b)
        self.assertEqual(s["statuses_public_ids_only"][0]["triage_status"],
             "DIVERGENT_SOURCE_REFS_NEEDS_INDEPENDENT_ADJUDICATION")

    def test_divergent_verdict_requires_adjudicator(self):
        a, b = self.forms()
        self.mark(a[0],"A")
        self.mark(b[0],"B","REJECT_PROPOSED_TASK_SCOPE")
        s = self.triage(a,b)
        self.assertEqual(s["statuses_public_ids_only"][0]["triage_status"],
             "DIVERGENT_VERDICT_NEEDS_INDEPENDENT_ADJUDICATION")

    def test_joint_rejection_does_not_admit_task(self):
        a,b=self.forms()
        self.mark(a[0],"A","REJECT_PROPOSED_TASK_SCOPE")
        self.mark(b[0],"B","REJECT_PROPOSED_TASK_SCOPE")
        self.assertEqual(self.triage(a,b)["statuses_public_ids_only"][0]["triage_status"],
             "BOTH_REJECT_SCOPE_NO_TASK_ADMISSION")

    def test_joint_insufficient_source_does_not_admit_task(self):
        a,b=self.forms()
        self.mark(a[0],"A","INSUFFICIENT_SOURCE_ERA_EVIDENCE")
        self.mark(b[0],"B","INSUFFICIENT_SOURCE_ERA_EVIDENCE")
        self.assertEqual(self.triage(a,b)["statuses_public_ids_only"][0]["triage_status"],
             "BOTH_INSUFFICIENT_SOURCE_EVIDENCE_NO_TASK_ADMISSION")

    def test_one_pending_review_reports_pending(self):
        a,b=self.forms()
        self.mark(a[0],"A")
        self.assertEqual(self.triage(a,b)["statuses_public_ids_only"][0]["triage_status"],
             "PENDING_INDEPENDENT_DOMAIN_REVIEW")

    def test_duplicate_or_missing_questions_rejected(self):
        a,b=self.forms()
        with self.assertRaisesRegex(ValueError,"exact six"):
            self.triage(a[:-1], b)
        a[1] = deepcopy(a[0])
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.triage(a, b)

    def test_same_reviewer_identity_for_both_slots_refused(self):
        a,b=self.forms()
        self.mark(a[0],"A")
        self.mark(b[0],"A")
        with self.assertRaisesRegex(ValueError,"same identity"):
            self.triage(a,b)

    def test_multiple_identities_inside_one_slot_refused(self):
        a,b=self.forms()
        self.mark(a[0],"A")
        self.mark(a[1],"OTHER")
        with self.assertRaisesRegex(ValueError,"mix identities"):
            self.triage(a,b)

    def test_forged_independent_approval_rejected(self):
        a,b=self.forms()
        a[0]["independent_approval"]=True
        with self.assertRaisesRegex(ValueError,"original source pins"):
            self.triage(a,b)

    def test_forged_oracle_field_rejected(self):
        a,b=self.forms()
        a[0]["hidden_oracle_passed"]=True
        with self.assertRaisesRegex(ValueError,"schema drift"):
            self.triage(a,b)

    def test_changed_original_source_blob_rejected(self):
        a,b=self.forms()
        a[0]["business_rules_git_blob_sha40"]="b"*40
        with self.assertRaisesRegex(ValueError,"source pins"):
            self.triage(a,b)

    def test_pending_row_with_hidden_content_rejected(self):
        a,b=self.forms()
        a[0]["reviewer_note"]="PRIVATE_GOLD_LEAK"
        with self.assertRaisesRegex(ValueError,"pending review"):
            self.triage(a,b)

    def test_positive_rule_memo_requires_source_refs_and_digest(self):
        a,b=self.forms()
        self.mark(a[0],"A")
        a[0]["normative_source_refs"]=[]
        with self.assertRaisesRegex(ValueError,"refs"):
            self.triage(a,b)
        self.mark(a[0],"A")
        a[0]["decision_memo_sha256"]="bad"
        with self.assertRaisesRegex(ValueError,"valid digest"):
            self.triage(a,b)

    def test_insufficient_review_must_not_claim_positive_rule_memo(self):
        a,b=self.forms()
        self.mark(a[0],"A","INSUFFICIENT_SOURCE_ERA_EVIDENCE")
        a[0]["decision_memo_sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"must not masquerade"):
            self.triage(a,b)

    def test_cli_public_prospective_status_and_strict_block(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main([]),0)
            self.assertEqual(main(["--require-adjudicated"]),2)
        s=output.getvalue()
        self.assertIn("PENDING_INDEPENDENT_DOMAIN_REVIEW",s)
        self.assertNotIn("SYNTHETIC_REVIEWER",s)

    def test_private_template_creation_is_nonadmission_and_0600(self):
        with TemporaryDirectory() as tmp:
            folder=Path(tmp)/"independent_A_B_blank"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--export-blank-dir",str(folder)]),0)
            self.assertTrue(folder.is_dir())
            for slot in ("A","B"):
                p=folder/(slot+"_go43_PENDING.jsonl")
                self.assertEqual(len(p.read_text().splitlines()),6)
                self.assertEqual(p.stat().st_mode & 0o777,0o600)
            with self.assertRaisesRegex(ValueError,"non-existing"):
                go43_domain_review_check(template_dir=folder)

    def test_private_inputs_processed_locally_but_redacted(self):
        a,b=self.forms()
        self.mark(a[0],"A",memo="a"*64)
        self.mark(b[0],"B",memo="f"*64)
        with TemporaryDirectory() as tmp:
            pa,pb=self.dump(tmp,a,b)
            out=Path(tmp)/"redacted.json"
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                self.assertEqual(main(["--reviewer-a",str(pa),"--reviewer-b",str(pb),
                                       "--output",str(out)]),0)
            report=out.read_text()
            self.assertEqual(json.loads(captured.getvalue()),json.loads(report))
            for secret in ("SYNTHETIC_REVIEWER","SYNTHETIC_CONFIDENTIAL",
                           "SYNTHETIC_PRIVATE","a"*64,"f"*64):
                self.assertNotIn(secret,report)
            self.assertFalse(json.loads(report)["task_admitted"])
            self.assertEqual(out.stat().st_mode & 0o777,0o600)

    def test_private_symlink_and_same_file_refused(self):
        a,b=self.forms()
        with TemporaryDirectory() as tmp:
            pa,pb=self.dump(tmp,a,b)
            with self.assertRaisesRegex(ValueError,"separate reviewer"):
                go43_domain_review_check(pa,pa)
            alias=Path(tmp)/"alias.jsonl"
            alias.symlink_to(pa)
            with self.assertRaisesRegex(ValueError,"non-symlink"):
                go43_domain_review_check(alias,pb)

    def test_output_wont_overwrite_private_inputs_or_existing_summary(self):
        a,b=self.forms()
        with TemporaryDirectory() as tmp:
            pa,pb=self.dump(tmp,a,b)
            with self.assertRaisesRegex(ValueError,"cannot overwrite"):
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["--reviewer-a",str(pa),"--reviewer-b",str(pb),
                          "--output",str(pa)])
            out=Path(tmp)/"already_present"
            out.write_text("keep original")
            with self.assertRaises(FileExistsError):
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["--reviewer-a",str(pa),"--reviewer-b",str(pb),
                          "--output",str(out)])
            self.assertEqual(out.read_text(),"keep original")

    def test_duplicate_json_keys_and_nan_rejected(self):
        a,b=self.forms()
        with TemporaryDirectory() as tmp:
            pa,pb=self.dump(tmp,a,b)
            lines=pa.read_text().splitlines()
            lines[0]=lines[0][:-1]+',"verdict":"PENDING"}'
            pa.write_text("\n".join(lines)+"\n")
            with self.assertRaisesRegex(ValueError,"duplicate private"):
                _read_private(pa)
            lines[0]=json.dumps(a[0])[:-1]+',"sneaky":NaN}'
            pa.write_text("\n".join(lines)+"\n")
            with self.assertRaisesRegex(ValueError,"NaN/Infinity"):
                _read_private(pa)

    def test_oversized_private_input_fails_bounded(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"large.jsonl"
            p.write_bytes(b"x"*(128*1024+1))
            with self.assertRaisesRegex(ValueError,"too large"):
                _read_private(p)

    def test_canonical_source_packet_cannot_self_approve(self):
        bad=deepcopy(self.packet)
        bad["oracle_sealed"]=True
        with self.assertRaisesRegex(ValueError,"cannot be promoted"):
            blank_go43_domain_decisions(bad)
        bad=deepcopy(self.packet)
        bad["pinned_original_documents"][1]["git_blob_sha40"]="b"*40
        with self.assertRaisesRegex(ValueError,"two original documents"):
            blank_go43_domain_decisions(bad)


if __name__=="__main__":
    unittest.main()
