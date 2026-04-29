"""Tests for Carr-Snoeyink-Axen leaf-queue merge."""

from collections import defaultdict, deque

from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def _assert_tree(edges, vertices):
    assert len(edges) == max(0, len(vertices) - 1)
    assert len(_edge_set(edges)) == len(edges)

    if not vertices:
        return

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


def _merged_from_mesh(mesh):
    join_edges = compute_join_tree(mesh)
    split_edges = compute_split_tree(mesh)
    return merge_trees(join_edges, split_edges, mesh.value)


def test_empty_edge_lists_return_empty_tree():
    assert merge_trees([], [], lambda v: 0.0) == []


def test_single_edge_tree_is_preserved():
    values = {0: 0.0, 1: 1.0}

    edges = merge_trees([(1, 0)], [(0, 1)], values.__getitem__)

    assert _edge_set(edges) == {(0, 1)}


def test_monotone_chain_merge_is_tree():
    values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
    join_edges = [(3, 2), (2, 1), (1, 0)]
    split_edges = [(0, 1), (1, 2), (2, 3)]

    edges = merge_trees(join_edges, split_edges, values.__getitem__)

    assert _edge_set(edges) == {(0, 1), (1, 2), (2, 3)}
    _assert_tree(edges, [0, 1, 2, 3])


def test_join_fork_two_peaks():
    values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
    join_edges = [(2, 1), (3, 1), (1, 0)]
    split_edges = [(0, 1), (1, 2), (2, 3)]

    edges = merge_trees(join_edges, split_edges, values.__getitem__)

    assert _edge_set(edges) == {(0, 1), (1, 2), (1, 3)}
    _assert_tree(edges, [0, 1, 2, 3])


def test_split_fork_two_valleys():
    values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
    join_edges = [(3, 2), (2, 1), (1, 0)]
    split_edges = [(0, 2), (1, 2), (2, 3)]

    edges = merge_trees(join_edges, split_edges, values.__getitem__)

    assert _edge_set(edges) == {(0, 2), (1, 2), (2, 3)}
    _assert_tree(edges, [0, 1, 2, 3])


def test_merge_output_has_no_duplicate_edges():
    values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
    join_edges = [(2, 1), (3, 1), (1, 0)]
    split_edges = [(0, 1), (1, 2), (2, 3)]

    edges = merge_trees(join_edges, split_edges, values.__getitem__)

    assert len(_edge_set(edges)) == len(edges)


def test_single_peak_fixture_merge(single_peak_mesh):
    edges = _merged_from_mesh(single_peak_mesh)

    assert _edge_set(edges) == {(0, 1), (1, 2)}
    _assert_tree(edges, [0, 1, 2])


def test_two_peaks_fixture_merge(two_peaks_mesh):
    edges = _merged_from_mesh(two_peaks_mesh)

    assert _edge_set(edges) == {(0, 1), (1, 2), (1, 3)}
    _assert_tree(edges, [0, 1, 2, 3])


def test_three_peaks_fixture_merge(three_peaks_mesh):
    edges = _merged_from_mesh(three_peaks_mesh)

    assert _edge_set(edges) == {(0, 1), (1, 2), (1, 3), (1, 4)}
    _assert_tree(edges, [0, 1, 2, 3, 4])


def test_saddle_fixture_merge(saddle_mesh):
    edges = _merged_from_mesh(saddle_mesh)

    assert _edge_set(edges) == {(0, 1), (1, 2), (2, 3)}
    _assert_tree(edges, [0, 1, 2, 3])
