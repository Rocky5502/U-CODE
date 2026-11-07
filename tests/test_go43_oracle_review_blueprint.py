"""Go 43 source-era reviewer handoff: adversarial *no-oracle* contracts.

Source metadata was collected from the public pre-PR Git tree. All
tests use fictional/source-free fixtures; tests NEVER run Go/MySQL or
generate expected functional answers or sealed oracle data.
"""
from copy import deepcopy
from hashlib import sha1
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import io
import json
import unittest

from ucode.go43_oracle_review_blueprint import (
    git_blob_sha1,inspect_go43_local_pref_fix_document,
    inspect_go43_local_business_rules,
    verify_go43_oracle_review_blueprint,
)
from ucode.pilot_preflight import build_pilot_preflight,ROOT
from scripts.compile_go43_review_handoff import compile_go43_public_handoff,main as cli

DATA=ROOT/"data/admission"


def jload(relative):
    return json.loads((DATA/relative).read_text(encoding="utf-8"))


class Go43IndependentOracleBlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=jload(
            "2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json")
        cls.source=jload(
            "2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json")
        cls.tree=jload("2026-10-27/two_candidate_pre_fix_tree_inventory.json")
        cls.chronology=jload(
            "2026-10-27/two_candidate_issue_chronology_metadata.json")
        cls.pilot=build_pilot_preflight()
        cls.business=jload(
            "2026-11-07/go43_pre_fix_business_rules_blob_METADATA_NOT_APPROVED.json")

    def verify(self,**changed):
        v={"blueprint":self.plan,"source_meta":self.source,
           "pilot":self.pilot,"pre_fix_tree_inventory":self.tree,
           "chronology":self.chronology,
           "business_rules_meta":self.business}
        v.update(changed)
        return verify_go43_oracle_review_blueprint(**v)

    def test_twelve_public_cases_six_unresolved_ambiguities_zero_admission(self):
        r=self.verify()
        self.assertEqual(r["candidate_id"],43)
        self.assertEqual(r["pre_pr_issue_to_pr_seconds"],8)
        self.assertEqual(r["public_review_case_families"],12)
        self.assertEqual(r["unresolved_normative_ambiguities"],6)
        self.assertEqual(r["higher_priority_rules_git_blob_sha40"],
                         "e71288e3127cb66f2471a5ddd2800092db0552cc")
        self.assertFalse(r["higher_priority_rules_hierarchy_reviewed"])
        self.assertEqual(r["qualified_executable_tasks"],0)
        self.assertEqual(r["independently_sealed_hidden_oracles"],0)
        self.assertEqual(r["policy_visible_gold_output_bytes"],0)
        self.assertFalse(r["go_code_executed"])
        self.assertFalse(r["policy_prompt_authorized"])

    def test_all_twelve_cases_point_only_to_pre_fix_sections(self):
        expected={"1","3.1","3.2","3.3","6.6","7"}
        self.assertEqual({s for x in self.plan["oracle_case_families"]
                          for s in x["spec_sections"]},expected)
        self.assertTrue(all(x["gold_output_included"] is False
                            for x in self.plan["oracle_case_families"]))
        self.assertTrue(all(x["stage"]=="PROPOSED_REVIEW_ONLY_NO_TEST_CODE_OR_GOLD"
                            for x in self.plan["oracle_case_families"]))

    def test_gold_patch_result_and_reviewer_pii_injection_rejected(self):
        for key in ("gold_patch","hidden_tests","reviewer_signature",
                    "post_pr_fix","approval","expected_test_output","oracle"):
            plan=deepcopy(self.plan)
            plan[key]="PRIVATE"
            with self.subTest(key=key),self.assertRaisesRegex(
                    ValueError,"schema drift"):
                self.verify(blueprint=plan)

    def test_subcase_gold_or_answer_fields_rejected(self):
        for key in ("expected_output","gold_code","code","fixture",
                    "post_fix_implementation","test_patch","secret_signature"):
            plan=deepcopy(self.plan)
            plan["oracle_case_families"][0][key]="PRIVATE"
            with self.subTest(key=key),self.assertRaisesRegex(
                    ValueError,"gold leakage"):
                self.verify(blueprint=plan)

    def test_public_blueprint_cannot_self_approve_any_gate(self):
        flags=("source_file_rights_adjudicated",
               "oracle_independently_authored","oracle_sealed_outside_repository",
               "sandbox_attested","execution_metering_attested","task_admitted",
               "go_executed","independent_source_era_scope_approved")
        for flag in flags:
            plan=deepcopy(self.plan)
            plan[flag]=True
            with self.subTest(flag=flag),self.assertRaisesRegex(
                    ValueError,"cannot self-approve"):
                self.verify(blueprint=plan)

    def test_external_business_rules_must_stay_unresolved(self):
        plan=deepcopy(self.plan)
        plan["external_business_rules_normativity_review"]="VERIFIED"
        with self.assertRaisesRegex(ValueError,"business-rule hierarchy"):
            self.verify(blueprint=plan)

    def test_scope_inflation_from_microtask_to_full_pr_rejected(self):
        plan=deepcopy(self.plan)
        plan["task_scope"]="full_pr"
        with self.assertRaisesRegex(ValueError,"immutable pre-fix microtask"):
            self.verify(blueprint=plan)
        p=deepcopy(self.pilot)
        next(x for x in p["candidates"]
             if x["candidate_id"]==43)["task_scope"]="full_pr"
        with self.assertRaisesRegex(ValueError,"task scope"):
            self.verify(pilot=p)

    def test_wrong_git_blob_sha_or_document_size_rejected(self):
        for field,value in (
            ("source_document_git_blob_sha40","f"*40),
            ("source_document_bytes",16053),
            ("base_commit","f"*40),
            ("base_tree_sha","f"*40),
            ("toolchain_go_mod_sha40","f"*40),
            ("business_rules_git_blob_sha40","f"*40),
            ("business_rules_bytes",17070),
        ):
            plan=deepcopy(self.plan)
            plan[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"immutable pre-fix"):
                self.verify(blueprint=plan)

    def test_superior_business_rules_metadata_requires_actual_git_object(self):
        for field,value in (
            ("spec_blob_sha","f"*40),
            ("spec_blob_size_bytes",17070),
            ("spec_path","docs/stray_post_pr.md"),
            ("base_tree_sha","0"*40),
            ("business_rule_versions_independently_adjudicated",True),
            ("source_file_rights_cleared",True),
            ("experiment_eligible",True),
        ):
            b=deepcopy(self.business)
            b[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"higher-priority business-rule"):
                self.verify(business_rules_meta=b)

    def test_source_metadata_forged_approval_rejected(self):
        for field in ("document_normatively_approved_as_full_pr_spec",
                      "pre_pr_issue_body_version_proven",
                      "independent_oracle_sealed",
                      "source_file_rights_cleared",
                      "experiment_eligible"):
            meta=deepcopy(self.source)
            meta[field]=True
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"metadata drift"):
                self.verify(source_meta=meta)

    def test_upstream_go_module_sha_drift_rejected(self):
        inv=deepcopy(self.tree)
        go=next(x for x in inv["records"] if x["candidate_id"]==43)
        go["toolchain_metadata"][0]["git_blob_sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"toolchain/tree evidence"):
            self.verify(pre_fix_tree_inventory=inv)

    def test_tree_source_execution_false_and_full_tree_required(self):
        for field in ("real_build_executed","tree_recursion_truncated",
                      "source_file_redistribution_approved",
                      "independent_oracle_verified"):
            inv=deepcopy(self.tree)
            go=next(x for x in inv["records"] if x["candidate_id"]==43)
            go[field]=True
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"toolchain/tree evidence"):
                self.verify(pre_fix_tree_inventory=inv)

    def test_issue_eight_seconds_chronology_and_no_immutable_issue_body(self):
        c=deepcopy(self.chronology)
        go=next(x for x in c["records"] if x["candidate_id"]==43)
        go["pr_created_at"]="2026-10-23T12:19:08Z"
        with self.assertRaisesRegex(ValueError,"eight-second"):
            self.verify(chronology=c)
        c=deepcopy(self.chronology)
        go=next(x for x in c["records"] if x["candidate_id"]==43)
        go["issue_text_at_pr_creation_immutably_archived"]=True
        with self.assertRaisesRegex(ValueError,"not archived"):
            self.verify(chronology=c)

    def test_missing_duplicate_and_fake_reviewer_case_rejected(self):
        for mutate in (
            lambda p:p["oracle_case_families"].pop(),
            lambda p:p["oracle_case_families"].__setitem__(
                1,deepcopy(p["oracle_case_families"][0])),
            lambda p:p["oracle_case_families"][0].__setitem__(
                "case_id","COPY_PR_GOLD_TEST"),
        ):
            p=deepcopy(self.plan);mutate(p)
            with self.assertRaises(ValueError):
                self.verify(blueprint=p)

    def test_oracle_case_cannot_change_section_or_status(self):
        for field,val in (
            ("spec_sections",["6.6"]),("stage","SEALED_AND_APPROVED"),
            ("gold_output_included",True),
        ):
            p=deepcopy(self.plan)
            p["oracle_case_families"][0][field]=val
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.verify(blueprint=p)

    def test_ambiguity_must_remain_unresolved_and_not_contain_answers(self):
        for field,val in (
            ("status","SOLVED_BY_COPILOT"),
            ("spec_section","100"),
            ("expected_points",25),
        ):
            p=deepcopy(self.plan)
            p["ambiguity_register"][0][field]=val
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.verify(blueprint=p)

    def test_low_balance_conflict_is_explicitly_review_required(self):
        ids={r["ambiguity_id"] for r in self.plan["ambiguity_register"]}
        self.assertIn("ZERO_FLOOR_VS_TOTAL_CONSERVATION",ids)
        self.assertIn("HALL_COEFFICIENT_FRACTIONAL_ROUNDING",ids)
        self.assertIn("EXTERNAL_BUSINESS_RULES_PRECEDENCE",ids)

    def test_git_blob_hash_uses_git_object_header_not_only_raw_sha(self):
        raw=b"public synthetic fixture\n"
        expected=sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        self.assertEqual(git_blob_sha1(raw),expected)
        self.assertNotEqual(git_blob_sha1(raw),sha1(raw).hexdigest())
        with self.assertRaises(TypeError):
            git_blob_sha1("not bytes")

    def test_wrong_or_oversized_local_document_is_rejected(self):
        for payload in (b"",b"hello",b"\x00"*16052,b"x"*1000001):
            with self.subTest(size=len(payload)),self.assertRaises(
                    ValueError):
                inspect_go43_local_pref_fix_document(payload)
            with self.subTest(size=len(payload)),self.assertRaises(
                    ValueError):
                inspect_go43_local_business_rules(payload)

    def test_read_only_report_does_not_embed_source_or_golds(self):
        report=compile_go43_public_handoff()
        self.assertEqual(len(report["case_categories_only_no_golds"]),12)
        self.assertEqual(len(report["normative_questions_still_open"]),6)
        self.assertIsNone(report["source_file_optional_external_witness"])
        self.assertIsNone(report["business_rules_optional_external_witness"])
        self.assertTrue(report["all_original_go_admission_gates_pending"])
        public=json.dumps(report)
        for token in ("gold_patch","expected_output","private_oracle",
                      "reviewer_identity","solution_patch"):
            self.assertNotIn(token,public)

    def test_cli_still_returns_blocked_even_with_source_only_review(self):
        with TemporaryDirectory() as td,redirect_stdout(io.StringIO()):
            path=Path(td,"review_status.json")
            code=cli(["--output",str(path),"--require-admitted"])
            self.assertEqual(code,2)
            assert path.is_file()
            output=json.loads(path.read_text())
            self.assertEqual(output["qualified_executable_tasks"],0)

    def test_cli_rejects_source_file_that_does_not_match_git_blob(self):
        with TemporaryDirectory() as td:
            p=Path(td,"design.md")
            p.write_text("post-PR substitute",encoding="utf-8")
            b=Path(td,"rules.md")
            b.write_text("another fake rule")
            with self.assertRaisesRegex(ValueError,"immutable pre-fix Git blob"):
                compile_go43_public_handoff(source_file=p,business_rules_file=b)

    def test_public_status_cannot_overwrite_supplied_source_file(self):
        with TemporaryDirectory() as td,redirect_stdout(io.StringIO()):
            p=Path(td,"source.txt")
            p.write_text("not original")
            b=Path(td,"rules.txt")
            b.write_text("not original either")
            with self.assertRaisesRegex(ValueError,"public status must not overwrite"):
                cli(["--source-file",str(p),
                     "--business-rules-file",str(b),"--output",str(p)])
            self.assertEqual(p.read_text(),"not original")

    def test_one_source_only_does_not_claim_verified_normative_hierarchy(self):
        with TemporaryDirectory() as td:
            p=Path(td,"design.md");p.write_text("fake")
            with self.assertRaisesRegex(ValueError,"both pre-fix"):
                compile_go43_public_handoff(source_file=p)

    def test_duplicate_source_and_business_paths_are_rejected(self):
        with TemporaryDirectory() as td:
            p=Path(td,"design.md");p.write_text("fake")
            with self.assertRaisesRegex(ValueError,"distinct local"):
                compile_go43_public_handoff(
                    source_file=p,business_rules_file=p)

    def test_review_report_is_deterministic(self):
        x=compile_go43_public_handoff()
        y=compile_go43_public_handoff()
        self.assertEqual(json.dumps(x,sort_keys=True),
                         json.dumps(y,sort_keys=True))


if __name__=="__main__":
    unittest.main()
