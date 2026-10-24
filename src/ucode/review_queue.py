"""Conservative manual review ordering for metadata-only GitHub PR leads.

No PR from this module is accepted as AI-written or runnable: all candidate
statuses remain pending file rights, line/commit attribution and a sealed
independent oracle. Inputs are repository metadata, not executable source.
"""
from dataclasses import dataclass
from typing import Sequence

LICENSE_UNKNOWN = {None, "", "NOASSERTION", "UNKNOWN"}
SENSITIVE_FRAGMENTS = (
    "auth", "oauth", "saml", "crypto", "credential", "secret", "token",
    "payment", "password", "login", "security", "permission",
)
GENERATED_OR_DATA_HINTS = (
    "wordlist", "dictionary", "fixtures", "generated", "codegen",
    "vendor", "min.js",
)


@dataclass(frozen=True)
class ReviewLead:
    candidate_id: int
    repository: str
    url: str
    language: str
    priority_class: str
    reasons: tuple[str, ...]
    production_path_count: int
    test_path_count: int
    file_rights_verified: bool = False
    independently_oracle_verified: bool = False
    ai_line_attribution_verified: bool = False

    @property
    def eligible(self) -> bool:
        # An independent task reviewer must promote it using a different
        # audited admission workflow; this queue NEVER promotes anything.
        return False


def rank_candidate(record: dict) -> ReviewLead | None:
    """Rank *source-path candidates* for human inspection; not acceptance."""
    if record.get("triage_status") != "production_source_path_detected":
        return None
    prod = record.get("production_files")
    tests = record.get("test_files")
    if not isinstance(prod, list) or not prod or not isinstance(tests, list):
        raise ValueError("source candidate has inconsistent production/test paths")
    reasons = ["source_path_only", "ai_line_authorship_unverified",
               "file_rights_not_cleared", "oracle_not_qualified"]
    known_license = record.get("repository_license_spdx") not in LICENSE_UNKNOWN
    if not known_license:
        reasons.append("repository_spdx_unknown")
    if not tests:
        reasons.append("no_changed_test_path")
    if record.get("fork"):
        reasons.append("fork_lineage_review")
    paths = prod + tests
    if any(any(w in path.lower() for w in SENSITIVE_FRAGMENTS) for path in paths):
        reasons.append("security_sensitive_path_manual_review")
    if any(any(w in path.lower() for w in GENERATED_OR_DATA_HINTS)
           for path in prod):
        reasons.append("generated_or_data_content_review")
    file_count = record.get("github_changed_file_count")
    if type(file_count) is not int or file_count < len(prod) + len(tests):
        raise ValueError("missing or implausible changed-file count")
    if file_count > 25:
        reasons.append("large_or_bulk_change")
    if record.get("changed_file_list_complete") is False:
        reasons.append("incomplete_github_changed_file_list")
    good = (known_license and bool(tests) and not record.get("fork")
            and file_count <= 25
            and not any(x in reasons for x in (
                "security_sensitive_path_manual_review",
                "generated_or_data_content_review",
                "incomplete_github_changed_file_list",
            )))
    return ReviewLead(
        candidate_id=int(record["candidate_id"]),
        repository=str(record["repository"]),
        url=str(record["pr_url"]),
        language=str(record["discovery_language"]),
        priority_class="first_pass_manual_review" if good
                       else "second_pass_manual_review",
        reasons=tuple(reasons), production_path_count=len(prod),
        test_path_count=len(tests),
    )


def select_review_queue(records: Sequence[dict]) -> list[ReviewLead]:
    results = []
    seen = set()
    for record in records:
        idx = record.get("candidate_id")
        if idx in seen:
            raise ValueError("duplicate review candidate")
        seen.add(idx)
        lead = rank_candidate(record)
        if lead is not None:
            results.append(lead)
    return sorted(
        results,
        key=lambda x: (
            0 if x.priority_class == "first_pass_manual_review" else 1,
            0 if x.test_path_count else 1,
            x.production_path_count, x.candidate_id,
        )
    )
