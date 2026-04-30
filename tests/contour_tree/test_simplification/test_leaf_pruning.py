"""Tests for Carr Definition 11.2 prunable leaves."""

from src.contour_tree_algo.simplification import (
    active_edges,
    build_mutable_tree,
    is_leaf,
    is_prunable_leaf,
    leaf_info,
    leaf_prune,
    simplify_contour_tree,
)


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def test_leaf_info_identifies_leaf_and_interior():
    values = {0: 0.0, 1: 1.0, 5: 5.0, 10: 10.0}
    state = build_mutable_tree([(10, 5), (5, 0), (5, 1)], values)

    assert leaf_info(state, 0) == (10, 5)
    assert is_leaf(state, 10)


def test_upper_leaf_is_prunable_when_interior_has_multiple_up_edges():
    values = {5: 5.0, 8: 8.0, 9: 9.0, 0: 0.0}
    state = build_mutable_tree([(8, 5), (9, 5), (5, 0)], values)

    assert is_prunable_leaf(state, 8, 5)


def test_last_upper_leaf_is_not_prunable():
    values = {5: 5.0, 9: 9.0, 0: 0.0, 1: 1.0}
    state = build_mutable_tree([(9, 5), (5, 0), (5, 1)], values)

    assert not is_prunable_leaf(state, 9, 5)


def test_carr_figure_11_5_upper_leaf_is_not_pruned():
    values = {50: 50.0, 71: 71.0, 81: 81.0, 90: 90.0}
    tree = [(90, 81), (81, 71), (81, 50)]
    state = build_mutable_tree(tree, values)

    assert not is_prunable_leaf(state, 90, 81)

    result = simplify_contour_tree(tree, values, mode="height", threshold=float("inf"))
    leaf_prunes = [record for record in result.collapse_record if record.kind == "leaf_prune"]
    assert all(record.leaf != 90 for record in leaf_prunes)


def test_lower_leaf_is_prunable_when_interior_has_multiple_down_edges():
    values = {5: 5.0, 9: 9.0, 0: 0.0, 1: 1.0}
    state = build_mutable_tree([(9, 5), (5, 0), (5, 1)], values)

    assert is_prunable_leaf(state, 0, 5)


def test_leaf_prune_removes_leaf_edge_only():
    values = {5: 5.0, 9: 9.0, 0: 0.0, 1: 1.0}
    state = build_mutable_tree([(9, 5), (5, 0), (5, 1)], values)

    interior = leaf_prune(state, 1, priority=5.0)

    assert interior == 5
    assert _edge_set(active_edges(state)) == {(5, 9), (1, 5)}
    assert state.collapse_record[0].kind == "leaf_prune"
    assert state.collapse_record[0].removed_edges == (1,)
    assert state.collapse_record[0].leaf == 0
    assert state.collapse_record[0].interior == 5
    assert state.collapse_record[0].priority == 5.0
