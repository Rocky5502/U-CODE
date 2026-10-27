"""Verify metadata-only lineage graph integrity in GitHub CI or after ZIP extraction."""
import argparse
import json
from pathlib import Path

from ucode.lineage_graph_verify import verify_lineage_review


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(verify_lineage_review(args.folder),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
