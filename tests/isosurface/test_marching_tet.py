"""
Tests for marching tetrahedra.
"""

import pytest

from src.isosurface.marching_tet import interpolate_edge, tetrahedron_triangles


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


class TestTetrahedronSingleTriangle:
    """One vertex on one side of the isovalue gives one triangle."""

    def test_midpoint_iso_yields_geometric_midpoint(self):
        point = interpolate_edge((0, 0, 0), (1, 0, 0), 0.0, 1.0, 0.5)

        assert point == pytest.approx((0.5, 0.0, 0.0))

    def test_single_vertex_above_produces_one_triangle(self):
        points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
        values = [1.0, 0.0, 0.0, 0.0]

        triangles = tetrahedron_triangles(points, values, 0.5)

        assert len(triangles) == 1
        assert len(triangles[0]) == 3
