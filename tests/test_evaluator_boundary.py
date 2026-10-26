"""No secret-oracle metadata may flow into the hypothetical coding policy."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.check_evaluator_boundary import (
    DEFAULT_REGISTRATIONS, check_registrations,
)
from ucode.evaluator_boundary import (
    EvaluatorRegistration, evaluate_registration,
    policy_visible_registration, registration_from_json,
)


class ProspectiveOracleBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = [json.loads(s) for s in Path(
            DEFAULT_REGISTRATIONS).read_text(encoding="utf-8").splitlines() if s]
        cls.objects = [registration_from_json(x) for x in cls.raw]

    def test_real_two_case_registration_has_zero_admission(self):
        results = check_registrations()
        self.assertEqual({r["candidate_id"] for r in results}, {43, 104})
        self.assertTrue(all(r["independently_admitted"] is False for r in results))
        self.assertTrue(all(r["oracle_evaluations"] == 0 for r in results))

    def test_oracle_visibility_is_structural_allowlist(self):
        x = self.objects[0]
        forbidden = (
            "evaluator_only_oracle_refs", "oracle_commitment_sha256",
            "oracle_author_role", "oracle_review_group",
            "environment_image_digest", "runner_attestation_ref",
            "model_train_lineage", "model_eval_lineage",
            "pr_authored_test_paths",
        )
        view = policy_visible_registration(x)
        for name in forbidden:
            self.assertNotIn(name, view)
        self.assertIn("task_base_sha", view)
        self.assertIn("policy_visible_spec_refs", view)

    def test_new_gold_oracle_ref_does_not_change_policy_view(self):
        x = self.objects[0]
        sealed_looking = replace(
            x, evaluator_only_oracle_refs=("evaluator-private://secret-tests-v4",),
            oracle_commitment_sha256="a"*64,
            oracle_author_role="independent_evaluator",
            oracle_review_group="sealed-group",
        )
        self.assertEqual(policy_visible_registration(x),
                         policy_visible_registration(sealed_looking))
        self.assertFalse(evaluate_registration(sealed_looking)["independently_admitted"])

    def test_policy_view_cannot_contain_exact_private_oracle_reference(self):
        x = self.objects[0]
        with self.assertRaisesRegex(ValueError, "oracle reference directly leaked"):
            replace(x, evaluator_only_oracle_refs=(
                x.policy_visible_spec_refs[0],))

    def test_pr_written_test_path_is_not_evaluator_only(self):
        x = self.objects[0]
        with self.assertRaisesRegex(ValueError, "PR-authored tests cannot"):
            replace(x, evaluator_only_oracle_refs=(x.pr_authored_test_paths[0],))

    def test_forged_seal_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot self-declare"):
            replace(self.objects[0], status="SEALED_APPROVED")

    def test_train_eval_lineage_overlap_blocked(self):
        with self.assertRaisesRegex(ValueError, "lineage must differ"):
            replace(self.objects[0], model_train_lineage="shared-repo-fork",
                    model_eval_lineage="shared-repo-fork")

    def test_model_author_cannot_self_attest_oracle(self):
        with self.assertRaisesRegex(ValueError, "implementer"):
            replace(self.objects[0], oracle_author_role="candidate_author")
        with self.assertRaisesRegex(ValueError, "implementer"):
            replace(self.objects[0], oracle_author_role="implementer")

    def test_malformed_digest_and_unpinned_execution_image_rejected(self):
        with self.assertRaisesRegex(ValueError, "commitment"):
            replace(self.objects[0], oracle_commitment_sha256="broken")
        with self.assertRaisesRegex(ValueError, "content-addressed"):
            replace(self.objects[0], environment_image_digest="ubuntu:latest")
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            replace(self.objects[0], environment_image_digest="sha256:short")

    def test_unknown_json_field_is_blocked_not_sent_to_agent(self):
        record = dict(self.raw[0], gold_patch="visible-to-model")
        with self.assertRaisesRegex(ValueError, "unknown registration fields"):
            registration_from_json(record)

    def test_microtask_scope_is_disclosed_without_full_pr_claim(self):
        x = next(x for x in self.objects if x.candidate_id == 43)
        self.assertEqual(x.task_scope, "declared_microtask")
        self.assertIn("microtask_not_full_pr_correctness",
                      evaluate_registration(x)["missing_or_unverified"])

    def test_both_cases_unsealed_even_when_pre_fix_spec_sha_exists(self):
        for x in self.objects:
            result = evaluate_registration(x)
            self.assertIn("no_separate_evaluator_oracle",
                          result["missing_or_unverified"])
            self.assertIn("isolated_runner_not_attested",
                          result["missing_or_unverified"])
        go = next(x for x in self.objects if x.candidate_id == 43)
        self.assertEqual(len(go.pre_fix_spec_blob_sha), 40)
        self.assertIsNone(next(x for x in self.objects
                               if x.candidate_id == 104).pre_fix_spec_blob_sha)

    def test_registration_list_must_match_every_dossier(self):
        with TemporaryDirectory() as td:
            p = Path(td)/"partial.jsonl"
            p.write_text(json.dumps(self.raw[0])+"\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "each prospective dossier"):
                check_registrations(registrations_path=p)

    def test_modified_base_revision_cannot_pass_canonical_binding(self):
        with TemporaryDirectory() as td:
            p = Path(td)/"drift.jsonl"
            changed = dict(self.raw[0], task_base_sha="a"*40)
            p.write_text("\n".join([json.dumps(changed),
                                     json.dumps(self.raw[1])])+"\n",
                         encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "original PR dossier"):
                check_registrations(registrations_path=p)

    def test_pr_authored_test_omission_cannot_pass_manifest(self):
        with TemporaryDirectory() as td:
            p = Path(td)/"test-omission.jsonl"
            changed = dict(self.raw[0], pr_authored_test_paths=[])
            p.write_text("\n".join([json.dumps(changed),
                                     json.dumps(self.raw[1])])+"\n",
                         encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "original PR dossier"):
                check_registrations(registrations_path=p)

    def test_declared_oracle_ref_with_all_metadata_still_needs_attestation(self):
        x = self.objects[1]
        altered = replace(
            x,
            evaluator_only_oracle_refs=("private://test-suite",),
            oracle_commitment_sha256="b"*64,
            oracle_author_role="independent_reviewer",
            oracle_review_group="separate-team",
            model_train_lineage="repo-A",
            model_eval_lineage="repo-B",
            environment_image_digest="sha256:"+"c"*64,
            runner_attestation_ref="sha256:operator-pending",
        )
        result = evaluate_registration(altered)
        self.assertEqual(result["readiness"],
                         "BLOCKED_INDEPENDENT_ATTESTATION_REQUIRED")
        self.assertFalse(result["independently_admitted"])


    def test_visible_spec_rejects_network_and_query_gold_smuggling(self):
        x = self.objects[0]
        refs = (
            "https://attacker.example/evaluator-secret",
            x.issue_ref + "?oracle=private-secret",
            x.issue_ref + "#hidden-test",
            x.issue_ref.replace("https://", "http://"),
            x.issue_ref.replace("github.com", "github.com.evil.example"),
        )
        for ref in refs:
            with self.subTest(ref=ref), self.assertRaisesRegex(
                    ValueError, "unsafe policy-visible"):
                replace(x, policy_visible_spec_refs=(ref,))

    def test_visible_spec_cannot_point_to_other_issue_or_post_fix_blob(self):
        x = self.objects[1]
        repo = x.repository
        later = "a" * 40
        with self.assertRaisesRegex(ValueError, "not task issue"):
            replace(x, policy_visible_spec_refs=(
                "https://github.com/" + repo + "/issues/999",))
        with self.assertRaisesRegex(ValueError, "pre-fix base"):
            replace(x, policy_visible_spec_refs=(
                "https://github.com/" + repo + "/blob/" + later + "/docs/design.md",))

    def test_visible_spec_ref_traversal_and_encoded_path_blocked(self):
        x = self.objects[1]
        p = "https://github.com/" + x.repository + "/blob/" + x.task_base_sha
        for ref in (p + "/docs/../oracle.py",
                    p + "/docs//oracle.py",
                    p + "/docs/%2e%2e/oracle.py"):
            with self.subTest(ref=ref), self.assertRaisesRegex(
                    ValueError, "pre-fix base|unsafe"):
                replace(x, policy_visible_spec_refs=(ref,))

    def test_pinned_public_spec_still_valid_and_not_oracle(self):
        x = self.objects[1]
        view = policy_visible_registration(x)
        self.assertEqual(view["policy_visible_spec_refs"],
                         list(x.policy_visible_spec_refs))
        self.assertNotIn("evaluator_only_oracle_refs", view)
        self.assertFalse(evaluate_registration(x)["independently_admitted"])


if __name__ == "__main__":
    unittest.main()
