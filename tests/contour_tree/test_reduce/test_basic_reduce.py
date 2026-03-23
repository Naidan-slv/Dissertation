"""
Basic tests for reduce_contour_tree (Algorithm 7.4).

Verifies that degree-2 vertices are removed and only critical points
(leaves and branch points) survive as supernodes.
"""

import pytest
from src.contour_tree_algo.reduce import reduce_contour_tree


class TestReduceBasic:
    """Core reduce behaviour on small hand-crafted trees."""

    def test_simple_path_no_branches(self):
        """
        Path: 0 -- 1 -- 2 -- 3  (all degree-2 except endpoints)

        Only the two endpoints (0, 3) are critical (leaves).
        Should reduce to one superarc: (0, 3).
        """
        edges = [(0, 1), (1, 2), (2, 3)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 3]
        assert len(superarcs) == 1
        assert tuple(sorted(superarcs[0])) == (0, 3)

    def test_single_edge(self):
        """
        Trivial tree: 0 -- 1

        Both vertices are leaves (degree 1) → both critical.
        No reduction possible.
        """
        edges = [(0, 1)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 1]
        assert len(superarcs) == 1

    def test_y_shape_one_saddle(self):
        """
        Y-shape:  0 -- 2 -- 3
                       |
                       1

        Vertex 2 has degree 3 (saddle), vertices 0, 1, 3 are leaves.
        All four are critical. Three superarcs.
        """
        edges = [(0, 2), (1, 2), (2, 3)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 1, 2, 3]
        assert len(superarcs) == 3

    def test_y_with_regular_vertices(self):
        """
        Y-shape with degree-2 vertices on each arm:

            0 -- 4 -- 2 -- 5 -- 3
                      |
                      1

        Critical: 0 (leaf), 1 (leaf), 2 (saddle, deg 3), 3 (leaf)
        Regular:  4 (deg 2), 5 (deg 2) → removed

        Superarcs: (0,2), (1,2), (2,3)
        """
        edges = [(0, 4), (4, 2), (1, 2), (2, 5), (5, 3)]
        supernodes, superarcs = reduce_contour_tree(edges)

        assert sorted(supernodes) == [0, 1, 2, 3]
        assert len(superarcs) == 3
        arc_set = {tuple(sorted(a)) for a in superarcs}
        assert (0, 2) in arc_set
        assert (1, 2) in arc_set
        assert (2, 3) in arc_set

    def test_empty_tree(self):
        """Empty edge list → no supernodes, no superarcs."""
        supernodes, superarcs = reduce_contour_tree([])

        assert supernodes == []
        assert superarcs == []
