"""
Tests for perturbation removal — collapsing artificial critical points
from tie-breaking on flat plateaus.
"""

import pytest
from src.contour_tree_algo.reduce import reduce_contour_tree, remove_perturbation


class TestPerturbationRemoval:
    """Test that flat superarcs are contracted correctly."""

    def test_no_flat_edges_unchanged(self):
        """If no supernodes share a value, tree structure is preserved.
        
        Y-shape so all nodes are truly critical (no degree-2):
            0 (0) -- 2 (5) -- 3 (10)
                     |
                     1 (3)
        """
        supernodes = [0, 1, 2, 3]
        superarcs = [(0, 2), (1, 2), (2, 3)]
        values = {0: 0, 1: 3, 2: 5, 3: 10}

        sn, sa = remove_perturbation(supernodes, superarcs, values.get)
        assert sorted(sn) == [0, 1, 2, 3]
        assert len(sa) == 3

    def test_single_flat_edge_contracted(self):
        """
        Y-shape with a flat edge on one branch:

            0 (0) -- 1 (5) -- 2 (5)
                     |
                     3 (10)

        Superarc (1,2) is flat. After contraction: {1,2} merges.
        Result: 3 supernodes (0, {1or2}, 3), 2 superarcs.
        But {1or2} has degree 2 → re-reduced to just 0 -- 3.
        
        Actually, the merged node connects to both 0 and 3, so degree 2 → 
        gets reduced. Final: 2 supernodes.
        
        Wait — original was a Y: 1 connects to 0, 2, and 3. After merging
        1 and 2 (flat), the merged node connects to 0 and 3 = degree 2.
        So yes, reduced to 0 -- 3.
        """
        supernodes = [0, 1, 2, 3]
        superarcs = [(0, 1), (1, 2), (1, 3)]
        values = {0: 0, 1: 5, 2: 5, 3: 10}

        sn, sa = remove_perturbation(supernodes, superarcs, values.get)
        assert len(sn) == 2
        assert len(sa) == 1

    def test_chain_of_flat_edges(self):
        """
        Y-shape where one arm has a flat chain:

            0 (0) -- 3 (5) -- 4 (5) -- 5 (5)
                     |
                     6 (10)

        Flat edges: (3,4), (4,5). All merge into one rep.
        Rep connects to 0 and 6 → degree 2 → re-reduced.
        Final: 0 -- 6.
        
        But if we make it a proper tree with branches:

            0 (0) -- 1 (5) -- 2 (5)
                     |         |
                     3 (10)    4 (8)

        Flat edge (1,2). Merge → rep connects to 0, 3, 4. Degree 3 = survives.
        """
        supernodes = [0, 1, 2, 3, 4]
        superarcs = [(0, 1), (1, 2), (1, 3), (2, 4)]
        values = {0: 0, 1: 5, 2: 5, 3: 10, 4: 8}

        sn, sa = remove_perturbation(supernodes, superarcs, values.get)
        # 1 and 2 merge → rep connects to 0, 3, 4 (degree 3). Survives.
        assert len(sn) == 4
        assert len(sa) == 3

    def test_flat_edge_creates_degree2_after_merge(self):
        """
        Y-shape where one branch has a flat edge:

            0 (0) -- 2 (5) -- 3 (10)
                     |
                     1 (5)

        Superarc (1,2) is flat. After contraction, {1,2} has degree 2
        (connected to 0 and 3), so it gets re-reduced away.
        Result: just 0 -- 3.
        """
        supernodes = [0, 1, 2, 3]
        superarcs = [(0, 2), (1, 2), (2, 3)]
        values = {0: 0, 1: 5, 2: 5, 3: 10}

        sn, sa = remove_perturbation(supernodes, superarcs, values.get)
        # After flat contraction: {1,2}→rep, with edges to 0 and 3
        # rep has degree 2 → removed in re-reduce
        assert len(sn) == 2
        assert len(sa) == 1
        assert tuple(sorted(sa[0])) == (0, 3)

    def test_empty_input(self):
        """Empty input stays empty."""
        sn, sa = remove_perturbation([], [], lambda x: 0)
        assert sn == []
        assert sa == []
