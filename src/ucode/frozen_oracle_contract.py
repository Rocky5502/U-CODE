"""Evaluator-only declared oracle fingerprints for every frozen study task.

This is an OFFLINE STRUCTURAL CONTRACT, not an authenticated time-stamp,
independently sealed test oracle, or executable task approval. The independent
runner must separately protect the manifest before any outcome is observed.
Do not include the manifest or hidden oracle artifacts in agent/policy inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_STAGE = "DECLARED_PREOUTCOME_ORACLE_IDENTITIES_NOT_AUTHENTICATED"


@dataclass(frozen=True)
class FrozenOracleManifest:
    """One expected evaluator oracle digest per task, even if nobody releases.

    Authenticity and chronological freezing are outside this Python class.
    Copying a digest from a verdict after the experiment is NOT precommitment.
    """

    task_oracles: tuple[tuple[str, str], ...]
    stage: str = _STAGE

    def __post_init__(self) -> None:
        if self.stage != _STAGE:
            raise ValueError("declared manifest cannot certify oracle authenticity")
        if (type(self.task_oracles) is not tuple
                or not 1 <= len(self.task_oracles) <= 10000):
            raise ValueError("bounded immutable task-oracle tuple required")
        seen = set()
        for row in self.task_oracles:
            if type(row) is not tuple or len(row) != 2:
                raise ValueError("one immutable task/digest pair per row required")
            task, digest = row
            if (type(task) is not str or not task.strip()
                    or len(task) > 256 or any(ord(x) < 32 for x in task)):
                raise ValueError("bounded printable task ID required")
            if task in seen:
                raise ValueError("duplicate task oracle commitment")
            seen.add(task)
            if type(digest) is not str or _SHA256.fullmatch(digest) is None:
                raise ValueError("task oracle fingerprint must be lowercase SHA256")

    def require_exact_tasks(self, task_ids: Sequence[str]) -> dict[str, str]:
        """Return immutable declaration as lookup after full matrix alignment."""
        if type(task_ids) not in (tuple, list):
            raise ValueError("frozen task identity sequence required")
        expected = list(task_ids)
        if len(expected) != len(set(expected)):
            raise ValueError("duplicate study task identity")
        indexed = dict(self.task_oracles)
        if set(indexed) != set(expected):
            raise ValueError(
                "frozen oracle manifest must cover every assigned task, including all-abstain tasks"
            )
        return indexed
