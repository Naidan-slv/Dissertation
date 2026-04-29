"""Split sweep tests for meshes with several low branches."""

from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.meshes.mesh2d import TriMesh2D


def _edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def test_three_valleys_multiway_split():
    values = {0: 0.0, 1: 0.1, 2: 0.2, 3: 0.6, 4: 1.0}
    triangles = [(0, 3, 4), (1, 3, 4), (2, 3, 4)]
    mesh = TriMesh2D(values, triangles)

    result = compute_split_tree(mesh)

    assert sorted(result) == sorted([(0, 3), (1, 3), (2, 3), (3, 4)])


def test_three_valleys_edge_count():
    values = {0: 0.0, 1: 0.1, 2: 0.2, 3: 0.6, 4: 1.0}
    triangles = [(0, 3, 4), (1, 3, 4), (2, 3, 4)]
    mesh = TriMesh2D(values, triangles)

    result = compute_split_tree(mesh)

    assert len(result) == len(values) - 1
    assert len(_edge_set(result)) == len(result)


def test_tied_valleys_use_vertex_id_order():
    values = {0: 0.0, 1: 0.0, 2: 0.5, 3: 1.0}
    triangles = [(0, 2, 3), (1, 2, 3)]
    mesh = TriMesh2D(values, triangles)

    result = compute_split_tree(mesh)

    assert sorted(result) == sorted([(0, 2), (1, 2), (2, 3)])


def test_split_edges_follow_low_to_high_order():
    values = {0: 0.0, 1: 0.1, 2: 0.2, 3: 0.6, 4: 1.0}
    triangles = [(0, 3, 4), (1, 3, 4), (2, 3, 4)]
    mesh = TriMesh2D(values, triangles)

    result = compute_split_tree(mesh)

    for low, high in result:
        assert (mesh.value(low), low) < (mesh.value(high), high)
