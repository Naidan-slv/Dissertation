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
    Expected: linear sequence of join edges.
    
    Vertices: 0(0.0), 1(0.5), 2(1.0), all connected in a line.
    Expected edges: [(0,1), (0,2)] — 0 is lowest, 1 and 2 merge into it sequentially
    """
    result = compute_join_tree(single_peak_mesh)
    result_sorted = sorted(result)
    expected = sorted([(0, 1), (0, 2)])
    
    assert result_sorted == expected


def test_two_peaks_binary_join(two_peaks_mesh):
    """
    Two peaks merging at one point is the canonical join tree case.
    Expected edges: [(0,1), (0,2), (0,3)]
    
    Vertices: 0(0.1), 1(0.5), 2(0.8), 3(0.9)
    """
    result = compute_join_tree(two_peaks_mesh)
    result_sorted = sorted(result)
    expected = sorted([(0, 1), (0, 2), (0, 3)])
    
    assert result_sorted == expected
