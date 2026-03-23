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
    
    Split sweep processes ascending: [0, 1, 2].
    For each vertex, look for LOWER neighbours and merge.
    
    - v=0: no lower neighbours -> no edge
    - v=1: lower neighbour 0, highest_in_component(0)=0, edge (0,1), union
    - v=2: lower neighbours {0,1} (same component), highest=1, edge (1,2)
    
    Result should be: [(0,1), (1,2)]
    """
    result = compute_split_tree(single_peak_mesh)
    result_sorted = sorted(result)
    expected = sorted([(0, 1), (1, 2)])
    
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

    Split sweep (ascending): process order is [0, 1, 2, 3]

    - v=0 (0.1): no lower neighbours -> no edge
    - v=1 (0.5): lower neighbours {0}.
                 highest_in_component(0)=0, edge (0,1), union
    - v=2 (0.8): lower neighbours {0,1} (same component).
                 highest_in_component(0)=1, edge (1,2), union
    - v=3 (0.9): lower neighbours {0,1} (same component as 2).
                 highest_in_component(0)=2, edge (2,3)

    Expected result: [(0,1), (1,2), (2,3)]
    """
    result = compute_split_tree(two_peaks_mesh)
    result_sorted = sorted(result)
    expected = sorted([(0, 1), (1, 2), (2, 3)])
