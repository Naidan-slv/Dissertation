"""Tests for isosurface payload export."""

import json

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.isosurface_payload import (
    VIEWER_PAYLOAD_SCHEMA_VERSION,
    build_isosurface_payload,
    extract_isosurface_payload,
    extract_grid_mesh_payload,
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


def test_payload_records_scalar_range_and_is_json_serialisable():
    payload = build_isosurface_payload([], [], isovalue=0.5, scalar_range=(0.0, 1.0))

    assert payload["scalar_range"] == [0.0, 1.0]
    assert json.loads(json.dumps(payload))["isovalue"] == 0.5


def test_payload_bounds_are_computed_from_points():
    payload = build_isosurface_payload(
        [(0.0, 0.0, 0.0), (1.0, 2.0, 3.0), (-1.0, 0.0, 2.0)],
        [(0, 1, 2)],
        isovalue=0.5,
    )

    assert payload["bounds"] == {"x": [-1.0, 1.0], "y": [0.0, 2.0], "z": [0.0, 3.0]}


def test_repeated_coordinates_are_deduplicated_in_first_seen_order():
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 0, 0)]
    triangles = [(0, 1, 2), (0, 3, 2)]

    payload = build_isosurface_payload(vertices, triangles, isovalue=0.5)

    assert payload["points"] == [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    assert payload["faces"] == [[0, 1, 2], [0, 1, 2]]


def test_degenerate_triangles_are_dropped():
    vertices = [(0, 0, 0), (1, 0, 0)]
    triangles = [(0, 1, 1)]

    payload = build_isosurface_payload(vertices, triangles, isovalue=0.5)

    assert payload["faces"] == []
    assert payload["triangle_count"] == 0


def test_extracted_payload_records_range_even_when_surface_is_empty():
    payload = extract_isosurface_payload(
        width=2,
        height=2,
        depth=2,
        data=[0.0] * 8,
        isovalue=1.0,
        dataset_name="flat cube",
    )

    assert payload["dataset_name"] == "flat cube"
    assert payload["scalar_range"] == [0.0, 0.0]
    assert payload["points"] == []
    assert payload["triangle_count"] == 0


def test_extracted_payload_keeps_grid_xyz_order():
    data = [0.0] * 8
    data[1] = 1.0  # vertex (x=1, y=0, z=0)

    payload = extract_isosurface_payload(2, 2, 2, data, isovalue=0.5)

    assert payload["triangle_count"] > 0
    assert payload["bounds"] == {"x": [0.5, 1.0], "y": [0.0, 0.5], "z": [0.0, 0.5]}


def test_grid_mesh_payload_uses_project_grid_mesh_values():
    data = np.zeros(8)
    data[1] = 1.0
    mesh = GridMesh3D(2, 2, 2, data)

    payload = extract_grid_mesh_payload(mesh, isovalue=0.5, dataset_name="grid mesh")

    assert payload["dataset_name"] == "grid mesh"
    assert payload["scalar_range"] == [0.0, 1.0]
    assert payload["bounds"] == {"x": [0.5, 1.0], "y": [0.0, 0.5], "z": [0.0, 0.5]}
