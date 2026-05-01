"""Tests for height-difference simplification."""

from collections import defaultdict, deque

from src.contour_tree_algo.simplification import (
    build_mutable_tree,
    edge_priority,
    simplify_contour_tree,
)


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def _assert_tree(edges):
    vertices = sorted({v for edge in edges for v in edge})
    if not vertices:
        return

    assert len(edges) == len(vertices) - 1

    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    seen = {vertices[0]}
    queue = deque([vertices[0]])
    while queue:
        v = queue.popleft()
        for nbr in adj[v]:
            if nbr not in seen:
                seen.add(nbr)
                queue.append(nbr)

    assert seen == set(vertices)


def test_height_priority_is_leaf_to_interior_difference():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0}
    state = build_mutable_tree([(8, 5), (9, 5), (5, 0)], values)

    priority = edge_priority(state, 0, mode="height", leaf=8, interior=5)

    assert priority == 3.0


def test_threshold_zero_preserves_nonzero_height_branches():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0}
    tree = [(8, 5), (9, 5), (5, 0)]

    result = simplify_contour_tree(tree, values, mode="height", threshold=0.0)

    assert _edge_set(result.edges) == _edge_set(tree)
    assert result.collapse_record == []


def test_threshold_zero_allows_regular_vertex_collapse():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    tree = [(3, 2), (2, 1)]

    result = simplify_contour_tree(tree, values, mode="height", threshold=0.0)

    assert _edge_set(result.edges) == {(1, 3)}
    assert result.collapse_record[0].kind == "vertex_collapse"
    assert result.collapse_record[0].collapsed_vertex == 2


def test_initial_regular_collapse_happens_before_leaf_pruning():
    values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
    tree = [(4, 3), (3, 2), (2, 0), (2, 1)]

    result = simplify_contour_tree(tree, values, mode="height", threshold=float("inf"))

    first_operation = result.collapse_record[-1]
    assert first_operation.kind == "vertex_collapse"
    assert first_operation.collapsed_vertex == 3


def test_height_mode_prunes_smallest_prunable_leaf_first():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0}
    tree = [(8, 5), (9, 5), (5, 0)]

    result = simplify_contour_tree(tree, values, mode="height", threshold=4.0)

    assert _edge_set(result.edges) == {(0, 9)}
    leaf_prunes = [record for record in result.collapse_record if record.kind == "leaf_prune"]
    assert leaf_prunes[-1].leaf == 8


def test_pruning_leaf_collapses_newly_regular_interior():
    values = {1: 0.0, 2: 2.0, 3: 3.0, 4: 4.0}
    tree = [(4, 2), (3, 2), (2, 1)]

    result = simplify_contour_tree(
        tree,
        values,
        mode="height",
        threshold=float("inf"),
        target_edges=1,
    )

    assert len(result.edges) == 1
    _assert_tree(result.edges)
    chronological_kinds = [record.kind for record in reversed(result.collapse_record)]
    assert chronological_kinds.index("leaf_prune") < chronological_kinds.index("vertex_collapse")


def test_target_edges_stops_simplification():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0, 1: 1.0}
    tree = [(8, 5), (9, 5), (5, 0), (5, 1)]

    result = simplify_contour_tree(
        tree,
        values,
        mode="height",
        threshold=float("inf"),
        target_edges=2,
    )

    assert len(result.edges) <= 2
    _assert_tree(result.edges)


def test_target_edges_can_be_reached_by_regular_collapse():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    tree = [(3, 2), (2, 1)]

    result = simplify_contour_tree(
        tree,
        values,
        mode="height",
        threshold=float("inf"),
        target_edges=1,
    )

    assert len(result.edges) == 1
    assert _edge_set(result.edges) == {(1, 3)}


def test_simplified_tree_edge_count_never_increases():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0, 1: 1.0}
    tree = [(8, 5), (9, 5), (5, 0), (5, 1)]

    result = simplify_contour_tree(
        tree,
        values,
        mode="height",
        threshold=float("inf"),
        target_edges=1,
    )

    assert len(result.edges) <= len(tree)
    _assert_tree(result.edges)
