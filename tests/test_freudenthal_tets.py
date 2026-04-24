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

    def test_every_tet_has_four_unique_vertices(self):
        tets = enumerate_tetrahedra(3, 3, 3)

        assert all(len(set(tet)) == 4 for tet in tets)

    def test_no_duplicate_tetrahedra(self):
        tets = enumerate_tetrahedra(3, 3, 3)
        normalised = [tuple(sorted(tet)) for tet in tets]

        assert len(normalised) == len(set(normalised))

    def test_output_is_deterministic(self):
        assert enumerate_tetrahedra(3, 3, 3) == enumerate_tetrahedra(3, 3, 3)

    def test_one_cube_edges_match_14_connected_pattern(self):
        tets = cube_tetrahedra(0, 1, 2, 3, 4, 5, 6, 7)
        edges = set()
        for tet in tets:
            for i, u in enumerate(tet):
                for v in tet[i + 1:]:
                    edges.add(tuple(sorted((u, v))))

        assert edges == {
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
            (1, 3), (1, 5), (1, 7),
            (2, 3), (2, 6), (2, 7),
            (3, 7),
            (4, 5), (4, 6), (4, 7),
            (5, 7),
            (6, 7),
        }
