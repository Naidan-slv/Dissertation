"""Build JSON-style payloads for contour-tree viewer overlays.

This keeps the tree data separate from Graphviz and PyVista. The viewer can use
it later to highlight which superarc contains the current isovalue.
"""

from src.visualization.dot_export import classify_nodes

CONTOUR_TREE_PAYLOAD_SCHEMA_VERSION = "contour-tree-payload-v1"


def _edge_range(u, v, value_fn):
    low = float(min(value_fn(u), value_fn(v)))
    high = float(max(value_fn(u), value_fn(v)))
    return [low, high]


def _is_active(value_range, isovalue):
    if isovalue is None:
        return False

    low, high = value_range
    return low <= float(isovalue) <= high


def build_contour_tree_payload(supernodes, superarcs, value_fn, isovalue=None):
    """Return nodes and superarcs in a viewer-friendly shape."""
    labels = classify_nodes(supernodes, superarcs, value_fn)
    nodes = [
        {"id": int(node), "value": float(value_fn(node)), "kind": labels[node]}
        for node in supernodes
    ]

    edges = []
    for u, v in superarcs:
        value_range = _edge_range(u, v, value_fn)
        edges.append(
            {
                "source": int(u),
                "target": int(v),
                "value_range": value_range,
                "active": _is_active(value_range, isovalue),
            }
        )

    return {
        "schema_version": CONTOUR_TREE_PAYLOAD_SCHEMA_VERSION,
        "isovalue": None if isovalue is None else float(isovalue),
        "nodes": nodes,
        "edges": edges,
    }
