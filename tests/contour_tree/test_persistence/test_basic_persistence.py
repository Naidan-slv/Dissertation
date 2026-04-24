"""
Tests for compute_persistence_pairs.

Uses TriMesh2D fixtures from simple_meshes and runs the full pipeline
(compute_unaugmented_contour_tree) to get real supernodes and superarcs,
then checks the persistence pairs produced.
"""

import pytest
from datasets.synthetic.carr_9x9_mesh import create_carr_9x9_mesh
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

    def test_single_peak_path_tree_has_one_pair(self):
        """
        single_peak: supernodes=[0,2], superarcs=[(0,2)].

        A one-edge tree is one essential min-max branch, so it gives one pair.
        """
        mesh = single_peak()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        assert len(pairs) == 1
        assert pairs[0].leaf == 0
        assert pairs[0].saddle == 2
        assert pairs[0].persistence == 1.0
        assert pairs[0].direction == "min"
        assert pairs[0].path == (0, 2)

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
        assert pairs[0].leaf == 2
        assert pairs[0].saddle == 1
        assert pairs[0].persistence == pytest.approx(0.3)
        assert pairs[0].direction == "max"
        assert pairs[0].path == (2, 1)
        assert pairs[1].leaf == 0
        assert pairs[1].saddle == 1
        assert pairs[1].persistence == pytest.approx(0.4)
        assert pairs[1].direction == "min"
        assert pairs[2].leaf == 3
        assert pairs[2].saddle == 1
        assert pairs[2].persistence == pytest.approx(0.4)
        assert pairs[2].direction == "max"

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
        assert [p.leaf for p in pairs] == [2, 0, 3, 4]
        assert [p.saddle for p in pairs] == [1, 1, 1, 1]
        assert [p.persistence for p in pairs] == [
            pytest.approx(0.3),
            pytest.approx(0.4),
            pytest.approx(0.4),
            pytest.approx(0.5),
        ]
        assert [p.direction for p in pairs] == ["max", "min", "max", "max"]

    def test_sort_order_ascending_persistence(self):
        """Pairs must be sorted ascending by persistence."""
        mesh = three_peaks_merge()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        persistences = [pair.persistence for pair in pairs]
        assert persistences == sorted(persistences)

    def test_stable_ordering_uses_value_then_leaf_id(self):
        """Equal persistence pairs are ordered by leaf value, then leaf id."""
        supernodes = [0, 1, 2, 3]
        superarcs = [(0, 1), (1, 2), (1, 3)]
        values = {0: 0.1, 1: 0.5, 2: 0.9, 3: 0.9}

        pairs = compute_persistence_pairs(supernodes, superarcs, values.__getitem__)

        assert [pair.leaf for pair in pairs] == [0, 2, 3]
        assert [pair.persistence for pair in pairs] == [
            pytest.approx(0.4),
            pytest.approx(0.4),
            pytest.approx(0.4),
        ]

    def test_carr_9x9_persistence_values(self):
        """Carr 9x9 paper example gives the hand-checked leaf-saddle differences."""
        mesh = create_carr_9x9_mesh()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)

        pairs = compute_persistence_pairs(supernodes, superarcs, mesh.value)

        assert [(p.leaf, p.saddle, p.persistence, p.direction) for p in pairs] == [
            (50, 43, 9, "max"),
            (23, 16, 10, "min"),
            (51, 43, 10, "min"),
            (8, 16, 30, "min"),
            (29, 47, 30, "max"),
            (55, 47, 50, "max"),
        ]

    def test_symmetric_field_has_symmetric_persistence(self):
        """Symmetric leaves around one saddle keep equal persistence values."""
        supernodes = [0, 1, 2, 3, 4]
        superarcs = [(0, 1), (1, 2), (1, 3), (1, 4)]
        values = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.0, 4: 0.0}

        pairs = compute_persistence_pairs(supernodes, superarcs, values.__getitem__)

        assert [pair.persistence for pair in pairs] == [
            pytest.approx(0.5),
            pytest.approx(0.5),
            pytest.approx(0.5),
            pytest.approx(0.5),
        ]
        assert [pair.direction for pair in pairs] == ["min", "min", "max", "max"]
