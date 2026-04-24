"""
Tests for Freudenthal tetrahedra on regular 3D grids.
"""

from src.meshes.freudenthal_tets import cube_tetrahedra


class TestCubeTetrahedra:
    """One-cube Freudenthal pattern."""

    def test_one_cube_has_six_tetrahedra(self):
        tets = cube_tetrahedra(0, 1, 2, 3, 4, 5, 6, 7)

        assert len(tets) == 6

    def test_each_tet_uses_major_diagonal(self):
        tets = cube_tetrahedra(0, 1, 2, 3, 4, 5, 6, 7)

        assert all(0 in tet and 7 in tet for tet in tets)
