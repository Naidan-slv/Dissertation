"""Tests for isosurface payload export."""

from src.visualization.isosurface_payload import build_isosurface_payload


def test_empty_payload_has_no_points_or_faces():
    payload = build_isosurface_payload([], [], isovalue=0.5)

    assert payload["points"] == []
    assert payload["faces"] == []
    assert payload["triangle_count"] == 0


def test_single_triangle_payload_keeps_xyz_points_and_face():
    vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    triangles = [(0, 1, 2)]

    payload = build_isosurface_payload(vertices, triangles, isovalue=0.5)

    assert payload["points"] == [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    assert payload["faces"] == [[0, 1, 2]]
    assert payload["triangle_count"] == 1
