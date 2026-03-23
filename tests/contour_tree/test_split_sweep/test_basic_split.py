"""
Basic split sweep tests covering simple, canonical cases.

These tests verify the core split sweep algorithm on the simplest meshes:
- single_peak: degenerate case (no actual splits)
- two_peaks_merge: the canonical binary split (mirror of join)

Based on:
    Carr et al. (2003), Algorithm 4.1 applied in reverse (split sweep)
"""

from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree


def test_single_peak_no_splits(single_peak_mesh):
    """
    Testing a simple monotone chain - just a linear path up to a peak.
    
    Mesh structure:
        2 (1.0)  <- peak
        |
        1 (0.5)
        |
        0 (0.0)  <- minimum
    
    When we do the split sweep top-to-bottom, we process [2, 1, 0].
    At each vertex, we look for HIGHER neighbors and merge them.
    
    - v=2: no higher neighbors
    - v=1: higher neighbor 2, so edge (2, 1)
    - v=0: higher neighbor 1, so edge (2, 0) (since 0 and 1 are already merged)
    
    Result should be: [(2, 1), (2, 0)]
    """
    result = compute_split_tree(single_peak_mesh)
    result_sorted = sorted(result)
    expected = sorted([(2, 1), (2, 0)])
    
    assert result_sorted == expected


def test_two_peaks_binary_split(two_peaks_mesh):
    """
    Two peaks connected through a join point. This is the opposite of
    the join sweep - instead of merging upward, we're splitting downward.
    
    Mesh structure:
        2(0.8)  3(0.9)  <- two separate peaks (NOT neighbors)
          \    /
           1(0.5)        <- join point
            |
           0(0.1)        <- minimum

    Adjacency (from triangles (0,1,2) and (0,1,3)):
    - 0: {1, 2, 3}
    - 1: {0, 2, 3}
    - 2: {0, 1}  <- NOT neighbors with 3
    - 3: {0, 1}

    Split sweep (descending): process order is [3, 2, 1, 0]

    - v=3 (0.9): highest peak, no higher neighbors -> no edge
    - v=2 (0.8): no higher neighbors (3 not connected to 2)-> no edge
    - v=1 (0.5): neighbors {0,2,3}. Higher neighbors are {2, 3}.
                 Both 2 and 3 are separate components, so:
                 edge (2, 1), union(2, 1)
                 edge (3, 1), union(3, 1)
                 Result: all three in same component with 3 as root
    - v=0 (0.1): all neighbors {1,2,3} are higher
                 find(2) = 3, find(3) = 3 (same root after unions)
                 only one distinct root: 3-> edge (3, 0)

    Expected result: [(2, 1), (3, 0), (3, 1)]
    """
    result = compute_split_tree(two_peaks_mesh)
    result_sorted = sorted(result)
    expected = sorted([(2, 1), (3, 0), (3, 1)])
