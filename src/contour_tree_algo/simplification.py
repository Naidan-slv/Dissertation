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

import heapq
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


def collapse_all_regular_vertices(state: MutableTree) -> None:
    """Collapse all currently regular vertices (Carr Algorithm 11.2 Rule I)."""
    candidates = [vertex for vertex in list(state.adj) if is_regular(state, vertex)]
    while candidates:
        vertex = candidates.pop()
        if not is_regular(state, vertex):
            continue
        new_edge_id = vertex_collapse(state, vertex)
        new_edge = state.edges[new_edge_id]
        candidates.extend(endpoint for endpoint in (new_edge.u, new_edge.v) if is_regular(state, endpoint))


def simplify_contour_tree(
    tree: Iterable[Edge],
    values: Mapping[int, float],
    measures: Mapping[Edge, ArcMeasure] | None = None,
    mode: Mode = "height",
    threshold: float | None = None,
    target_edges: int | None = None,
) -> SimplificationResult:
    """Simplify a contour tree using Carr-style collapses and leaf pruning."""
    if mode not in ("height", "measure"):
        raise ValueError(f"unknown simplification mode: {mode}")

    state = build_mutable_tree(tree, values, measures)
    collapse_all_regular_vertices(state)

    if threshold is None and target_edges is None:
        return SimplificationResult(
            edges=active_edges(state),
            collapse_record=state.collapse_record,
            removed_edges=state.removed_edges,
            mode=mode,
            threshold=threshold,
            target_edges=target_edges,
        )

    queue: list[tuple[float, tuple[float, int], int, int]] = []

    def push_leaf(edge_id: int) -> None:
        info = leaf_info(state, edge_id)
        if info is None:
            return
        leaf, interior = info
        if not is_prunable_leaf(state, leaf, interior):
            return
        priority = edge_priority(state, edge_id, mode=mode, leaf=leaf, interior=interior)
        heapq.heappush(queue, (priority, scalar_order(state, leaf), leaf, edge_id))

    for edge_id in active_edge_ids(state):
        push_leaf(edge_id)

    while queue:
        if target_edges is not None and len(active_edge_ids(state)) <= target_edges:
            break

        _, _, _, edge_id = heapq.heappop(queue)
        info = leaf_info(state, edge_id)
        if info is None:
            continue
        leaf, interior = info
        if not is_prunable_leaf(state, leaf, interior):
            continue

        priority = edge_priority(state, edge_id, mode=mode, leaf=leaf, interior=interior)
        if threshold is not None and priority > threshold:
            break

        changed_vertex = leaf_prune(state, edge_id, priority=priority)
        for incident_edge_id in active_incident_edges(state, changed_vertex):
            push_leaf(incident_edge_id)

    return SimplificationResult(
        edges=active_edges(state),
        collapse_record=state.collapse_record,
        removed_edges=state.removed_edges,
        mode=mode,
        threshold=threshold,
        target_edges=target_edges,
    )


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
        if measures and key in measures and hasattr(measures[key], "node_count"):
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
    incident = active_incident_edges(state, vertex)
    if len(incident) != 2 or not is_regular(state, vertex):
        raise ValueError(f"vertex {vertex} is not regular")

    first_id, second_id = incident
    first = state.edges[first_id]
    second = state.edges[second_id]
    a = other_endpoint(first, vertex)
    b = other_endpoint(second, vertex)
    upper, lower = sorted((a, b), key=lambda v: scalar_order(state, v), reverse=True)

    upper_edge_id = first_id if other_endpoint(first, vertex) == upper else second_id
    lower_edge_id = first_id if other_endpoint(first, vertex) == lower else second_id
    upper_edge = state.edges[upper_edge_id]
    lower_edge = state.edges[lower_edge_id]

    for edge_id in (upper_edge_id, lower_edge_id):
        edge = state.edges[edge_id]
        edge.active = False
        edge.already_collapsed = True
        state.adj[edge.u].discard(edge_id)
        state.adj[edge.v].discard(edge_id)

    new_edge_id = state.next_edge_id
    state.next_edge_id += 1
    new_edge = MutableEdge(
        id=new_edge_id,
        u=upper,
        v=lower,
        upper_arc=upper_edge_id,
        lower_arc=lower_edge_id,
        old_edges=(upper_edge_id, lower_edge_id),
        up_weight=upper_edge.up_weight,
        down_weight=lower_edge.down_weight,
    )
    state.edges[new_edge_id] = new_edge
    state.adj[upper].add(new_edge_id)
    state.adj[lower].add(new_edge_id)
    state.adj[vertex].clear()
    state.collapse_record.insert(0, CollapseRecord(
        kind="vertex_collapse",
        removed_edges=(upper_edge_id, lower_edge_id),
        new_edge=new_edge_id,
        collapsed_vertex=vertex,
    ))
    return new_edge_id


def edge_priority(
    state: MutableTree,
    edge_id: int,
    mode: Mode = "height",
    leaf: int | None = None,
    interior: int | None = None,
) -> float:
    """Return the pruning priority for a leaf edge."""
    if leaf is None or interior is None:
        info = leaf_info(state, edge_id)
        if info is None:
            raise ValueError(f"edge {edge_id} is not an active leaf edge")
        leaf, interior = info

    if mode == "height":
        return abs(float(state.values[leaf]) - float(state.values[interior]))

    if mode == "measure":
        edge = state.edges[edge_id]
        weight = edge.up_weight
        if scalar_order(state, leaf) < scalar_order(state, interior):
            weight = edge.down_weight
        if weight != 0.0:
            return float(weight)

        key = _measure_key(edge.u, edge.v)
        if state.measures and key in state.measures and hasattr(state.measures[key], "node_count"):
            return float(state.measures[key].node_count)

        return abs(float(state.values[leaf]) - float(state.values[interior]))

    raise ValueError(f"unknown simplification mode: {mode}")


def leaf_prune(state: MutableTree, edge_id: int, priority: float | None = None) -> int:
    """Remove a prunable leaf edge and return the interior vertex."""
    info = leaf_info(state, edge_id)
    if info is None:
        raise ValueError(f"edge {edge_id} is not an active leaf edge")

    leaf, interior = info
    if not is_prunable_leaf(state, leaf, interior):
        raise ValueError(f"leaf {leaf} is not prunable from interior {interior}")

    edge = state.edges[edge_id]
    edge.active = False
    state.adj[edge.u].discard(edge_id)
    state.adj[edge.v].discard(edge_id)
    state.removed_edges.append(edge_id)
    state.collapse_record.insert(0, CollapseRecord(
        kind="leaf_prune",
        removed_edges=(edge_id,),
        leaf=leaf,
        interior=interior,
        priority=priority,
    ))
    return interior
