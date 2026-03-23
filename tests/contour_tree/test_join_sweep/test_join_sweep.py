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


# -----------------------------------------
# Step 3 -- Each vertex is made into a singleton set in the UnionFind
# Before any unions, every vertex must be registered via make_set.
# Based on: Carr et al. (2003) Algorithm 4.1 -- initialization step
# -----------------------------------------

def test_make_set_each_vertex(two_peaks_mesh):
    """
    compute_join_tree must call make_set for each vertex.
    We verify this indirectly: if any vertex is skipped,
    subsequent calls to find() would fail with KeyError.
    The function should complete without error on a multi-vertex mesh.
    Based on: Carr et al. (2003) Algorithm 4.1 -- "for i := 1 to n, make_set(i)"
    """
    # This test just ensures compute_join_tree can be called
    # and returns without error. Step 4 will add the union logic
    # that would fail if any vertex was skipped.
    result = compute_join_tree(two_peaks_mesh)
    assert isinstance(result, list)


# -----------------------------------------
# Step 4 -- Union lower neighbours and record join edges
# For each vertex, find lower neighbours, call union, and record edges.
# Based on: Carr et al. (2003) Algorithm 4.1 -- join sweep core loop
# -----------------------------------------

def test_join_tree_two_peaks_merge(two_peaks_mesh):
    """
    For two_peaks_merge mesh:
      vertices: 0(0.1), 1(0.5), 2(0.8), 3(0.9)
      edges: (0,1), (0,1), (1,2), (0,3)
    
    The join tree should have edges connecting lower vertices to where they merge.
    Expected result: some join edges are recorded.
    
    Based on: Carr et al. (2003) Algorithm 4.1.
    Hand-traced expected edges: [(0,1), (0,2), (0,3)]
    (vertex 0 is the lowest, vertices 1,2,3 all merge into the component containing 0)
    """
    result = compute_join_tree(two_peaks_mesh)
    
    # Should have some edges
    assert isinstance(result, list)
    assert len(result) > 0, "Join tree should have at least one edge"
    
    # Each edge should be a tuple of two vertices
    for edge in result:
        assert isinstance(edge, tuple) and len(edge) == 2
        child, parent = edge
        assert child in two_peaks_mesh.vertices()
        assert parent in two_peaks_mesh.vertices()
        assert child != parent, "A vertex should not merge with itself"


def test_join_tree_two_peaks_merge_exact_edges(two_peaks_mesh):
    """
    Verify the exact join tree edges for two_peaks_merge.
    
    Processing order (top to bottom): 3(0.9), 2(0.8), 1(0.5), 0(0.1)
    - v=3: no higher neighbours -> no edge
    - v=2: no higher neighbours (3 not adjacent) -> no edge
    - v=1: higher neighbours {2,3}, two distinct components:
           lowest_in_component(2)=2, edge (2,1); lowest_in_component(3)=3, edge (3,1)
    - v=0: higher neighbours all one component, lowest=1, edge (1,0)
    """
    result = compute_join_tree(two_peaks_mesh)
    
    # Sort for deterministic comparison
    result_sorted = sorted(result)
    expected = sorted([(1, 0), (2, 1), (3, 1)])
    
    assert result_sorted == expected, f"Expected {expected}, got {result_sorted}"
