"""Offline/opt-in SWE-rebench V2 metadata intake, NEVER evaluator or oracle.

Accept ONLY explicitly projected metadata columns from a user-provided local
Parquet/JSONL snapshot. No downloads, imports of external dataset scripts,
container execution, gold/test patch ingestion, or licensing decisions.
This is a *candidate discovery adapter* for a separately sourced dataset.
"""
from __future__ import annotations

import csv
import io
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

SWE_REBENCH_V2_DATASET = "nebius/SWE-rebench-V2"
EXPECTED_META_FIELDS = frozenset({
    "instance_id", "repo", "base_commit", "language", "license",
    "created_at", "image_name",
})
DISALLOWED_EVALUATOR_FIELDS = frozenset({
    "patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS",
    "FAIL_TO_FAIL", "PASS_TO_FAIL", "gold_patch",
    "oracle", "oracle_passed", "test_results", "meta",
    "pr_description", "problem_statement", "install_config", "interface",
})
LANGUAGE_MAP = {
    "py": "Python", "python": "Python",
    "js": "JavaScript", "javascript": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "java": "Java", "go": "Go", "golang": "Go",
    "rust": "Rust", "rs": "Rust",
    "c++": "C++", "cpp": "C++", "cxx": "C++",
    "c": "C", "c#": "C#", "csharp": "C#", "cs": "C#",
    "kotlin": "Kotlin", "kt": "Kotlin",
    "php": "PHP", "ruby": "Ruby", "rb": "Ruby",
}
def _safe_metadata_text(value, *, max_chars=512):
    """Never emit spreadsheet formulas or control sequences from foreign rows."""
    return (type(value) is str and len(value) <= max_chars
            and not value.startswith(("=", "+", "-", "@", "\t", "\r", "\n"))
            and all(ord(c) >= 32 and ord(c) != 127 for c in value))


def _untrusted_created_at(value):
    """SWE-rebench documentation has described this as string or int64 ms.

    Convert only millisecond integers to UTC; preserve well-formed timestamp
    strings verbatim rather than claiming they have been time-zone verified.
    """
    if value is None:
        return ""
    if type(value) is int:
        if not 946684800000 <= value <= 4102444800000:
            raise ValueError("upstream epoch milliseconds out of supported range")
        return datetime.fromtimestamp(
            value / 1000, tz=timezone.utc).isoformat()
    if not _safe_metadata_text(value, max_chars=64):
        raise ValueError("untrusted timestamp text malformed")
    return value


SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
FIELDS = (
    "source_dataset", "source_revision", "external_instance_id",
    "repository", "base_commit_sha", "normalized_search_scope_language",
    "upstream_language_label", "repository_license_metadata",
    "upstream_created_at_unverified", "upstream_image_name_untrusted",
    "related_to_existing_discovery_repo", "same_base_commit_cluster_hint",
    "rights_review", "independent_oracle_verified", "split_verified",
    "actual_task_execution_status", "experiment_eligible",
)


@dataclass(frozen=True)
class ExternalIntake:
    candidates: tuple[dict, ...]
    exclusions: tuple[dict, ...]
    report: dict


