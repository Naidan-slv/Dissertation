"""Command line entry point for the Klacansky interactive viewer."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.visualization.dataset_viewer import show_klacansky_viewer


def build_parser():
    parser = argparse.ArgumentParser(description="Open an interactive Klacansky volume viewer.")
    parser.add_argument("dataset", nargs="?", default="fuel")
    parser.add_argument("--isovalue", type=float, default=None)
    parser.add_argument("--no-freudenthal", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return show_klacansky_viewer(
        args.dataset,
        initial_isovalue=args.isovalue,
        freudenthal=not args.no_freudenthal,
    )


if __name__ == "__main__":
    main()
