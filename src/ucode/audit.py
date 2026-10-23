"""Read-only GitHub candidate audit.

PRs matching bot-author search are *leads*, not automatically AI-written files.
This scanner neither clones nor runs third-party source; metadata != correctness.
"""
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_SUFFIXES = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".c",
    ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".go", ".rs", ".cs",
    ".kt", ".kts", ".swift", ".rb", ".php", ".dart",
}
EXCLUDED_PARTS = {
    "vendor", "node_modules", "dist", "build", "third_party", "third-party",
    "generated", ".git", "target", "__pycache__", "site-packages",
}
PR_URL = re.compile(r"^https://github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)$")
EXPECTED_AGENTS = {"copilot-swe-agent[bot]", "copilot"}  # GitHub API may report Copilot
TEST_DIRS = {"test", "tests", "spec", "specs", "unittests", "__tests__"}
SOURCE_LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".java": "Java", ".go": "Go", ".rs": "Rust",
    ".cc": "C++", ".cpp": "C++", ".cxx": "C++", ".hpp": "C++",
    ".c": "C", ".h": "C/C++ Header", ".cs": "C#", ".kt": "Kotlin",
    ".kts": "Kotlin", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".dart": "Dart",
}


def is_test_path(path: str) -> bool:
    """Classify source used only for tests/specifications from its path."""
    parts = [p.lower() for p in Path(path).parts]
    if not parts:
        return False
    name = parts[-1]
    return (any(p in TEST_DIRS or p.endswith(".tests") for p in parts[:-1])
            or name.startswith("test_")
            or name.endswith(("_test.py", "_test.go", "tests.swift", "tests.cs"))
            or ".test." in name or ".spec." in name)


def source_language(path: str) -> str | None:
    """Language of the *changed file*, never the repository's GitHub language."""
    return SOURCE_LANGUAGES.get(Path(path).suffix.lower())


def is_source_path(path: str) -> bool:
    """Conservative eligible source path (not a guarantee of human/AI origin)."""
    parsed = Path(path)
    return (
        parsed.suffix.lower() in SOURCE_SUFFIXES
        and not any(part.lower() in EXCLUDED_PARTS for part in parsed.parts)
        and not parsed.name.lower().endswith((".min.js", ".generated.ts",
                                                   ".gradle.kts"))
    )


def audit_pr_metadata(pr: dict, files: list[dict], license_spdx: str | None) -> dict:
    """Pure metadata triage; NEVER claim full provenance or functional correctness."""
    account = str((pr.get("user") or {}).get("login") or "")
    agent_match = account.casefold() in EXPECTED_AGENTS
    merged = bool(pr.get("merged_at"))
    code_files = [f for f in files if is_source_path(str(f.get("filename", "")))]
    additions = sum(max(0, int(f.get("additions", 0))) for f in code_files)
    deletions = sum(max(0, int(f.get("deletions", 0))) for f in code_files)
    production_files = [f for f in code_files if not is_test_path(str(f.get("filename", "")))]
    test_files = [f for f in code_files if is_test_path(str(f.get("filename", "")))]
    if not (merged and agent_match):
        status = "agent_or_merge_mismatch"
    elif not files:
        status = "empty_file_list_needs_review"
    elif production_files:
        status = "production_source_path_detected"
    elif test_files:
        status = "test_only_source_change"
    else:
        status = "non_source_change"
    actual_languages = sorted({source_language(str(f.get("filename", "")))
                               for f in production_files if source_language(str(f.get("filename", "")))})
    return {
        "status": status,
        "agent_account": account,
        "agent_account_matches_search": agent_match,
        "merged": merged,
        "base_sha": (pr.get("base") or {}).get("sha"),
        "head_sha": (pr.get("head") or {}).get("sha"),
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "code_files": [f.get("filename") for f in code_files],
        "code_file_count": len(code_files),
        "production_file_count": len(production_files),
        "test_file_count": len(test_files),
        "production_code_files": [f.get("filename") for f in production_files],
        "test_code_files": [f.get("filename") for f in test_files],
        "changed_production_languages": actual_languages,
        "source_additions": additions,
        "source_deletions": deletions,
        "repository_license_spdx": license_spdx or "UNKNOWN",
        # Repo-level SPDX never guarantees rights on every changed source file.
        "license_review_required": True,
        "repository_spdx_is_rights_clearance": False,
        "manual_patch_review_done": False,
        "file_level_license_review_done": False,
        "test_verification_done": False,
        "functional_correctness_known": False,
        "note": "Counts are PR changed-source lines, not independently proven AI-written lines.",
    }


