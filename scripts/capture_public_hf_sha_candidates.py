"""U-CODE six-model *public SHA-candidate* export; offline by default.

Optional --capture-public-heads makes six public SHA-only HTTPS metadata
requests, no auth/tokens, weight downloads, model inference, or GPU work.
Local CLI never approves model checkpoints, task runs, licenses or costs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucode.hub_revision_preflight import (
    build_public_revision_packet, validate_revision_candidate_packet,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-public-heads", action="store_true",
                        help="OPT IN: query six public Hub SHA metadata endpoints only; no tokens or files")
    parser.add_argument("--output", type=Path, default=None,
                        help="public-only local JSON, never raw HTTP responses")
    parser.add_argument("--require-approved", action="store_true",
                        help="strict non-admission mode: must exit 2 while externally unapproved")
    args = parser.parse_args(argv)
    packet = build_public_revision_packet(capture_public_heads=args.capture_public_heads)
    validate_revision_candidate_packet(packet)
    text = json.dumps(packet, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        output = args.output
        if output.is_symlink():
            raise ValueError("public output destination must not be symlinked")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 2 if args.require_approved else 0


if __name__ == "__main__":
    raise SystemExit(main())
