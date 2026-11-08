"""Local-only Go #43 A/B *domain rule* triage; no golds, no task admission.

No third-party code or networking. Actual completed reviewer worksheets must
remain OFF public GitHub/Actions/Overleaf and must never enter a model policy
prompt. Blank templates may be exported only to a private directory OUTSIDE
the checkout, with restrictive file permissions.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from scripts.export_go43_spec_feasibility import compile_go43_spec_feasibility
from ucode.go43_domain_decision_triage import (
    blank_go43_domain_decisions, triage_private_go43_domain_decisions,
)
from ucode.pilot_preflight import ROOT

_MAX_BYTES = 128 * 1024
_MAX_ROW = 16 * 1024


def _no_duplicates(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate private reviewer JSON field")
        result[name] = value
    return result


def _no_nonjson(text):
    raise ValueError("NaN/Infinity are not JSON reviewer evidence")


def _outside_repo(path: Path) -> Path:
    p = Path(path)
    dest = p.resolve()
    root = ROOT.resolve()
    if dest == root or root in dest.parents:
        raise ValueError("private reviewer files may not be inside public repository")
    return p


def _read_private(path: Path) -> tuple[dict, ...]:
    p = _outside_repo(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError("private reviewer input must be a local non-symlink regular file")
    # Bound reads before parsing and NEVER print raw private bytes or filenames.
    if p.stat().st_size > _MAX_BYTES:
        raise ValueError("private reviewer file too large")
    payload = p.read_bytes()
    if not payload or len(payload) > _MAX_BYTES:
        raise ValueError("empty or oversized reviewer input")
    rows = payload.splitlines()
    if len(rows) != 6:
        raise ValueError("exactly six private review records required")
    decoded = []
    for line in rows:
        if not line or len(line) > _MAX_ROW:
            raise ValueError("blank or oversized private review line")
        try:
            obj = json.loads(line.decode("utf-8"),
                object_pairs_hook=_no_duplicates, parse_constant=_no_nonjson)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError("invalid private JSON reviewer record") from exc
        if type(obj) is not dict:
            raise ValueError("private reviewer row must be an object")
        decoded.append(obj)
    return tuple(decoded)


def _export_blank_private(packet: dict, directory: Path) -> dict:
    directory = _outside_repo(directory)
    if directory.exists() or directory.is_symlink():
        raise ValueError("choose a new, non-existing private review directory")
    if not directory.parent.exists() or not directory.parent.is_dir():
        raise ValueError("private review parent directory must already exist")
    directory.mkdir(mode=0o700)
    forms = blank_go43_domain_decisions(packet)
    for slot in ("A", "B"):
        path = directory / (slot + "_go43_PENDING.jsonl")
        # No overwrite / symlink follow; private by default on POSIX.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            for row in forms[slot]:
                out.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    return {
        "stage": "TWO_BLANK_PRIVATE_REVIEW_TEMPLATES_NOT_HUMAN_REVIEWS",
        "pending_rows_each_slot": 6,
        "total_unreviewed_rows": 12,
        "reviewers_contacted": False,
        "reviewer_identity_authenticated": False,
        "independently_admitted_executable_tasks": 0,
    }


def go43_domain_review_check(
    reviewer_a: Path | None = None,
    reviewer_b: Path | None = None,
    *, template_dir: Path | None = None,
) -> dict:
    if (reviewer_a is None) != (reviewer_b is None):
        raise ValueError("both private independent reviewer files are required together")
    if template_dir is not None and reviewer_a is not None:
        raise ValueError("cannot generate blank forms and inspect completed inputs together")
    packet = compile_go43_spec_feasibility()
    if template_dir is not None:
        return _export_blank_private(packet, template_dir)
    if reviewer_a is None:
        # Strictly prospective public/CI mode: NOT real people reviewing.
        return triage_private_go43_domain_decisions(
            packet, *tuple(blank_go43_domain_decisions(packet)[slot]
                            for slot in ("A", "B")))
    a = _outside_repo(reviewer_a)
    b = _outside_repo(reviewer_b)
    if a.resolve() == b.resolve():
        raise ValueError("separate reviewer A/B files required")
    return triage_private_go43_domain_decisions(
        packet, _read_private(a), _read_private(b))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", type=Path)
    parser.add_argument("--reviewer-b", type=Path)
    parser.add_argument("--export-blank-dir", type=Path)
    parser.add_argument("--output", type=Path,
                        help="optional REDACTED output outside repo for private reviews")
    parser.add_argument("--require-adjudicated", action="store_true",
                        help="always block: external approval is unavailable here (exit 2)")
    args = parser.parse_args(argv)
    summary = go43_domain_review_check(
        args.reviewer_a, args.reviewer_b, template_dir=args.export_blank_dir)
    if args.output is not None:
        out = _outside_repo(args.output)
        if out.is_symlink() or (args.reviewer_a is not None and
               out.resolve() in (args.reviewer_a.resolve(), args.reviewer_b.resolve())):
            raise ValueError("redacted output cannot overwrite a private reviewer input")
        if not out.parent.is_dir():
            raise ValueError("redacted output parent must exist")
        # No implicit replacement of any existing status file.
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 2 if args.require_adjudicated else 0


if __name__ == "__main__":
    raise SystemExit(main())
