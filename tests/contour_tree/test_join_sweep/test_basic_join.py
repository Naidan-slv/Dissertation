"""
Basic join sweep tests covering simple, canonical cases.

These tests verify the core join sweep algorithm on the simplest meshes:
- single_peak: degenerate case (no actual joins)
- two_peaks_merge: the canonical binary join

Based on:
    Carr et al. (2003), Algorithm 4.1
"""

from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree


def test_single_peak_no_joins(single_peak_mesh):
    """
    Single peak mesh is monotone (linear chain).
    Expected: linear chain of join edges.
    
    Vertices: 0(0.0), 1(0.5), 2(1.0), all connected in a triangle.
    Processing descending: 2, 1, 0
    - v=2: no higher neighbours -> no edge
    - v=1: higher neighbour 2, lowest_in_component(2)=2, edge (2,1), union
    - v=0: higher neighbours 1,2 (same component), lowest=1, edge (1,0)
    Expected edges: [(1,0), (2,1)]
    """
    result = compute_join_tree(single_peak_mesh)
    result_sorted = sorted(result)
    expected = sorted([(2, 1), (1, 0)])
    
    assert result_sorted == expected


def test_two_peaks_binary_join(two_peaks_mesh):
    """
    Two peaks merging at one point is the canonical join tree case.
    
    Vertices: 0(0.1), 1(0.5), 2(0.8), 3(0.9)
    Processing descending: 3, 2, 1, 0
    - v=3: no higher neighbours -> no edge
    - v=2: no higher neighbours (3 not adjacent to 2) -> no edge
    - v=1: higher neighbours {2,3}, two distinct components:
           lowest_in_component(2)=2, edge (2,1), union
           lowest_in_component(3)=3, edge (3,1), union
    - v=0: higher neighbours {1,2,3} all one component, lowest=1, edge (1,0)
    Expected edges: [(1,0), (2,1), (3,1)]
    """
    result = compute_join_tree(two_peaks_mesh)
    result_sorted = sorted(result)
    expected = sorted([(1, 0), (2, 1), (3, 1)])
    
    assert result_sorted == expected
