"""Strict public Hugging Face HEAD revision *candidate* collector for U-CODE.

A public Hub SHA is a mutable-branch metadata observation, NOT frozen model
weights, independently authenticated commit identity, accepted model terms,
a tokenizer or chat-template checksum, an approved checkpoint or runnable GPU.
Default path is OFFLINE. Network lookup is explicit opt-in, six fixed URLs
only, no token, no redirects/proxy, no downloads of model or source files.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re
import urllib.error
import urllib.request

from .model_readiness import validate_selected_manifest

ROOT = Path(__file__).resolve().parents[2]
_SELECTED = "configs/accepted_six_model_study_2026-10-25.json"
_ORIGINAL = "configs/models_v2_2026-10-24.json"
_PROTOCOL = "configs/confirmatory_sbse_protocol_2026-10-25.json"
_SHA40 = re.compile(r"^[a-f0-9]{40}$")
_URL_PREFIX = "https://huggingface.co/api/models/"
_URL_SUFFIX = "?expand=sha"
_MAX_RESPONSE = 32768
_STAGE = "PUBLIC_HUB_MAIN_SHA_CANDIDATES_NOT_CHECKPOINT_ATTESTATIONS"


def _read_registry(root: Path, relative: str) -> dict:
    obj = json.loads((root / relative).read_text(encoding="utf-8"))
    if type(obj) is not dict:
        raise ValueError("canonical model registry is not a JSON object")
    return obj


def _selected_ids(root: Path) -> tuple[str, ...]:
    selected = _read_registry(root, _SELECTED)
    source = _read_registry(root, _ORIGINAL)
    protocol = _read_registry(root, _PROTOCOL)
    statuses = validate_selected_manifest(selected, source)
    ids = tuple(x.model_id for x in statuses)
    if (len(ids) != 6 or len(set(ids)) != 6
            or any(x.runnable for x in statuses)
            or protocol.get("status") != "PROSPECTIVE_NO_QUALIFIED_EXECUTABLE_TASKS"
            or protocol.get("model_ids") != list(ids)
            or protocol.get("qualified_task_ids") != []
            or protocol.get("model_revisions_frozen") is not False
            or protocol.get("results_measured") is not False
            or protocol.get("external_code_executions") != 0
            or selected.get("no_paid_compute_approved") is not True):
        raise ValueError("frozen six-model study is changed or self-approved")
    for item in selected["models"]:
        if (item.get("checkpoint_revision") is not None
                or item.get("tokenizer_revision") is not None
                or item.get("frozen_chat_template_sha256") is not None
                or item.get("model_weights_verified") is not False
                or item.get("inference_execution_status") != "NOT_RUN"
                or item.get("independently_verified_task_runs") != 0):
            raise ValueError("unverified selected model unexpectedly promoted")
    return ids


def public_head_url(model_id: str, *, root: Path = ROOT) -> str:
    """Only fixed user-selected model IDs are URL-eligible."""
    if type(model_id) is not str or model_id not in _selected_ids(root):
        raise ValueError("unregistered model public lookup forbidden")
    return _URL_PREFIX + model_id + _URL_SUFFIX


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _read_public_head_metadata(url: str) -> dict | None:
    """Opt-in unauthenticated public SHA-only request; failure is unavailable.

    No caller URL, account token, proxies, redirects, retries, file contents,
    arbitrary Python or third-party repository code. Never log response body.
    The connection origin is a fixed HTTPS Hub API path.
    """
    if (type(url) is not str or not url.startswith(_URL_PREFIX)
            or not url.endswith(_URL_SUFFIX)):
        raise ValueError("unexpected public hub endpoint")
    request = urllib.request.Request(
        url, headers={"Accept": "application/json",
                      "User-Agent": "U-CODE-Public-HEAD-Metadata/1.0"},
        method="GET")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), _RejectRedirect())
    try:
        with opener.open(request, timeout=7) as response:
            if response.geturl() != url or response.status != 200:
                return None
            mime = response.headers.get("Content-Type", "")
            if "application/json" not in mime.lower():
                return None
            raw = response.read(_MAX_RESPONSE + 1)
    except (OSError, ValueError, urllib.error.URLError):
        return None
    if not raw or len(raw) > _MAX_RESPONSE:
        return None
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    if type(obj) is not dict or type(obj.get("sha")) is not str:
        return None
    if not _SHA40.fullmatch(obj["sha"]):
        return None
    # Only SHA survives. Other fields, including possibly injected prompt
    # text, are ignored. Public HTTPS is NOT a signature or immutable pin.
    return {"sha": obj["sha"]}


def validate_revision_candidate_packet(packet: dict, *, root: Path = ROOT) -> dict:
    """Fail-closed public packet validator; no privilege-granting output."""
    ids = _selected_ids(root)
    expected_top = {
        "schema_version", "stage", "collection_mode",
        "public_sha_candidate_rows", "public_sha_candidates_observed",
        "model_revisions_selected_for_execution", "checkpoint_weights_verified",
        "tokenizer_revisions_independently_frozen", "license_rights_approved",
        "authenticated_provenance_certificates", "real_model_executions",
        "real_task_executions", "approved_checkpoint_count",
    }
    if (type(packet) is not dict or set(packet) != expected_top
            or packet["schema_version"] != "1.0"
            or packet["stage"] != _STAGE
            or packet["collection_mode"] not in ("OFFLINE_PENDING", "OPT_IN_PUBLIC_HTTPS")
            or any(packet[k] is not False for k in (
                "model_revisions_selected_for_execution",
                "checkpoint_weights_verified",
                "tokenizer_revisions_independently_frozen",
                "license_rights_approved",
                "authenticated_provenance_certificates",
            ))
            or type(packet["real_model_executions"]) is not int
            or packet["real_model_executions"] != 0
            or type(packet["real_task_executions"]) is not int
            or packet["real_task_executions"] != 0
            or type(packet["approved_checkpoint_count"]) is not int
            or packet["approved_checkpoint_count"] != 0):
        raise ValueError("public model branch SHA cannot grant model approval")
    rows = packet["public_sha_candidate_rows"]
    if type(rows) is not list or len(rows) != 6:
        raise ValueError("exactly six model SHA candidate rows required")
    expected_row = {
        "model_id", "public_read_only_request_url",
        "observed_hub_main_sha40_candidate",
        "public_metadata_status", "head_branch_can_change",
        "authenticated_commit_signature", "weight_files_sha256_verified",
        "tokenizer_files_sha256_verified", "frozen_chat_template_sha256",
        "full_license_reviewed", "model_load_measured",
        "approved_for_inference",
    }
    count = 0
    for i, row in enumerate(rows):
        if type(row) is not dict or set(row) != expected_row:
            raise ValueError("model candidate row has unknown/privileged fields")
        if row["model_id"] != ids[i] or row["public_read_only_request_url"] != (
            _URL_PREFIX + ids[i] + _URL_SUFFIX):
            raise ValueError("model identity or fixed public source URL drift")
        sha = row["observed_hub_main_sha40_candidate"]
        state = row["public_metadata_status"]
        if sha is None:
            if state not in ("NOT_QUERIED_OFFLINE", "PUBLIC_METADATA_LOOKUP_UNAVAILABLE"):
                raise ValueError("unobserved model cannot claim an observed SHA")
        elif (type(sha) is not str or not _SHA40.fullmatch(sha)
              or state != "HTTPS_PUBLIC_SHA_OBSERVED_NOT_INDEPENDENTLY_AUTHENTICATED"):
            raise ValueError("public commit SHA40 candidate invalid or self-approved")
        if (packet["collection_mode"] == "OFFLINE_PENDING"
                and (sha is not None or state != "NOT_QUERIED_OFFLINE")):
            raise ValueError("offline pending cannot fabricate HTTP observations")
        if any(row[k] is not False for k in (
            "authenticated_commit_signature",
            "weight_files_sha256_verified",
            "tokenizer_files_sha256_verified",
            "full_license_reviewed", "model_load_measured",
            "approved_for_inference",
        )):
            raise ValueError("public branch pointer cannot attest model files")
        if row["head_branch_can_change"] is not True:
            raise ValueError("public branch pointer is mutable and unaudited")
        if row["frozen_chat_template_sha256"] is not None:
            raise ValueError("no chat-template hash from branch metadata")
        count += int(sha is not None)
    if (type(packet["public_sha_candidates_observed"]) is not int
            or packet["public_sha_candidates_observed"] != count):
        raise ValueError("SHA observation count drift")
    return {
        "stage": _STAGE,
        "registered_models": 6,
        "observed_public_sha_candidates_not_frozen_revisions": count,
        "models_without_observed_sha_candidate": 6-count,
        "official_model_revisions_approved": 0,
        "independently_verified_weight_or_tokenizer_hashes": 0,
        "licensed_runnable_checkpoints": 0,
        "real_inference_executions": 0,
    }


def build_public_revision_packet(
    *, root: Path = ROOT, capture_public_heads: bool = False,
    public_getter=None,
) -> dict:
    """Create six-row offline packet; optionally query only public SHA metadata.

    public_getter is for first-party test injection only. A metadata getter,
    including caller-controlled data, NEVER grants rights or task eligibility.
    """
    ids = _selected_ids(root)
    if type(capture_public_heads) is not bool:
        raise TypeError("capture_public_heads must be explicit boolean")
    if public_getter is not None and not callable(public_getter):
        raise TypeError("public_getter must be callable")
    if not capture_public_heads and public_getter is not None:
        raise ValueError("offline mode refuses a callable metadata getter")
    getter = public_getter or _read_public_head_metadata
    rows = []
    for model_id in ids:
        url = _URL_PREFIX + model_id + _URL_SUFFIX
        metadata = getter(url) if capture_public_heads else None
        sha = metadata.get("sha") if type(metadata) is dict else None
        if type(sha) is not str or not _SHA40.fullmatch(sha):
            sha = None
        rows.append({
            "model_id": model_id,
            "public_read_only_request_url": url,
            "observed_hub_main_sha40_candidate": sha,
            "public_metadata_status": (
                "HTTPS_PUBLIC_SHA_OBSERVED_NOT_INDEPENDENTLY_AUTHENTICATED"
                if sha is not None else (
                    "PUBLIC_METADATA_LOOKUP_UNAVAILABLE" if capture_public_heads
                    else "NOT_QUERIED_OFFLINE")),
            "head_branch_can_change": True,
            "authenticated_commit_signature": False,
            "weight_files_sha256_verified": False,
            "tokenizer_files_sha256_verified": False,
            "frozen_chat_template_sha256": None,
            "full_license_reviewed": False,
            "model_load_measured": False,
            "approved_for_inference": False,
        })
    packet = {
        "schema_version": "1.0",
        "stage": _STAGE,
        "collection_mode": (
            "OPT_IN_PUBLIC_HTTPS" if capture_public_heads else "OFFLINE_PENDING"),
        "public_sha_candidate_rows": rows,
        "public_sha_candidates_observed": sum(
            int(x["observed_hub_main_sha40_candidate"] is not None)
            for x in rows),
        "model_revisions_selected_for_execution": False,
        "checkpoint_weights_verified": False,
        "tokenizer_revisions_independently_frozen": False,
        "license_rights_approved": False,
        "authenticated_provenance_certificates": False,
        "real_model_executions": 0,
        "real_task_executions": 0,
        "approved_checkpoint_count": 0,
    }
    validate_revision_candidate_packet(packet, root=root)
    return packet
