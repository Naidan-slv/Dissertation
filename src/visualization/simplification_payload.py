"""Viewer payload helpers for Carr-style simplification context.

References: Carr (2004) Ch. 11 for collapse records and Weber et al. (2007)
for the display motivation. This remains tree/context display only.
"""

from src.contour_tree_algo.simplification import simplify_contour_tree
from src.visualization.contour_tree_payload import build_contour_tree_payload

SIMPLIFICATION_PAYLOAD_SCHEMA_VERSION = "viewer-payload-v1"


def _tree_nodes(supernodes, superarcs):
    nodes = set(supernodes)
    for u, v in superarcs:
        nodes.add(u)
        nodes.add(v)
    return sorted(nodes)


def _record_payload(record):
    return {
        "kind": record.kind,
        "removed_edges": list(record.removed_edges),
        "new_edge": record.new_edge,
        "leaf": record.leaf,
        "interior": record.interior,
        "collapsed_vertex": record.collapsed_vertex,
        "priority": record.priority,
    }


def build_simplification_payload(
    supernodes,
    superarcs,
    value_fn,
    isovalue=None,
    mode="height",
    threshold=None,
    target_edges=None,
):
    nodes = _tree_nodes(supernodes, superarcs)
    values = {node: float(value_fn(node)) for node in nodes}
    result = simplify_contour_tree(
        superarcs,
        values,
        mode=mode,
        threshold=threshold,
        target_edges=target_edges,
    )
    simplified_nodes = _tree_nodes([], result.edges)
    simplified_tree = build_contour_tree_payload(
        simplified_nodes,
        result.edges,
        values.__getitem__,
        isovalue=isovalue,
    )
    active_edges = [edge for edge in simplified_tree["edges"] if edge["active_at_isovalue"]]

    return {
        "schema_version": SIMPLIFICATION_PAYLOAD_SCHEMA_VERSION,
        "mode": result.mode,
        "threshold": result.threshold,
        "target_edge_count": result.target_edges,
        "component_mapping": "interval-only",
        "original_edge_count": len(superarcs),
        "simplified_edge_count": len(result.edges),
        "active_edge_count": len(active_edges),
        "collapse_record_count": len(result.collapse_record),
        "collapse_records": [_record_payload(record) for record in result.collapse_record],
        "simplified_tree": simplified_tree,
    }
