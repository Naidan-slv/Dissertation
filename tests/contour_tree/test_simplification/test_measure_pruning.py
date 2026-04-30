"""Tests for measure-ranked simplification."""

from src.contour_tree_algo.measures import ArcMeasure
from src.contour_tree_algo.simplification import simplify_contour_tree


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
