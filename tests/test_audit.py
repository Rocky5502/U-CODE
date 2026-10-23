import unittest
from unittest.mock import patch

from ucode.audit import audit_pr_metadata, inspect_candidate, is_source_path, read_candidates


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
        self.assertEqual(result["status"], "metadata_supported_needs_manual_validation")
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
        self.assertEqual(result["status"], "triage_reject_or_needs_review")

    def test_reject_non_bot_or_unmerged(self):
        changed = [{"filename": "src/mod.py", "additions": 1, "deletions": 0}]
        p = {"user": {"login": "person"}, "merged_at": "2026-10-01"}
        self.assertEqual(audit_pr_metadata(p, changed, "MIT")["status"],
                         "triage_reject_or_needs_review")
        p["user"]["login"] = "copilot-swe-agent[bot]"
        p["merged_at"] = None
        self.assertEqual(audit_pr_metadata(p, changed, "MIT")["status"],
                         "triage_reject_or_needs_review")

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

    def test_manifest_has_120_unique_candidates(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / "data/discovery/agent_pr_candidates_120.csv"
        rows = read_candidates(path)
        self.assertEqual(len(rows), 120)
        self.assertEqual(len({x["query_language"] for x in rows}), 12)
        self.assertEqual(len({x["repository"] for x in rows}), 120)


if __name__ == "__main__":
    unittest.main()
