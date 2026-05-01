"""Compose the payload pieces needed by the interactive viewer.

The surface and contour-tree overlays are built separately, but the slider needs
both to agree on the same isovalue. This module keeps that wiring in one place.
"""

from src.visualization.contour_tree_payload import build_contour_tree_payload
from src.visualization.isosurface_payload import extract_grid_mesh_payload

VIEWER_COMBINED_PAYLOAD_SCHEMA_VERSION = "combined-viewer-payload-v1"


def build_viewer_payload(mesh, supernodes, superarcs, isovalue, dataset_name=None, value_fn=None):
    """Return linked isosurface and contour-tree payloads for one isovalue."""
    if value_fn is None:
        value_fn = mesh.value

    return {
        "schema_version": VIEWER_COMBINED_PAYLOAD_SCHEMA_VERSION,
        "dataset_name": dataset_name,
        "isovalue": float(isovalue),
        "isosurface": extract_grid_mesh_payload(
            mesh,
            isovalue,
            dataset_name=dataset_name,
        ),
        "contour_tree": build_contour_tree_payload(
            supernodes,
            superarcs,
            value_fn,
            isovalue=isovalue,
        ),
    }