def screen_swe_rebench_v2(rows, *, revision: str,
                          existing_discovery_repositories=()) -> ExternalIntake:
    """Canonical metadata-only projection. Never infer oracle correctness."""
    if not SHA40.fullmatch(revision):
        raise ValueError("immutable 40-hex dataset source revision required")
    existing = {x.casefold() for x in existing_discovery_repositories}
    if any(type(x) is not str or not REPO.fullmatch(x)
           for x in existing_discovery_repositories):
        raise ValueError("discovery repository identifiers malformed")
    seen_ids = set()
    kept, excluded = [], []
    base_clusters = defaultdict(list)
    scanned = 0
    for row in rows:
        scanned += 1
        if type(row) is not dict:
            raise ValueError("dataset row must be a plain metadata dict")
        if set(row) & DISALLOWED_EVALUATOR_FIELDS:
            raise ValueError("gold/test patch, model annotations or policy prompt fields cannot enter metadata intake")
        if set(row) != EXPECTED_META_FIELDS:
            raise ValueError("exact seven projected metadata fields required; never silently ingest task labels")
        uid = row["instance_id"]
        repo = row["repo"]
        rev = row["base_commit"]
        raw_lang = row["language"]
        if (type(uid) is not str or not uid or len(uid) > 256
            or any(ord(c) < 32 for c in uid)):
            raise ValueError("invalid source instance ID")
        if uid in seen_ids:
            raise ValueError("duplicate instance ID in source snapshot")
        seen_ids.add(uid)
        if (type(repo) is not str or not REPO.fullmatch(repo)
            or type(rev) is not str or not SHA40.fullmatch(rev)):
            # Do not cherry-pick "bad" tasks away without recording attrition.
            excluded.append({"instance_id": uid,
                             "reason": "malformed_repo_or_base_sha"})
            continue
        if type(raw_lang) is not str:
            excluded.append({"instance_id": uid, "reason": "invalid_language_label"})
            continue
        lang = LANGUAGE_MAP.get(raw_lang.strip().lower())
        if not lang:
            excluded.append({"instance_id": uid,
                             "reason": "not_in_12_original_search_languages_or_unrecognized"})
            continue
        license_id = row["license"]
        if type(license_id) is not str or not license_id.strip():
            excluded.append({"instance_id": uid,
                             "reason": "missing_per_repository_license_metadata"})
            continue
        try:
            created_at = _untrusted_created_at(row.get("created_at"))
        except ValueError:
            excluded.append({"instance_id": uid,
                             "reason": "invalid_creation_timestamp"})
            continue
        image_name = row.get("image_name") or ""
        if (not _safe_metadata_text(uid, max_chars=256)
            or not _safe_metadata_text(raw_lang, max_chars=100)
            or not _safe_metadata_text(license_id, max_chars=256)
            or not _safe_metadata_text(image_name, max_chars=512)):
            excluded.append({"instance_id": uid,
                             "reason": "unsafe_spreadsheet_or_control_metadata"})
            continue
        base_clusters[(repo.casefold(), rev)].append(uid)
        kept.append({
            "source_dataset": SWE_REBENCH_V2_DATASET,
            "source_revision": revision,
            "external_instance_id": uid,
            "repository": repo,
            "base_commit_sha": rev,
            "normalized_search_scope_language": lang,
            "upstream_language_label": raw_lang,
            "repository_license_metadata": license_id,
            "upstream_created_at_unverified": created_at,
            "upstream_image_name_untrusted": image_name,
            "related_to_existing_discovery_repo": "POTENTIAL_OVERLAP_REVIEW"
            if repo.casefold() in existing else "NOT_MATCHED_BY_NAME_ONLY",
            "same_base_commit_cluster_hint": "",  # Filled after stream complete
            "rights_review": "PENDING",
            "independent_oracle_verified": "FALSE",
            "split_verified": "FALSE",
            "actual_task_execution_status": "NOT_RUN",
            "experiment_eligible": "FALSE",
        })
    clusters = {k: v for k, v in base_clusters.items() if len(v) > 1}
    for r in kept:
        group = (r["repository"].casefold(), r["base_commit_sha"])
        if group in clusters:
            r["same_base_commit_cluster_hint"] = (
                "CANDIDATE_SHARED_BASE_REVIEW:" + sha256(
                    ("\x00".join(group)).encode()).hexdigest()[:16])
    kept.sort(key=lambda x: x["external_instance_id"])
    excluded.sort(key=lambda x: x["instance_id"])
    if scanned != len(kept)+len(excluded):
        raise ValueError("screening attrition arithmetic failed")
    report = {
        "schema_version": "1.0",
        "stage": "EXTERNAL_SOURCE_METADATA_PROJECTION_NOT_TASK_ADMISSION",
        "source_dataset": SWE_REBENCH_V2_DATASET,
        "source_revision": revision,
        "rows_scanned_in_LOCAL_snapshot": scanned,
        "metadata_candidate_rows_kept": len(kept),
        "excluded_metadata_rows": len(excluded),
        "exclusion_reasons": dict(sorted(Counter(
            e["reason"] for e in excluded).items())),
        "kept_by_normalized_language": dict(sorted(Counter(
            r["normalized_search_scope_language"] for r in kept).items())),
        "potential_source_repo_name_overlap_count": sum(
            r["related_to_existing_discovery_repo"] != "NOT_MATCHED_BY_NAME_ONLY"
            for r in kept),
        "candidate_shared_base_repo_sha_groups": len(clusters),
        "timestamp_format": "unverified upstream strings OR converted epoch milliseconds UTC",
        "spreadsheet_formula_cells_allowed": False,
        "independent_executable_task_admissions": 0,
        "evaluation_gold_or_test_patches_exposed": False,
        "model_inference_executed": False,
        "sealed_oracles_verified": False,
        "train_test_split_adjudicated": False,
        "warning": "Dataset card license is NOT per-repository rights approval; source split=train is NOT an independent train/evaluation split",
    }
    return ExternalIntake(tuple(kept), tuple(excluded), report)


def csv_release(data: ExternalIntake) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS,
                            lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for r in data.candidates:
        writer.writerow(r)
    return output.getvalue()


def read_local_parquet_projected(paths, *, batch_size=1024):
    """Requires separately installed pyarrow; reads only seven safe fields.

    Input files are a *local user-controlled pinned snapshot*; caller has to
    assess Parquet parser security separately. Never invoke remote data code.
    """
    if type(batch_size) is not int or not 1 <= batch_size <= 16384:
        raise ValueError("safe Parquet batch size required")
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "opt-in pyarrow not installed; approved offline environment required"
        ) from exc
    for path in sorted(Path(p) for p in paths):
        if path.suffix != ".parquet" or not path.is_file() or path.is_symlink():
            raise ValueError("local normal Parquet files only")
        pf = pq.ParquetFile(path)
        schema_names = set(pf.schema_arrow.names)
        if not EXPECTED_META_FIELDS <= schema_names:
            raise ValueError("Parquet snapshot lacks required safe fields")
        for batch in pf.iter_batches(
            batch_size=batch_size, columns=sorted(EXPECTED_META_FIELDS)):
            for record in batch.to_pylist():
                yield record
