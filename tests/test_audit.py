import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
import json

from ucode.audit import (audit_pr_metadata, inspect_candidate, is_source_path,
                         is_test_path, source_language, read_candidates,
                         select_candidates, audit_manifest)


class AuditTests(unittest.TestCase):
    def test_source_classifier(self):
        for path in ("src/a.py", "app/view.tsx", "pkg/a.rs", "src/c.c",
                     "kernel/a.cpp", "src/lib.cs", "app/Main.kt", "lib/f.php"):
            self.assertTrue(is_source_path(path), path)
        for path in ("README.md", "package-lock.json", "vendor/a.py",
                     "node_modules/index.ts", "dist/a.js", "out/image.png",
                     "js/app.min.js", "target/release/a.rs"):
            self.assertFalse(is_source_path(path), path)

    def test_metadata_not_correctness(self):
        pr = {"user": {"login": "copilot-swe-agent[bot]"},
              "merged_at": "2026-10-01T00:00:00Z",
              "base": {"sha": "one"}, "head": {"sha": "two"}}
        changed = [{"filename": "src/x.py", "additions": 15, "deletions": 3},
                   {"filename": "README.md", "additions": 200, "deletions": 0}]
        result = audit_pr_metadata(pr, changed, "MIT")
        self.assertEqual(result["status"], "production_source_path_detected")
        self.assertEqual(result["source_additions"], 15)
        self.assertFalse(result["functional_correctness_known"])
        self.assertFalse(result["test_verification_done"])

    def test_copilot_api_login_alias(self):
        pr = {"user": {"login": "Copilot"}, "merged_at": "2026-10-01"}
        files = [{"filename": "app/a.mjs", "additions": 10, "deletions": 1}]
        result = audit_pr_metadata(pr, files, "MIT")
        self.assertTrue(result["agent_account_matches_search"])
        self.assertEqual(result["code_file_count"], 1)

    def test_reject_docs_only(self):
        pr = {"user": {"login": "copilot-swe-agent[bot]"},
              "merged_at": "2026-10-01T00:00:00Z"}
        result = audit_pr_metadata(pr, [{"filename": "README.md"}], None)
        self.assertEqual(result["status"], "non_source_change")

    def test_reject_non_bot_or_unmerged(self):
        changed = [{"filename": "src/mod.py", "additions": 1, "deletions": 0}]
        p = {"user": {"login": "person"}, "merged_at": "2026-10-01"}
        self.assertEqual(audit_pr_metadata(p, changed, "MIT")["status"],
                         "agent_or_merge_mismatch")
        p["user"]["login"] = "copilot-swe-agent[bot]"
        p["merged_at"] = None
        self.assertEqual(audit_pr_metadata(p, changed, "MIT")["status"],
                         "agent_or_merge_mismatch")

    @patch("ucode.audit.github_json")
    def test_no_source_checkout_in_auditor(self, api):
        pr = {"user": {"login": "copilot-swe-agent[bot]"}, "merged_at": "2026-10-01",
              "base": {"sha": "abc"}, "head": {"sha": "def"}}
        files = [{"filename": "test/a.py", "additions": 4, "deletions": 1}]
        repo = {"default_branch": "main", "archived": False,
                "license": {"spdx_id": "Apache-2.0"}}
        api.side_effect = [pr, files, repo]
        result = inspect_candidate({"repository": "org/repo",
                                    "agent_pr_url": "https://github.com/org/repo/pull/3",
                                    "query_language": "Python"})
        self.assertEqual(result["source_additions"], 4)
        self.assertEqual(result["base_sha"], "abc")
        self.assertFalse(result["manual_patch_review_done"])

    def test_test_only_changes_not_production(self):
        pr = {"user": {"login": "Copilot"}, "merged_at": "2026-10-01"}
        files = [{"filename": "tests/test_dependency_security.py",
                  "additions": 9, "deletions": 1},
                 {"filename": "test/search.test.mjs", "additions": 1, "deletions": 0}]
        r = audit_pr_metadata(pr, files, "MIT")
        self.assertEqual(r["status"], "test_only_source_change")
        self.assertEqual(r["production_file_count"], 0)
        self.assertEqual(r["test_file_count"], 2)
        self.assertTrue(r["license_review_required"])

    def test_changed_language_not_repository_primary(self):
        pr = {"user": {"login": "Copilot"}, "merged_at": "2026-10-01"}
        paths = [{"filename": "ios/NIKNOLIG/App/HomeView.swift", "additions": 4},
                 {"filename": "ios/NIKNOLIGCore/Tests/CoreTests.swift", "additions": 3}]
        r = audit_pr_metadata(pr, paths, None)
        self.assertEqual(r["changed_production_languages"], ["Swift"])
        self.assertEqual(r["production_file_count"], 1)
        self.assertTrue(is_test_path("Core/MCPhappey.Tests/OpenXmlWordTests.cs"))
        self.assertEqual(source_language("src/lib/matcher.ts"), "TypeScript")

    def test_fork_and_license_are_not_clearance(self):
        pr = {"user": {"login": "Copilot"}, "merged_at": "2026-10-01"}
        r = audit_pr_metadata(pr, [{"filename": "main.c", "additions": 3}], "Apache-2.0")
        self.assertEqual(r["status"], "production_source_path_detected")
        self.assertTrue(r["license_review_required"])
        self.assertFalse(r["repository_spdx_is_rights_clearance"])
        self.assertFalse(r["functional_correctness_known"])

    def test_code_and_test_separation(self):
        pr = {"user": {"login": "Copilot"}, "merged_at": "2026-10-01"}
        paths = [{"filename": "src/math/exp_log_avx2_fma.cc", "additions": 10},
                 {"filename": "unittests/cc/math/test_exp_log_kernel.cc", "additions": 12}]
        r = audit_pr_metadata(pr, paths, "Apache-2.0")
        self.assertEqual(r["production_file_count"], 1)
        self.assertEqual(r["test_file_count"], 1)
        self.assertEqual(r["changed_production_languages"], ["C++"])

    def test_stratified_batch_selection(self):
        manifest = Path(__file__).resolve().parents[1] / "data/discovery/agent_pr_candidates_120.csv"
        rows = read_candidates(manifest)
        first = select_candidates(rows, per_language=2, language_offset=0)
        second = select_candidates(rows, per_language=2, language_offset=2)
        self.assertEqual(len(first), 24)
        self.assertEqual(len(second), 24)
        self.assertEqual(len({r["repository"] for r in first + second}), 48)
        self.assertEqual(first[0]["id"], "1")
        self.assertEqual(second[0]["id"], "3")
        with self.assertRaises(ValueError):
            select_candidates(rows, language_offset=2)

    @patch("ucode.audit.inspect_candidate")
    @patch("ucode.audit.read_candidates")
    def test_rate_limit_halts_remaining_requests(self, read, inspect):
        read.return_value = [
            {"repository": "a/a", "agent_pr_url": "https://github.com/a/a/pull/1"},
            {"repository": "b/b", "agent_pr_url": "https://github.com/b/b/pull/2"},
            {"repository": "c/c", "agent_pr_url": "https://github.com/c/c/pull/3"},
        ]
        inspect.side_effect = HTTPError("https://api.github.com", 429,
                                        "secondary rate limit", None, None)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            report = audit_manifest("ignored.csv", path)
            records = [json.loads(s) for s in path.read_text().splitlines()]
        self.assertEqual(inspect.call_count, 1)
        self.assertTrue(report["halted_for_rate_limit"])
        self.assertEqual([r["status"] for r in records],
                         ["rate_limited", "not_attempted_rate_limit",
                          "not_attempted_rate_limit"])

    def test_manifest_has_120_unique_candidates(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / "data/discovery/agent_pr_candidates_120.csv"
        rows = read_candidates(path)
        self.assertEqual(len(rows), 120)
        self.assertEqual(len({x["query_language"] for x in rows}), 12)
        self.assertEqual(len({x["repository"] for x in rows}), 120)


if __name__ == "__main__":
    unittest.main()
