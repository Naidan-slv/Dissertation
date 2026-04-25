"""
Tests for marching tetrahedra.
"""

import pytest

from src.isosurface.marching_tet import (
    extract_isosurface,
    interpolate_edge,
    tetrahedron_triangles,
)


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


class TestTetrahedronTwoTriangles:
    """Two vertices on each side gives two triangles."""

    def test_two_vertices_above_produces_two_triangles(self):
        points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
        values = [1.0, 1.0, 0.0, 0.0]

        triangles = tetrahedron_triangles(points, values, 0.5)

        assert len(triangles) == 2
        assert all(len(triangle) == 3 for triangle in triangles)


class TestExtractIsosurface:
    """Grid-level marching tetrahedra extraction."""

    def test_grid_extraction_returns_vertices_and_triangles(self):
        data = [0, 0, 0, 0, 1, 1, 1, 1]

        vertices, triangles = extract_isosurface(2, 2, 2, data, 0.5)

        assert vertices
        assert triangles

    def test_closed_surface_euler_sanity(self):
        data = [1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1]
        data[21] = 0
        data[22] = 0
        data[25] = 0
        data[26] = 0
        data[37] = 0
        data[38] = 0
        data[41] = 0
        data[42] = 0

        vertices, triangles = extract_isosurface(4, 4, 4, data, 0.5)
        edges = set()
        for a, b, c in triangles:
            edges.add(tuple(sorted((a, b))))
            edges.add(tuple(sorted((b, c))))
            edges.add(tuple(sorted((a, c))))

        assert len(vertices) - len(edges) + len(triangles) == 2
