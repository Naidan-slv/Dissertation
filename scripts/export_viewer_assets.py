"""Export repeatable JSON assets for the interactive viewer."""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree
from src.input.ingest import load_raw_dataset
from src.visualization.dot_export import ct_to_dot, save_dot
from src.visualization.viewer_payload import build_viewer_payload

VIEWER_ASSETS_MANIFEST_SCHEMA_VERSION = "viewer-assets-manifest-v1"


def _safe_dataset_name(dataset_name):
    """Return a filesystem-safe dataset stem."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(dataset_name)).strip("_") or "dataset"


def _mesh_scalar_range(mesh):
    values = [mesh.value(v) for v in mesh.vertices()]
    if not values:
        raise ValueError("viewer asset export needs at least one mesh vertex")
    return float(min(values)), float(max(values))


def _default_isovalue(mesh):
    low, high = _mesh_scalar_range(mesh)
    return (low + high) / 2.0


def _write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_parser():
    """Return the command line parser for viewer asset export."""
    parser = argparse.ArgumentParser(
        description="Export repeatable interactive-viewer JSON assets."
    )
    parser.add_argument("dataset", nargs="?", default="fuel")
    parser.add_argument("--isovalue", type=float, default=None)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--output-dir", default="output/viewer")
    parser.add_argument("--no-freudenthal", action="store_true")
    return parser


def asset_paths(output_dir, dataset_name):
    """Return the payload and manifest paths for a dataset export."""
    output_dir = Path(output_dir)
    dataset_stem = _safe_dataset_name(dataset_name)
    return (
        output_dir / f"{dataset_stem}_viewer_payload.json",
        output_dir / f"{dataset_stem}_viewer_manifest.json",
        output_dir / f"{dataset_stem}_contour_tree.dot",
    )


def build_asset_manifest(
    dataset_name,
    isovalue,
    threshold,
    payload_path,
    manifest_path,
    command,
    dot_path=None,
    screenshot_path=None,
):
    """Return JSON-serialisable manifest metadata for an export."""
    return {
        "schema_version": VIEWER_ASSETS_MANIFEST_SCHEMA_VERSION,
        "dataset": dataset_name,
        "isovalue": float(isovalue),
        "simplification_threshold": None if threshold is None else float(threshold),
        "component_mapping": "interval-only",
        "outputs": {
            "viewer_payload": str(payload_path),
            "manifest": str(manifest_path),
            "dot_graph": None if dot_path is None else str(dot_path),
            "screenshot": None if screenshot_path is None else str(screenshot_path),
        },
        "command": list(command) if command is not None else None,
        "paper_basis": {
            "contour_tree": "Carr contour-tree construction and simplification context.",
            "mesh": "Freudenthal tetrahedralization for regular 3D scalar grids.",
            "isosurface": "marching tetrahedra isosurface extraction.",
            "viewer_link": "Weber-style linked-viewer motivation, with interval-only component mapping here.",
        },
    }


def export_viewer_assets(
    dataset_name,
    isovalue=None,
    threshold=None,
    output_dir="output/viewer",
    freudenthal=True,
    loader=load_raw_dataset,
    contour_tree_fn=compute_unaugmented_contour_tree,
    command=None,
):
    """Build and write viewer payload and manifest JSON files."""
    mesh = loader(dataset_name, freudenthal=freudenthal)
    supernodes, superarcs = contour_tree_fn(mesh)

    if isovalue is None:
        isovalue = _default_isovalue(mesh)

    simplification = None
    if threshold is not None:
        simplification = {"threshold": float(threshold)}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_path, manifest_path, dot_path = asset_paths(output_dir, dataset_name)

    payload = build_viewer_payload(
        mesh=mesh,
        supernodes=list(supernodes),
        superarcs=list(superarcs),
        isovalue=float(isovalue),
        dataset_name=dataset_name,
        simplification=simplification,
    )
    dot_text = ct_to_dot(
        list(supernodes),
        list(superarcs),
        mesh.value,
        isovalue=float(isovalue),
    )
    manifest = build_asset_manifest(
        dataset_name=dataset_name,
        isovalue=isovalue,
        threshold=threshold,
        payload_path=payload_path,
        manifest_path=manifest_path,
        command=command,
        dot_path=dot_path,
    )

    _write_json(payload_path, payload)
    save_dot(dot_text, str(dot_path))
    _write_json(manifest_path, manifest)

    return {"viewer_payload": payload_path, "manifest": manifest_path, "dot_graph": dot_path}


def main(argv=None):
    """CLI entry point."""
    raw_args = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(raw_args)
    return export_viewer_assets(
        dataset_name=args.dataset,
        isovalue=args.isovalue,
        threshold=args.threshold,
        output_dir=args.output_dir,
        freudenthal=not args.no_freudenthal,
        command=["scripts/export_viewer_assets.py", *raw_args],
    )


if __name__ == "__main__":
    main()