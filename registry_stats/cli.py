from __future__ import annotations

import argparse
import sys

from registry_stats.runner import collect_from_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect OCI registry download statistics")
    parser.add_argument(
        "--config",
        default="registry-stats.yaml",
        help="Path to registry-stats.yaml",
    )
    args = parser.parse_args(argv)
    return collect_from_config(args.config)


if __name__ == "__main__":
    sys.exit(main())
