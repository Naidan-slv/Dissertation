"""
Tests for marching tetrahedra.
"""

from src.isosurface.marching_tet import tetrahedron_triangles


class TestTetrahedronEmptyCases:
    """Cases where no isosurface crosses the tetrahedron."""

    def test_all_below_produces_no_triangles(self):
        points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
        values = [0.0, 0.1, 0.2, 0.3]

        assert tetrahedron_triangles(points, values, 0.5) == []

    def test_all_above_produces_no_triangles(self):
        points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
        values = [0.6, 0.7, 0.8, 0.9]

        assert tetrahedron_triangles(points, values, 0.5) == []
