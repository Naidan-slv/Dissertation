"""Export repeatable JSON assets for the interactive viewer."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree
from src.input.ingest import load_raw_dataset


def build_parser():
    """Return the command line parser for viewer asset export."""
    raise NotImplementedError()


def asset_paths(output_dir, dataset_name):
    """Return the payload and manifest paths for a dataset export."""
    raise NotImplementedError()


def build_asset_manifest(dataset_name, isovalue, threshold, payload_path, manifest_path, command):
    """Return JSON-serialisable manifest metadata for an export."""
    raise NotImplementedError()


def export_viewer_assets(
    dataset_name,
    isovalue=None,
    threshold=None,
    output_dir="output/viewer",
    loader=load_raw_dataset,
    contour_tree_fn=compute_unaugmented_contour_tree,
    command=None,
):
    """Build and write viewer payload and manifest JSON files."""
    raise NotImplementedError()


def main(argv=None):
    """CLI entry point."""
    raise NotImplementedError()


if __name__ == "__main__":
    main()