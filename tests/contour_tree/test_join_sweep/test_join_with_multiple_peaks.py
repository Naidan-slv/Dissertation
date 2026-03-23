"""
Join sweep tests for meshes with multiple peaks and more complex topologies.

These tests cover:
- three_peaks_merge: multi-way join (3+ branches)
- saddle_mesh: tied values (determinism test)
- nested_hierarchy_mesh: hierarchical join structure

Based on:
    Carr et al. (2003), Algorithm 4.1 and Section 3 (contour tree structure)
"""

from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree


def test_three_peaks_multiway_join(three_peaks_mesh):
    """
    Three peaks merging at one point tests multi-way join handling.
    
    Vertices: 0(0.1), 1(0.5), 2(0.8), 3(0.9), 4(1.0)
    Processing descending: 4, 3, 2, 1, 0
    - v=4,3,2: no higher neighbours (peaks not adjacent to each other)
    - v=1: higher neighbours {2,3,4}, three distinct components:
           edges (2,1), (3,1), (4,1)
    - v=0: higher neighbours all one component, lowest=1, edge (1,0)
    Expected edges: [(1,0), (2,1), (3,1), (4,1)]
    """
    result = compute_join_tree(three_peaks_mesh)
    result_sorted = sorted(result)
    expected = sorted([(1, 0), (2, 1), (3, 1), (4, 1)])
    
    assert result_sorted == expected


def test_saddle_mesh_tied_values(saddle_mesh):
    """
    Saddle mesh has tied values (vertices 1 and 2 both 0.5).
    This tests deterministic tie-breaking by vertex ID.
    
    Vertices: 0(0.1), 1(0.5), 2(0.5), 3(0.9)
    Adjacency: 0-{1,2,3}, 1-{0,3}, 2-{0,3}, 3-{0,1,2}
    Descending (with tiebreak): 3, 2, 1, 0
    - v=3: no higher neighbours -> no edge
    - v=2: higher neighbour 3 (tied at 0.5 but 3>2 so 3 is "higher"),
           lowest_in_component(3)=3, edge (3,2), union
    - v=1: higher neighbour 3 (same component as 2),
           lowest_in_component(3)=2, edge (2,1), union
    - v=0: higher neighbours all one component, lowest=1, edge (1,0)
    Expected edges: [(1,0), (2,1), (3,2)]
    """
    result = compute_join_tree(saddle_mesh)
    result_sorted = sorted(result)
    expected = sorted([(1, 0), (2, 1), (3, 2)])
    
    assert result_sorted == expected


def test_nested_hierarchy_mesh_complex(nested_hierarchy_mesh):
    """
    Nested hierarchy mesh tests correct component tracking across
    multiple levels of topological structure.
    
    Vertices: 0(0.1), 1(0.4), 2(0.6), 3(0.7), 4(0.8), 5(1.0)
    Adjacency: 0-{1,2,3}, 1-{0,2,3}, 2-{0,1,3,4,5}, 3-{0,1,2,4,5}, 4-{2,3,5}, 5-{2,3,4}
    Descending: 5, 4, 3, 2, 1, 0 — each vertex merges with the one above it
    forming a linear chain: (5,4), (4,3), (3,2), (2,1), (1,0)
    """
    result = compute_join_tree(nested_hierarchy_mesh)
    result_sorted = sorted(result)
    expected = sorted([(5, 4), (4, 3), (3, 2), (2, 1), (1, 0)])
    
    assert result_sorted == expected
