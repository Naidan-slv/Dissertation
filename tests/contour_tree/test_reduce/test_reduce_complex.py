"""
Edge case and complex topology tests for reduce_contour_tree.

Tests larger trees, multiple saddles, long chains, and validates
superarc counts match expected topology.
"""

import pytest
from src.contour_tree_algo.reduce import reduce_contour_tree


class TestReduceComplex:
    """Test reduce on more complex tree topologies."""

    def test_diamond_two_saddles(self):
        """
        Diamond shape (two saddles):

            0
           / \\
          1   2       saddles at 1 and 2
           \\ /
            3

        But as a tree (no cycles!):
            0 -- 1 -- 3
            0 -- 2 -- 3   ← would create cycle, not valid tree

        Actual valid tree with two saddles:
            3 -- 1 -- 0 -- 2 -- 4
                      |
                      5

        Vertex 0 has degree 3 (saddle), all others degree 1 or on a path.
        """
        edges = [(3, 1), (1, 0), (0, 2), (2, 4), (0, 5)]
        supernodes, superarcs = reduce_contour_tree(edges)

        # 0 is degree-3 (saddle), 1 and 2 are degree-2 (regular), 3,4,5 are leaves
        assert 0 in supernodes
        assert 3 in supernodes
        assert 4 in supernodes
        assert 5 in supernodes
        # 1 and 2 are degree-2 → removed
        assert 1 not in supernodes
        assert 2 not in supernodes
        assert len(superarcs) == 3

    def test_long_chain_many_regular(self):
        """
        Long chain: 0 -- 1 -- 2 -- ... -- 9

        Only endpoints 0 and 9 are critical. All middle vertices removed.
        """
        edges = [(i, i + 1) for i in range(9)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 9]
        assert len(superarcs) == 1
        assert tuple(sorted(superarcs[0])) == (0, 9)

    def test_star_graph(self):
        """
        Star: centre 0 connected to 1, 2, 3, 4, 5.

        Centre has degree 5 (saddle), all others degree 1 (leaves).
        All vertices are critical — no reduction happens.
        """
        edges = [(0, i) for i in range(1, 6)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 1, 2, 3, 4, 5]
        assert len(superarcs) == 5

    def test_superarc_count_equals_supernodes_minus_one(self):
        """
        For any tree: #superarcs == #supernodes - 1.

        Test on a complex tree with mixed regular and critical vertices.

            10 -- 11 -- 12 -- 0 -- 1 -- 2 -- 3
                              |
                              4 -- 5 -- 6
                              |
                              7 -- 8 -- 9
        """
        edges = [
            (10, 11), (11, 12), (12, 0),  # arm 1
            (0, 1), (1, 2), (2, 3),        # arm 2
            (0, 4), (4, 5), (5, 6),        # arm 3
            (0, 7), (7, 8), (8, 9),        # arm 4
        ]
        supernodes, superarcs = reduce_contour_tree(edges)

        # vertex 0 is degree-4 (saddle), endpoints 3,6,9,10 are leaves
        assert 0 in supernodes
        assert len(superarcs) == len(supernodes) - 1

    def test_all_critical_no_reduction(self):
        """
        Tree where every vertex is critical (no degree-2):

            1 -- 0 -- 2
           / \\      / \\
          3   4    5   6

        0: degree 2 → regular (will be removed)
        1: degree 3 → saddle
        2: degree 3 → saddle
        3,4,5,6: degree 1 → leaves

        Superarcs: (3,1), (4,1), (1,2), (5,2), (6,2) — but 0 is removed
        so (1,0) + (0,2) contracts to (1,2).
        """
        edges = [(1, 0), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [1, 2, 3, 4, 5, 6]
        assert len(superarcs) == 5
        arc_set = {tuple(sorted(a)) for a in superarcs}
        assert (1, 2) in arc_set  # contracted from 1-0-2
