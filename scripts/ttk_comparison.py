"""Fallback helpers for comparing project contour-tree counts with TTK output."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_parser():
    """Return the command line parser for TTK comparison summaries."""
    raise NotImplementedError()


def ttk_available(executable="ttkContourForests"):
    """Return whether a TTK executable is available on PATH."""
    raise NotImplementedError()


def parse_ttk_summary(text):
    """Parse a saved TTK CSV/text summary into normalised counts."""
    raise NotImplementedError()


def load_ttk_summary(path):
    """Load and parse a saved TTK summary file."""
    raise NotImplementedError()


def project_summary_from_tree(supernodes, superarcs):
    """Return project contour-tree counts in the same shape as TTK counts."""
    raise NotImplementedError()


def compare_summaries(project_summary, ttk_summary):
    """Return per-metric project-vs-TTK deltas."""
    raise NotImplementedError()


def main(argv=None):
    """CLI entry point."""
    raise NotImplementedError()


if __name__ == "__main__":
    main()