"""Tests for measure-ranked simplification."""

from src.contour_tree_algo.measures import ArcMeasure
from src.contour_tree_algo.simplification import (
    build_mutable_tree,
    edge_priority,
    simplify_contour_tree,
)


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def test_measure_mode_can_choose_different_leaf_than_height_mode():
    values = {5: 5.0, 8: 8.0, 20: 20.0, 0: 0.0}
    tree = [(8, 5), (20, 5), (5, 0)]
    measures = {
        (5, 8): ArcMeasure(
            node_count=100,
            cell_crossing_count=100,
            scalar_sum=0.0,
            scalar_square_sum=0.0,
            sample_vertices=(5, 8),
        ),
        (5, 20): ArcMeasure(
            node_count=1,
            cell_crossing_count=1,
            scalar_sum=0.0,
            scalar_square_sum=0.0,
            sample_vertices=(5, 20),
        ),
        (0, 5): ArcMeasure(
            node_count=100,
            cell_crossing_count=100,
            scalar_sum=0.0,
            scalar_square_sum=0.0,
            sample_vertices=(0, 5),
        ),
    }

    height_result = simplify_contour_tree(
        tree,
        values,
        mode="height",
        threshold=float("inf"),
        target_edges=2,
    )
    measure_result = simplify_contour_tree(
        tree,
        values,
        measures=measures,
        mode="measure",
        threshold=float("inf"),
        target_edges=2,
    )

    assert height_result.collapse_record[0].leaf == 8
    assert measure_result.collapse_record[0].leaf == 20
    assert _edge_set(height_result.edges) != _edge_set(measure_result.edges)


def test_measure_upper_leaf_priority_uses_down_weight():
    values = {5: 5.0, 10: 10.0}
    state = build_mutable_tree([(10, 5)], values)
    state.edges[0].up_weight = 50.0
    state.edges[0].down_weight = 7.0

    priority = edge_priority(state, 0, mode="measure", leaf=10, interior=5)

    assert priority == 7.0


def test_measure_lower_leaf_priority_uses_up_weight():
    values = {5: 5.0, 1: 1.0}
    state = build_mutable_tree([(5, 1)], values)
    state.edges[0].up_weight = 50.0
    state.edges[0].down_weight = 7.0

    priority = edge_priority(state, 0, mode="measure", leaf=1, interior=5)

    assert priority == 50.0
