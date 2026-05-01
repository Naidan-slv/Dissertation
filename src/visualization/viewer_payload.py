"""Compose the payload pieces needed by the interactive viewer.

The surface and contour-tree overlays are built separately, but the slider needs
both to agree on the same isovalue. This module keeps that wiring in one place.
"""

from src.visualization.contour_tree_payload import build_contour_tree_payload
from src.visualization.isosurface_payload import extract_grid_mesh_payload

VIEWER_PAYLOAD_SCHEMA_VERSION = "viewer-payload-v1"


def _summary(isovalue, isosurface, contour_tree):
    """Return the small counters a viewer/debug panel can show."""
    active_edges = [edge for edge in contour_tree["edges"] if edge["active"]]
    return {
        "isovalue": float(isovalue),
        "triangle_count": isosurface["triangle_count"],
        "active_arc_count": len(active_edges),
        "node_count": len(contour_tree["nodes"]),
        "edge_count": len(contour_tree["edges"]),
    }


def build_viewer_payload(mesh, supernodes, superarcs, isovalue, dataset_name=None, value_fn=None):
    """Return linked isosurface and contour-tree payloads for one isovalue."""
    if value_fn is None:
        value_fn = mesh.value

    isosurface = extract_grid_mesh_payload(
        mesh,
        isovalue,
        dataset_name=dataset_name,
    )
    contour_tree = build_contour_tree_payload(
        supernodes,
        superarcs,
        value_fn,
        isovalue=isovalue,
    )

    return {
        "schema_version": VIEWER_PAYLOAD_SCHEMA_VERSION,
        "payload_type": "combined-viewer",
        "dataset_name": dataset_name,
        "isovalue": float(isovalue),
        "component_mapping": "interval-only",
        "summary": _summary(isovalue, isosurface, contour_tree),
        "isosurface": isosurface,
        "contour_tree": contour_tree,
    }
