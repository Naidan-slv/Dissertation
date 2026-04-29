"""Tests for Carr §10.8 approximate superarc measures."""

import numpy as np
import pytest

from src.contour_tree_algo.measures import (
    compute_arc_measures,
    reduce_with_superarc_vertices,
)
from src.meshes.grid_mesh_3d import GridMesh3D
from src.meshes.mesh2d import TriMesh2D


def _arc(a, b):
    return tuple(sorted((a, b)))


class TestSuperarcReduction:
    """Reduced superarcs keep the regular vertices on their augmented paths."""

    def test_reduction_keeps_absorbed_vertices(self):
        ct_edges = [(0, 4), (4, 2), (1, 2), (2, 5), (5, 3)]

        supernodes, superarcs, paths = reduce_with_superarc_vertices(ct_edges)

        assert sorted(supernodes) == [0, 1, 2, 3]
        assert {_arc(*edge) for edge in superarcs} == {
            (0, 2),
            (1, 2),
            (2, 3),
        }
        assert set(paths[(0, 2)]) == {0, 4, 2}
        assert set(paths[(1, 2)]) == {1, 2}
        assert set(paths[(2, 3)]) == {2, 5, 3}


class TestArcMeasures:
    """Carr §10.8 approximations on small hand-checked meshes."""

    def test_one_measure_per_superarc(self):
        values = {0: 0.0, 1: 5.0, 2: 10.0, 3: 3.0, 4: 2.0}
        mesh = TriMesh2D(values, [(0, 1, 2), (1, 4, 3)])
        ct_edges = [(0, 1), (1, 2), (1, 4), (4, 3)]

        measures = compute_arc_measures(mesh, ct_edges)

        assert set(measures) == {(0, 1), (1, 2), (1, 3)}

    def test_hand_computed_chain_measure(self):
        values = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
        mesh = TriMesh2D(values, [(0, 1, 2), (1, 2, 3)])
        ct_edges = [(0, 1), (1, 2), (2, 3)]

        measures = compute_arc_measures(mesh, ct_edges)
        measure = measures[(0, 3)]

        assert measure.sample_vertices == (0, 1, 2, 3)
        assert measure.node_count == 4
        assert measure.scalar_sum == pytest.approx(6.0)
        assert measure.scalar_square_sum == pytest.approx(14.0)
        assert measure.cell_crossing_count == 2

    def test_symmetric_branches_have_equal_measures(self):
        values = {
            0: 0.0,
            1: 0.0,
            2: 1.0,
            3: 2.0,
            4: 0.5,
            5: 0.5,
        }
        mesh = TriMesh2D(values, [(0, 4, 2), (1, 5, 2), (2, 5, 3)])
        ct_edges = [(0, 4), (4, 2), (1, 5), (5, 2), (2, 3)]

        measures = compute_arc_measures(mesh, ct_edges)
        left = measures[(0, 2)]
        right = measures[(1, 2)]

        assert left.node_count == right.node_count
        assert left.scalar_sum == pytest.approx(right.scalar_sum)
        assert left.scalar_square_sum == pytest.approx(right.scalar_square_sum)
        assert left.cell_crossing_count == right.cell_crossing_count

    def test_grid_3d_freudenthal_cell_crossing_count_is_nonzero(self):
        data = np.arange(8, dtype=float)
        mesh = GridMesh3D(width=2, height=2, depth=2, data=data, freudenthal=True)

        measures = compute_arc_measures(mesh, [(0, 7)])

        assert measures[(0, 7)].cell_crossing_count == 6

    def test_scalar_range_vertices_from_other_superarcs_are_not_counted(self):
        values = {0: 0.0, 1: 5.0, 2: 10.0, 3: 3.0, 4: 2.0}
        mesh = TriMesh2D(values, [(0, 1, 2), (1, 4, 3)])
        ct_edges = [(0, 1), (1, 2), (1, 4), (4, 3)]

        measures = compute_arc_measures(mesh, ct_edges)
        measure = measures[(0, 1)]

        assert measure.sample_vertices == (0, 1)
        assert measure.node_count == 2
        assert 3 not in measure.sample_vertices
        assert 4 not in measure.sample_vertices
        assert measure.scalar_sum == pytest.approx(5.0)
