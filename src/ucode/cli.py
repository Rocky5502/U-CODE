"""CLI: explicitly label experiments, metadata triage, and synthetic smoke tests."""
import argparse
import json
from dataclasses import asdict

from .audit import audit_manifest
from .simulation import run_synthetic_episode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ucode", description="U-CODE research scaffold; no scientific findings yet")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("simulate", help="Synthetic smoke test ONLY")
    demo.add_argument("--policy", default="uncertainty_pareto",
                      choices=["uncertainty_pareto", "random", "cost_first",
                               "fixed_test", "quality_only"])
    demo.add_argument("--seed", type=int, default=7)
    demo.add_argument("--budget", type=float, default=9)
    audit = sub.add_parser("audit", help="Read-only PR metadata triage; no code runs")
    audit.add_argument("--input", default="data/discovery/agent_pr_candidates_120.csv")
    audit.add_argument("--output", default="data/derived/pr_audit.jsonl")
    audit.add_argument("--limit", type=int, default=0,
                       help="0=all within chosen cohort; start with a small pilot")
    audit.add_argument("--per-language", type=int, default=0,
                       help="sample N in each original GitHub query-language group")
    audit.add_argument("--language-offset", type=int, default=0,
                       help="0-based starting position within each language group")
    args = parser.parse_args(argv)
    if args.command == "simulate":
        result = asdict(run_synthetic_episode(args.policy, args.seed, args.budget))
        result["warning"] = "SYNTHETIC ONLY; not evidence of accuracy or search gains"
    else:
        result = audit_manifest(args.input, args.output, args.limit,
                                args.per_language, args.language_offset)
        result["warning"] = "PR metadata triage ONLY; test/AI attribution not verified"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
