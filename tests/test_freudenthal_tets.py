"""
Tests for Freudenthal tetrahedra on regular 3D grids.
"""

from src.meshes.freudenthal_tets import cube_tetrahedra, enumerate_tetrahedra


class TestCubeTetrahedra:
    """One-cube Freudenthal pattern."""

    def test_one_cube_has_six_tetrahedra(self):
        tets = cube_tetrahedra(0, 1, 2, 3, 4, 5, 6, 7)

        assert len(tets) == 6

    def test_each_tet_uses_major_diagonal(self):
        tets = cube_tetrahedra(0, 1, 2, 3, 4, 5, 6, 7)

        assert all(0 in tet and 7 in tet for tet in tets)


class TestEnumerateTetrahedra:
    """Freudenthal tetrahedra over whole grids."""

    def test_2x2x2_grid_has_six_tetrahedra(self):
        tets = enumerate_tetrahedra(2, 2, 2)

        assert len(tets) == 6

    def test_3x3x3_grid_has_48_tetrahedra(self):
        tets = enumerate_tetrahedra(3, 3, 3)

        assert len(tets) == 48
