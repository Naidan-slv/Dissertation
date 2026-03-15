"""
Tests for the join sweep (Algorithm 4.1, Carr et al. 2003).

Built incrementally -- one test per step of the algorithm.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Computing Contour Trees in All Dimensions."
    Computational Geometry, 24(3), 75-94.
    Algorithm 4.1.
"""

import pytest
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree


# -----------------------------------------
# Step 1 -- Function is callable and returns a list
# -----------------------------------------

def test_join_tree_is_callable(single_peak_mesh):
    """
    compute_join_tree must accept a mesh and return a list.
    This is the minimal contract before any logic is implemented.
    """
    result = compute_join_tree(single_peak_mesh)
    assert isinstance(result, list)


# -----------------------------------------
# Step 2 -- Vertices are sorted ascending by scalar value
# The join sweep must process vertices bottom to top.
# Based on: Carr et al. (2003) Algorithm 4.1 -- ascending vertex order.
# We verify this indirectly via mesh.sorted_vertices() which the function uses.
# -----------------------------------------

def test_sorted_verts_ascending(two_peaks_mesh):
    """
    mesh.sorted_vertices() must return all vertices ordered by scalar value
    ascending, with vertex ID as tiebreaker.
    This is the order compute_join_tree processes vertices in.
    Based on: Carr et al. (2003) Algorithm 4.1.
    """
    verts = two_peaks_mesh.sorted_vertices(ascending=True)
    assert len(verts) == 4

    values = [two_peaks_mesh.value(v) for v in verts]
    assert values == sorted(values)


def test_sorted_verts_contains_all_vertices(two_peaks_mesh):
    """
    sorted_vertices() must contain every vertex -- no duplicates, no omissions.
    """
    verts = two_peaks_mesh.sorted_vertices(ascending=True)
    assert sorted(verts) == sorted(two_peaks_mesh.vertices())
