"""Fail-closed, source-free policy input projection; NOT task admission.

Never feed reviewer-only PR dossiers to this adapter. Text provenance and
absence of prompt-injection or solution leakage still require external review.
"""
from dataclasses import dataclass
from hashlib import sha256
import re
import unicodedata
from typing import Mapping

_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset(("repository", "base_sha", "prefixed_spec", "spec_sha256"))


@dataclass(frozen=True)
class AgentTaskView:
    repository: str
    base_sha: str
    prefixed_spec: str
    spec_sha256: str

    def __post_init__(self):
        if (type(self.repository) is not str or not _REPO.fullmatch(self.repository)
                or any(x in (".", "..") for x in self.repository.split("/"))):
            raise ValueError("invalid repository identity")
        if type(self.base_sha) is not str or not _SHA40.fullmatch(self.base_sha):
            raise ValueError("invalid immutable base SHA")
        if (type(self.prefixed_spec) is not str or not self.prefixed_spec.strip()
                or len(self.prefixed_spec.encode("utf-8")) > 65536):
            raise ValueError("invalid bounded pre-fix specification")
        # Human-language and ordinary multiline task specs are permitted.
        # C0/C1 controls, bidirectional override/zero-width format chars,
        # and unpaired surrogates can conceal or rewrite policy-visible text.
        # This is text-shape validation, NOT protection from prompt injection.
        if any(unicodedata.category(ch) in ("Cc", "Cf", "Cs")
               and ch not in ("\n", "\t") for ch in self.prefixed_spec):
            raise ValueError("policy-visible specification contains unsafe control or formatting character")
        if type(self.spec_sha256) is not str or not _SHA256.fullmatch(self.spec_sha256):
            raise ValueError("invalid specification digest")
        if sha256(self.prefixed_spec.encode("utf-8")).hexdigest() != self.spec_sha256:
            raise ValueError("pre-fix specification digest mismatch")

    def to_policy_input(self) -> str:
        """Deterministic view, not evidence that the specification is authentic."""
        return ("Repository: " + self.repository + "\nBase commit: " +
                self.base_sha + "\nPre-fix task specification:\n" + self.prefixed_spec)


def parse_agent_task_view(record: Mapping) -> AgentTaskView:
    """Exact allowlist excludes head/merge SHAs, PR notes, tests and oracles.

    This is intentionally incompatible with admission dossier dictionaries.
    """
    if not isinstance(record, Mapping) or set(record) != _FIELDS:
        raise ValueError("policy view must contain exactly four safe fields")
    return AgentTaskView(**{key: record[key] for key in _FIELDS})
