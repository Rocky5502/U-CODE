"""Export twelve reviewer-only evidence packets (NO executable task grants)."""
import argparse
import json
from pathlib import Path

from ucode.pending_review_packets import export_pending_review_packets


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path,
                   default=Path("dist/ucode-admission-review-only"))
    args = p.parse_args(argv)
    result = export_pending_review_packets(args.output_dir)
    print(json.dumps({
        "stage": result["status"],
        "reviewer_packets": result["reviewer_packets"],
        "pending_eight_gate_checks": result["pending_eight_gate_checks"],
        "approved_executable_tasks": result["scientifically_admitted_executable_tasks"],
    }, indent=2))
    print("REVIEW PACKETS ONLY; NO AUTHOR APPROVAL OR TEST EXECUTION.")


if __name__ == "__main__":
    main()
