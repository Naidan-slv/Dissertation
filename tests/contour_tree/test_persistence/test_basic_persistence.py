"""
Tests for compute_persistence_pairs.

Uses TriMesh2D fixtures from simple_meshes and runs the full pipeline
(compute_unaugmented_contour_tree) to get real supernodes and superarcs,
then checks the persistence pairs produced.
"""

import pytest
from datasets.synthetic.simple_meshes import (
    single_peak,
    two_peaks_merge,
    three_peaks_merge,
)
from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree
from src.contour_tree_algo.persistence import compute_persistence_pairs


class TestPersistencePairs:
    """Persistence pairs on small TriMesh2D fixtures."""

    def test_empty_superarcs_returns_empty(self):
        """No superarcs means no leaves — result must be empty list."""
        result = compute_persistence_pairs([], [], lambda v: 0.0)
        assert result == []

    def test_single_peak_path_tree(self):
        """
        single_peak: supernodes=[0,2], superarcs=[(0,2)].

        Both endpoints are leaves (degree 1). Each walks to the other end.
            leaf 0 -> saddle 2, persistence = |1.0 - 0.0| = 1.0
            leaf 2 -> saddle 0, persistence = |0.0 - 1.0| = 1.0

        Sorted by (persistence, leaf_id): [(0,2,1.0), (2,0,1.0)]
        """
        mesh = single_peak()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        assert len(pairs) == 2
        assert pairs[0] == (0, 2, 1.0)
        assert pairs[1] == (2, 0, 1.0)

    def test_two_peaks_merge_y_shape(self):
        """
        two_peaks_merge: supernodes=[0,1,2,3], saddle=1 (degree 3).
        Leaves: 0 (val=0.1), 2 (val=0.8), 3 (val=0.9).

            leaf 2 -> saddle 1, persistence = |0.5 - 0.8| = 0.3
            leaf 0 -> saddle 1, persistence = |0.5 - 0.1| = 0.4
            leaf 3 -> saddle 1, persistence = |0.5 - 0.9| = 0.4

        Sorted by (persistence, leaf_id): [(2,1,0.3), (0,1,0.4), (3,1,0.4)]
        """
        mesh = two_peaks_merge()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        assert len(pairs) == 3
        assert pairs[0] == (2, 1, pytest.approx(0.3))
        assert pairs[1] == (0, 1, pytest.approx(0.4))
        assert pairs[2] == (3, 1, pytest.approx(0.4))

    def test_three_peaks_merge_star(self):
        """
        three_peaks_merge: supernodes=[0,1,2,3,4], saddle=1 (degree 4).
        Leaves: 0 (val=0.1), 2 (val=0.8), 3 (val=0.9), 4 (val=1.0).

            leaf 2 -> saddle 1, persistence = |0.5 - 0.8| = 0.3
            leaf 0 -> saddle 1, persistence = |0.5 - 0.1| = 0.4
            leaf 3 -> saddle 1, persistence = |0.5 - 0.9| = 0.4
            leaf 4 -> saddle 1, persistence = |0.5 - 1.0| = 0.5

        Sorted: [(2,1,0.3), (0,1,0.4), (3,1,0.4), (4,1,0.5)]
        """
        mesh = three_peaks_merge()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        assert len(pairs) == 4
        assert pairs[0] == (2, 1, pytest.approx(0.3))
        assert pairs[1] == (0, 1, pytest.approx(0.4))
        assert pairs[2] == (3, 1, pytest.approx(0.4))
        assert pairs[3] == (4, 1, pytest.approx(0.5))

    def test_sort_order_ascending_persistence(self):
        """Pairs must be sorted ascending by persistence."""
        mesh = three_peaks_merge()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        persistences = [p for _, _, p in pairs]
        assert persistences == sorted(persistences)