def read_candidates(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    seen = set()
    for row in rows:
        m = PR_URL.fullmatch(row.get("agent_pr_url", ""))
        if m is None or row.get("repository") != m.group(1):
            raise ValueError("invalid repository / PR URL in manifest")
        if row["repository"].casefold() in seen:
            raise ValueError("duplicate repository in manifest")
        seen.add(row["repository"].casefold())
    return rows


def github_json(path: str, token: str | None = None) -> object:
    """GitHub REST GET; raises on HTTP/rate limits; never sends credentials elsewhere."""
    if not path.startswith("/repos/"):
        raise ValueError("only repository API paths are supported")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "U-CODE-research-audit/0.1",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as res:
        return json.load(res)


def _files_for_pr(repo: str, number: int, token: str | None) -> list[dict]:
    files = []
    for page in range(1, 31):  # GitHub's cap is 3000 changed files per PR
        chunk = github_json(f"/repos/{repo}/pulls/{number}/files?per_page=100&page={page}", token)
        if not isinstance(chunk, list):
            raise ValueError("unexpected GitHub PR files response")
        files.extend(chunk)
        if len(chunk) < 100:
            return files
    # GitHub REST returns at most 3000 changed files for a PR.
    # Do not silently treat an ambiguous boundary as a complete audit.
    raise ValueError("PR changed-file list reached GitHub's 3000-file cap")


def inspect_candidate(row: dict, token: str | None = None) -> dict:
    match = PR_URL.fullmatch(row["agent_pr_url"])
    if not match:
        raise ValueError("invalid PR link")
    repo, number_str = match.groups()
    number = int(number_str)
    base = f"/repos/{repo}"
    pr = github_json(f"{base}/pulls/{number}", token)
    files = _files_for_pr(repo, number, token)
    repodata = github_json(base, token)
    if not isinstance(pr, dict) or not isinstance(repodata, dict):
        raise ValueError("unexpected GitHub API response")
    license_obj = repodata.get("license") or {}
    spdx = license_obj.get("spdx_id") if isinstance(license_obj, dict) else None
    metadata = audit_pr_metadata(pr, files, spdx)
    return {
        "discovery_language": row.get("query_language"),
        "repository": repo,
        "agent_pr_url": row["agent_pr_url"],
        "pr_number": number,
        "repo_default_branch": repodata.get("default_branch"),
        "repo_archived": repodata.get("archived"),
        "repo_is_fork": repodata.get("fork"),
        "repo_parent_full_name": (repodata.get("parent") or {}).get("full_name"),
        "language_label_is_repository_primary_not_patch_label": True,
        **metadata,
    }


def select_candidates(
    rows: list[dict], limit: int = 0, per_language: int = 0,
    language_offset: int = 0,
) -> list[dict]:
    """Select a deterministic slice; source discovery ordering remains preserved.

    `per_language=2, language_offset=2` selects the third and fourth record
    in each original language group, without conflating the group with
    changed-file language.
    """
    if limit < 0 or per_language < 0 or language_offset < 0:
        raise ValueError("selection parameters must be nonnegative")
    if per_language == 0 and language_offset:
        raise ValueError("language_offset requires per_language")
    if per_language:
        seen: dict[str, int] = {}
        selected: list[dict] = []
        for row in rows:
            language = str(row.get("query_language", ""))
            position = seen.get(language, 0)
            seen[language] = position + 1
            if language_offset <= position < language_offset + per_language:
                selected.append(row)
    else:
        selected = rows
    return selected[:limit] if limit else selected


def audit_manifest(
    input_path: str | Path, output_path: str | Path, limit: int = 0,
    per_language: int = 0, language_offset: int = 0,
) -> dict:
    """Read-only deterministic audit; output overwritten, never appended.

    Respect GitHub 403/429 rate-limit signals by stopping the batch immediately,
    without retry bursts. Unattempted candidates are distinct from retrieval
    failures; proceed in a later authorized session.
    """
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    rows = read_candidates(input_path)
    selected = select_candidates(rows, limit, per_language, language_offset)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    halted = False
    with open(output, "w", encoding="utf-8") as f:
        for row in selected:
            if halted:
                result = {"repository": row["repository"],
                          "agent_pr_url": row["agent_pr_url"],
                          "status": "not_attempted_rate_limit"}
            else:
                try:
                    result = inspect_candidate(row, token)
                except urllib.error.HTTPError as exc:
                    limited = exc.code in (403, 429)
                    result = {"repository": row["repository"],
                              "agent_pr_url": row["agent_pr_url"],
                              "status": "rate_limited" if limited else "retrieval_failed",
                              "error_type": type(exc).__name__,
                              "http_status": exc.code}
                    if limited:
                        halted = True
                except (ValueError, urllib.error.URLError, TimeoutError, OSError) as exc:
                    result = {"repository": row["repository"],
                              "agent_pr_url": row["agent_pr_url"],
                              "status": "retrieval_failed",
                              "error_type": type(exc).__name__,
                              "error": str(exc)[:220]}
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            counts[result["status"]] = counts.get(result["status"], 0) + 1
    return {"candidates_requested": len(selected), "statuses": counts,
            "halted_for_rate_limit": halted, "output": str(output)}
