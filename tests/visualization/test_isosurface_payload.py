"""Tests for isosurface payload export."""

from src.visualization.isosurface_payload import (
    VIEWER_PAYLOAD_SCHEMA_VERSION,
    build_isosurface_payload,
)


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


def test_payload_has_schema_version_and_dataset_name():
    payload = build_isosurface_payload([], [], isovalue=0.5, dataset_name="demo")

    assert payload["schema_version"] == VIEWER_PAYLOAD_SCHEMA_VERSION
    assert payload["dataset_name"] == "demo"
