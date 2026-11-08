"""Adversarial first-party tests for public HF branch revision metadata.

Entire CI path is offline: even mock HTTPS responses never connect externally.
"""
from __future__ import annotations

from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.capture_public_hf_sha_candidates import main
from ucode.hub_revision_preflight import (
    ROOT, _MAX_RESPONSE, _read_public_head_metadata,
    build_public_revision_packet, public_head_url,
    validate_revision_candidate_packet,
)

_CANDIDATE = "a" * 40


def _mock_one_first(url: str) -> dict | None:
    return {"sha": _CANDIDATE, "authorization": "FAKE_SHOULD_NEVER_APPEAR"} if (
        "Qwen2.5-Coder-7B-Instruct" in url) else None


class FakeResponse:
    def __init__(self, url, data, *, mime="application/json", code=200, final=None):
        self.url = url
        self.final = url if final is None else final
        self.status = code
        self.headers = {"Content-Type": mime}
        self.data = data

    def geturl(self):
        return self.final

    def read(self, limit):
        return self.data[:limit]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def open(self, req, timeout):
        self.requests.append((req, timeout))
        return self.response


class PublicHFRevisionPreflightTests(unittest.TestCase):
    def test_default_mode_never_uses_network(self):
        with patch("ucode.hub_revision_preflight._read_public_head_metadata",
                   side_effect=AssertionError("network must not run")):
            p = build_public_revision_packet()
        a = validate_revision_candidate_packet(p)
        self.assertEqual(p["collection_mode"], "OFFLINE_PENDING")
        self.assertEqual(a["registered_models"], 6)
        self.assertEqual(a["observed_public_sha_candidates_not_frozen_revisions"], 0)
        self.assertEqual(a["licensed_runnable_checkpoints"], 0)
        self.assertEqual(p["approved_checkpoint_count"], 0)
        self.assertTrue(all(x["observed_hub_main_sha40_candidate"] is None
                            for x in p["public_sha_candidate_rows"]))

    def test_one_untrusted_public_sha_candidate_cannot_approve(self):
        p = build_public_revision_packet(
            capture_public_heads=True, public_getter=_mock_one_first)
        a = validate_revision_candidate_packet(p)
        self.assertEqual(p["public_sha_candidates_observed"], 1)
        self.assertEqual(a["models_without_observed_sha_candidate"], 5)
        self.assertEqual(a["official_model_revisions_approved"], 0)
        self.assertFalse(p["model_revisions_selected_for_execution"])
        self.assertFalse(p["authenticated_provenance_certificates"])
        self.assertEqual(p["real_model_executions"], 0)
        self.assertNotIn("authorization", json.dumps(p))

    def test_unknown_lookups_cannot_change_frozen_model_roster(self):
        with self.assertRaisesRegex(ValueError, "unregistered model"):
            public_head_url("Random/Unknown-Instruct")
        with self.assertRaisesRegex(ValueError, "unregistered model"):
            public_head_url("Qwen/Qwen2.5-Coder-7B-Instruct/../../secrets")

    def test_only_canonical_hub_urls(self):
        p = build_public_revision_packet()
        ids = [row["model_id"] for row in p["public_sha_candidate_rows"]]
        self.assertEqual(len(set(ids)), 6)
        for row in p["public_sha_candidate_rows"]:
            self.assertEqual(
                row["public_read_only_request_url"], public_head_url(row["model_id"]))
            self.assertTrue(row["public_read_only_request_url"].startswith(
                "https://huggingface.co/api/models/"))
            self.assertTrue(row["public_read_only_request_url"].endswith("?expand=sha"))

    def test_abbreviated_or_uppercase_sha_rejected(self):
        for badsha in ("abcd123", "A"*40, "g"*40, "a"*39, None):
            p = build_public_revision_packet(
                capture_public_heads=True, public_getter=lambda _: {"sha": badsha})
            self.assertEqual(p["public_sha_candidates_observed"], 0)
        p = build_public_revision_packet(
            capture_public_heads=True, public_getter=_mock_one_first)
        p["public_sha_candidate_rows"][0]["observed_hub_main_sha40_candidate"] = "ab12"
        with self.assertRaisesRegex(ValueError, "SHA40 candidate invalid"):
            validate_revision_candidate_packet(p)

    def test_sha_count_cannot_be_inflated(self):
        p = build_public_revision_packet()
        p["public_sha_candidates_observed"] = 1
        with self.assertRaisesRegex(ValueError, "observation count"):
            validate_revision_candidate_packet(p)

    def test_offline_claim_of_observed_sha_rejected(self):
        p = build_public_revision_packet()
        p["public_sha_candidate_rows"][0]["observed_hub_main_sha40_candidate"] = _CANDIDATE
        p["public_sha_candidate_rows"][0]["public_metadata_status"] = (
            "HTTPS_PUBLIC_SHA_OBSERVED_NOT_INDEPENDENTLY_AUTHENTICATED")
        p["public_sha_candidates_observed"] = 1
        with self.assertRaisesRegex(ValueError, "offline pending"):
            validate_revision_candidate_packet(p)

    def test_forged_approval_flag_rejected(self):
        for key in (
            "model_revisions_selected_for_execution",
            "checkpoint_weights_verified",
            "tokenizer_revisions_independently_frozen",
            "license_rights_approved",
            "authenticated_provenance_certificates",
        ):
            p = build_public_revision_packet()
            p[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(
                    ValueError, "cannot grant model approval"):
                validate_revision_candidate_packet(p)

    def test_forged_row_trust_flag_rejected(self):
        for key in (
            "authenticated_commit_signature", "weight_files_sha256_verified",
            "tokenizer_files_sha256_verified", "full_license_reviewed",
            "model_load_measured", "approved_for_inference",
        ):
            p = build_public_revision_packet()
            p["public_sha_candidate_rows"][0][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(
                    ValueError, "cannot attest model files"):
                validate_revision_candidate_packet(p)

    def test_forged_chat_template_hash_rejected(self):
        p = build_public_revision_packet()
        p["public_sha_candidate_rows"][0]["frozen_chat_template_sha256"] = "b"*64
        with self.assertRaisesRegex(ValueError, "chat-template"):
            validate_revision_candidate_packet(p)

    def test_wrong_identity_url_and_missing_row_rejected(self):
        for corruption in ("swap", "url", "truncate", "extra"):
            p = build_public_revision_packet()
            if corruption == "swap":
                p["public_sha_candidate_rows"].reverse()
            elif corruption == "url":
                p["public_sha_candidate_rows"][0]["public_read_only_request_url"] = (
                    "https://evil.test/s")
            elif corruption == "truncate":
                p["public_sha_candidate_rows"].pop()
            elif corruption == "extra":
                p["public_sha_candidate_rows"][0]["approved"] = True
            with self.subTest(corruption=corruption), self.assertRaises(ValueError):
                validate_revision_candidate_packet(p)

    def test_malformed_counts_and_executions_rejected(self):
        for field, value in (("real_model_executions", 1),
                             ("real_model_executions", True),
                             ("real_task_executions", 2),
                             ("approved_checkpoint_count", 6),
                             ("approved_checkpoint_count", True)):
            p = build_public_revision_packet()
            p[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "cannot grant model approval"):
                validate_revision_candidate_packet(p)

    def test_undocumented_packet_fields_rejected(self):
        p = build_public_revision_packet()
        p["private_token"] = "fake"
        with self.assertRaises(ValueError):
            validate_revision_candidate_packet(p)

    def test_offline_with_getter_rejected(self):
        with self.assertRaisesRegex(ValueError, "offline mode refuses"):
            build_public_revision_packet(public_getter=lambda url: {"sha": _CANDIDATE})
        with self.assertRaises(TypeError):
            build_public_revision_packet(capture_public_heads="yes")
        with self.assertRaises(TypeError):
            build_public_revision_packet(capture_public_heads=True, public_getter=42)

    def test_mocked_public_https_reads_only_sha_no_auth(self):
        url = public_head_url("Qwen/Qwen2.5-Coder-7B-Instruct")
        response = FakeResponse(url, json.dumps({
            "sha": _CANDIDATE, "metadata": {"fake_secret": "never_emit"}
        }).encode("utf-8"))
        opener = FakeOpener(response)
        with patch("urllib.request.build_opener", return_value=opener):
            got = _read_public_head_metadata(url)
        self.assertEqual(got, {"sha": _CANDIDATE})
        self.assertEqual(len(opener.requests), 1)
        req, timeout = opener.requests[0]
        self.assertEqual(timeout, 7)
        self.assertEqual(req.full_url, url)
        self.assertEqual(req.get_method(), "GET")
        self.assertNotIn("authorization", repr(req.headers).lower())

    def test_mocked_https_rejects_bad_mime_redirect_and_oversize(self):
        url = public_head_url("Qwen/Qwen2.5-Coder-7B-Instruct")
        for response in (
            FakeResponse(url, b'{"sha":"' + _CANDIDATE.encode() + b'"}',
                         mime="text/plain"),
            FakeResponse(url, b'{"sha":"' + _CANDIDATE.encode() + b'"}',
                         final="https://evil.test/redirect"),
            FakeResponse(url, b"x" * (_MAX_RESPONSE + 1)),
            FakeResponse(url, b'{"sha":null}'),
            FakeResponse(url, b'{"sha":"abc"}'),
            FakeResponse(url, b"not-json"),
        ):
            with self.subTest(response=response.data[:8]), patch(
                "urllib.request.build_opener",
                return_value=FakeOpener(response)):
                self.assertIsNone(_read_public_head_metadata(url))

    def test_cli_default_offline_and_strict_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "public_pending.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--output", str(output)]), 0)
                self.assertEqual(main(["--require-approved"]), 2)
            contents = output.read_text(encoding="utf-8")
            result = json.loads(contents)
            self.assertEqual(result, build_public_revision_packet())
            self.assertEqual(result["public_sha_candidates_observed"], 0)
            self.assertNotIn("Authorization", contents)
            self.assertNotIn("HF_TOKEN", contents)

    def test_cli_symlink_output_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original"
            original.write_text("never-overwrite", encoding="utf-8")
            alias = Path(tmp) / "link"
            alias.symlink_to(original)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    ValueError, "symlink"):
                main(["--output", str(alias)])
            self.assertEqual(original.read_text(encoding="utf-8"), "never-overwrite")


if __name__ == "__main__":
    unittest.main()
