"""Tests for combined viewer payloads."""

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.viewer_payload import build_viewer_payload


def test_viewer_payload_uses_same_isovalue_for_surface_and_tree():
    data = np.zeros(8)
    data[1] = 1.0
    mesh = GridMesh3D(2, 2, 2, data)

    payload = build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1],
        superarcs=[(0, 1)],
        isovalue=0.5,
        dataset_name="tiny grid",
    )

    assert payload["isovalue"] == 0.5
    assert payload["isosurface"]["dataset_name"] == "tiny grid"
    assert payload["isosurface"]["triangle_count"] > 0
    assert payload["contour_tree"]["edges"] == [
        {"source": 0, "target": 1, "value_range": [0.0, 1.0], "active": True}
    ]
