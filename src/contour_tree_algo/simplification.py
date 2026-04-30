"""
Contour-tree simplification by vertex collapse and leaf pruning.

References:
- Carr (2004) Ch. 11, Algorithms 11.1 and 11.2.
- Carr (2004) Ch. 10, §10.8 for approximate local measures.
- Takahashi, Takeshima and Fujishiro (2004) §3.5 for height-difference pruning.
- Edelsbrunner, Letscher and Zomorodian (2002) §3 for persistence motivation.

Height mode is contour-tree leaf-to-saddle height pruning, not full persistent homology.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Literal, Mapping, Tuple

from src.contour_tree_algo.measures import ArcMeasure


Edge = Tuple[int, int]
Mode = Literal["height", "measure"]


@dataclass
class MutableEdge:
    """Mutable contour-tree edge used during simplification."""

    id: int
    u: int
    v: int
    active: bool = True
    already_collapsed: bool = False
    upper_arc: int | None = None
    lower_arc: int | None = None
    old_edges: Tuple[int, ...] = ()
    up_weight: float = 0.0
    down_weight: float = 0.0


@dataclass(frozen=True)
class CollapseRecord:
    """One simplification operation."""

    kind: Literal["vertex_collapse", "leaf_prune"]
    removed_edges: Tuple[int, ...]
    new_edge: int | None = None
    leaf: int | None = None
    interior: int | None = None
    collapsed_vertex: int | None = None
    priority: float | None = None


@dataclass
class SimplificationResult:
    """Simplified tree and operation log."""

    edges: list[Edge]
    collapse_record: list[CollapseRecord]
    removed_edges: list[int]
    mode: Mode
    threshold: float | None
    target_edges: int | None


@dataclass
class MutableTree:
    """Mutable tree state for Carr Algorithm 11.2."""

    edges: Dict[int, MutableEdge]
    adj: Dict[int, set[int]]
    values: Mapping[int, float]
    measures: Mapping[Edge, ArcMeasure] | None = None
    next_edge_id: int = 0
    collapse_record: list[CollapseRecord] = field(default_factory=list)
    removed_edges: list[int] = field(default_factory=list)


def simplify_contour_tree(
    tree: Iterable[Edge],
    values: Mapping[int, float],
    measures: Mapping[Edge, ArcMeasure] | None = None,
    mode: Mode = "height",
    threshold: float | None = None,
    target_edges: int | None = None,
) -> SimplificationResult:
    """Simplify a contour tree using Carr-style collapses and leaf pruning."""
    raise NotImplementedError


def build_mutable_tree(
    tree: Iterable[Edge],
    values: Mapping[int, float],
    measures: Mapping[Edge, ArcMeasure] | None = None,
) -> MutableTree:
    """Build mutable edge and adjacency records."""
    edges: Dict[int, MutableEdge] = {}
    adj: Dict[int, set[int]] = defaultdict(set)

    for edge_id, (u, v) in enumerate(tree):
        edge = MutableEdge(id=edge_id, u=u, v=v)
        key = _measure_key(u, v)
        if measures and key in measures:
            measure = measures[key]
            edge.up_weight = float(measure.node_count)
            edge.down_weight = float(measure.node_count)
        edges[edge_id] = edge
        adj[u].add(edge_id)
        adj[v].add(edge_id)

    return MutableTree(
        edges=edges,
        adj=adj,
        values=values,
        measures=measures,
        next_edge_id=len(edges),
    )


def scalar_order(state: MutableTree, vertex: int) -> tuple[float, int]:
    """Return deterministic scalar order for a vertex."""
    return (float(state.values[vertex]), vertex)


def active_edge_ids(state: MutableTree) -> list[int]:
    """Return active edge ids."""
    return [edge_id for edge_id, edge in state.edges.items() if edge.active]


def active_edges(state: MutableTree) -> list[Edge]:
    """Return active tree edges as endpoint pairs."""
    return [(edge.u, edge.v) for edge in state.edges.values() if edge.active]


def other_endpoint(edge: MutableEdge, vertex: int) -> int:
    """Return the endpoint of edge opposite vertex."""
    if edge.u == vertex:
        return edge.v
    if edge.v == vertex:
        return edge.u
    raise ValueError(f"vertex {vertex} is not incident to edge {edge.id}")


def active_incident_edges(state: MutableTree, vertex: int) -> list[int]:
    """Return active edge ids incident to vertex."""
    return [edge_id for edge_id in state.adj[vertex] if state.edges[edge_id].active]


def up_degree(state: MutableTree, vertex: int) -> int:
    """Count active incident edges to higher neighbours."""
    count = 0
    for edge_id in active_incident_edges(state, vertex):
        nbr = other_endpoint(state.edges[edge_id], vertex)
        if scalar_order(state, nbr) > scalar_order(state, vertex):
            count += 1
    return count


def down_degree(state: MutableTree, vertex: int) -> int:
    """Count active incident edges to lower neighbours."""
    count = 0
    for edge_id in active_incident_edges(state, vertex):
        nbr = other_endpoint(state.edges[edge_id], vertex)
        if scalar_order(state, nbr) < scalar_order(state, vertex):
            count += 1
    return count


def is_regular(state: MutableTree, vertex: int) -> bool:
    """Return True when vertex has one up-edge and one down-edge."""
    return up_degree(state, vertex) == 1 and down_degree(state, vertex) == 1


def is_leaf(state: MutableTree, vertex: int) -> bool:
    """Return True when vertex has one active incident edge."""
    return len(active_incident_edges(state, vertex)) == 1


def _measure_key(u: int, v: int) -> Edge:
    return tuple(sorted((u, v)))


def leaf_info(state: MutableTree, edge_id: int) -> tuple[int, int] | None:
    """Return (leaf, interior) for a leaf edge, or None."""
    edge = state.edges[edge_id]
    if not edge.active:
        return None

    u_is_leaf = is_leaf(state, edge.u)
    v_is_leaf = is_leaf(state, edge.v)
    if u_is_leaf and not v_is_leaf:
        return edge.u, edge.v
    if v_is_leaf and not u_is_leaf:
        return edge.v, edge.u
    return None


def is_prunable_leaf(state: MutableTree, leaf: int, interior: int) -> bool:
    """Return True when Carr Definition 11.2 allows pruning this leaf."""
    if scalar_order(state, leaf) > scalar_order(state, interior):
        return up_degree(state, interior) > 1
    return down_degree(state, interior) > 1


def vertex_collapse(state: MutableTree, vertex: int) -> int:
    """Collapse a regular vertex following Carr Algorithm 11.1."""
    raise NotImplementedError


def edge_priority(
    state: MutableTree,
    edge_id: int,
    mode: Mode = "height",
    leaf: int | None = None,
    interior: int | None = None,
) -> float:
    """Return the pruning priority for a leaf edge."""
    raise NotImplementedError


def leaf_prune(state: MutableTree, edge_id: int, priority: float | None = None) -> int:
    """Remove a prunable leaf edge and return the interior vertex."""
    raise NotImplementedError
