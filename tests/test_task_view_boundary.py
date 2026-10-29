"""Adversarial, source-free task-input boundary tests."""
import hashlib
import unittest
from dataclasses import FrozenInstanceError

from ucode.task_view_boundary import parse_agent_task_view


class AgentTaskViewBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.clean = dict(repository="owner/repo", base_sha="a" * 40,
                          prefixed_spec="Fix documented pre-fix behavior.")
        self.clean["spec_sha256"] = hashlib.sha256(
            self.clean["prefixed_spec"].encode()).hexdigest()

    def test_deterministic_immutable_view(self):
        view = parse_agent_task_view(self.clean)
        self.assertEqual(view, parse_agent_task_view(dict(reversed(list(self.clean.items())))))
        self.assertIn("Base commit", view.to_policy_input())
        self.assertNotIn("pull/", view.to_policy_input())
        with self.assertRaises(FrozenInstanceError):
            view.base_sha = "b" * 40

    def test_reviewer_and_oracle_fields_fail_closed(self):
        for key in ("head_sha", "merge_commit_sha", "pr_url", "changed_test_paths",
                    "gold_patch", "hidden_tests", "oracle_correct", "reviewer_notes",
                    "reviewer", "license_approved", "status", "test_verdict"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "exactly four"):
                parse_agent_task_view(dict(self.clean, **{key: "unsafe"}))

    def test_missing_fields_fail_closed(self):
        for key in self.clean:
            x = dict(self.clean)
            del x[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_agent_task_view(x)

    def test_modified_spec_requires_matching_digest(self):
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            parse_agent_task_view(dict(self.clean, prefixed_spec="post-fix text"))

    def test_invalid_identity_and_values(self):
        for key, bad in (("base_sha", "../"), ("base_sha", True),
                         ("repository", "../repo"), ("repository", 42),
                         ("spec_sha256", "a" * 40), ("prefixed_spec", " "),
                         ("prefixed_spec", "x" * 65537)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_agent_task_view(dict(self.clean, **{key: bad}))

    def test_policy_spec_rejects_bidi_zero_width_and_terminal_controls(self):
        import unicodedata
        for injected in ("\\x00", "\\x1b[31m", "\\r", "\\u202e",
                         "\\u2066", "\\u200b", "\\u0085", "\\ud800"):
            with self.subTest(char=repr(injected)):
                text="Review this normal task: "+injected+" hidden behavior."
                rec=dict(self.clean,prefixed_spec=text)
                try:
                    rec["spec_sha256"]=hashlib.sha256(text.encode("utf-8")).hexdigest()
                except UnicodeEncodeError:
                    # Unpaired surrogates are rejected by the existing
                    # UTF-8 byte-length check before any model request.
                    with self.assertRaises((ValueError,UnicodeEncodeError)):
                        parse_agent_task_view(rec)
                    continue
                with self.assertRaisesRegex(ValueError,"unsafe control"):
                    parse_agent_task_view(rec)

    def test_human_language_and_multiline_spec_remain_permitted(self):
        statement="Maintain the existing API.\\n支持中文功能。\\tनेपाली विवरण।"
        record=dict(self.clean,prefixed_spec=statement,
                    spec_sha256=hashlib.sha256(statement.encode()).hexdigest())
        result=parse_agent_task_view(record)
        self.assertEqual(result.prefixed_spec,statement)

    def test_dossier_is_never_policy_input(self):
        with self.assertRaisesRegex(ValueError, "exactly four"):
            parse_agent_task_view(dict(self.clean, gates=[], candidate_id=104))


if __name__ == "__main__":
    unittest.main()
