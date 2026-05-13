"""Command line entry point for the Klacansky interactive viewer."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.visualization.dataset_viewer import show_klacansky_viewer, show_raw_file_viewer


def build_parser():
    parser = argparse.ArgumentParser(description="Open an interactive Klacansky volume viewer.")
    parser.add_argument("dataset", nargs="?", default="fuel")
    parser.add_argument("--file", "-f", type=str, help="Path to a .raw file outside datasets.yaml")
    parser.add_argument("--shape", "-s", type=int, nargs=3, metavar=("W", "H", "D"), help="Dimensions for --file input")
    parser.add_argument("--dtype", "-d", default="uint8", help="NumPy dtype for --file input (default: uint8)")
    parser.add_argument("--isovalue", type=float, default=None)
    parser.add_argument("--no-freudenthal", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.file:
        if args.shape is None:
            raise SystemExit("--shape W H D is required when using --file")
        return show_raw_file_viewer(
            args.file,
            tuple(args.shape),
            dtype=args.dtype,
            initial_isovalue=args.isovalue,
            freudenthal=not args.no_freudenthal,
        )

    return show_klacansky_viewer(
        args.dataset,
        initial_isovalue=args.isovalue,
        freudenthal=not args.no_freudenthal,
    )


if __name__ == "__main__":
    main()
