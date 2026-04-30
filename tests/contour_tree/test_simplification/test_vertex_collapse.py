"""Tests for Carr Algorithm 11.1 vertex collapse."""

from src.contour_tree_algo.simplification import (
    active_edges,
    build_mutable_tree,
    down_degree,
    is_regular,
    up_degree,
    vertex_collapse,
)


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def test_regular_chain_vertex_collapses_to_one_edge():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    state = build_mutable_tree([(3, 2), (2, 1)], values)

    new_edge_id = vertex_collapse(state, 2)

    assert _edge_set(active_edges(state)) == {(1, 3)}
    assert state.edges[new_edge_id].old_edges == (0, 1)


def test_regular_vertex_has_one_up_and_one_down_edge():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    state = build_mutable_tree([(3, 2), (2, 1)], values)

    assert up_degree(state, 2) == 1
    assert down_degree(state, 2) == 1
    assert is_regular(state, 2)


def test_vertex_collapse_marks_old_edges_as_collapsed():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    state = build_mutable_tree([(3, 2), (2, 1)], values)

    vertex_collapse(state, 2)

    assert not state.edges[0].active
    assert not state.edges[1].active
    assert state.edges[0].already_collapsed
    assert state.edges[1].already_collapsed


def test_vertex_collapse_records_operation():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    state = build_mutable_tree([(3, 2), (2, 1)], values)

    new_edge_id = vertex_collapse(state, 2)

    assert state.collapse_record[0].kind == "vertex_collapse"
    assert state.collapse_record[0].removed_edges == (0, 1)
    assert state.collapse_record[0].new_edge == new_edge_id
    assert state.collapse_record[0].collapsed_vertex == 2


def test_vertex_collapse_transfers_up_and_down_weights():
    values = {1: 0.0, 2: 1.0, 3: 2.0}
    measures = {
        (2, 3): object(),
        (1, 2): object(),
    }
    state = build_mutable_tree([(3, 2), (2, 1)], values, measures=measures)
    state.edges[0].up_weight = 30.0
    state.edges[1].down_weight = 10.0

    new_edge_id = vertex_collapse(state, 2)

    assert state.edges[new_edge_id].up_weight == 30.0
    assert state.edges[new_edge_id].down_weight == 10.0
