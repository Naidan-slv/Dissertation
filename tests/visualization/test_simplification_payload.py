"""Tests for simplification context in viewer payloads."""

import json

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.simplification_payload import build_simplification_payload
from src.visualization.viewer_payload import build_viewer_payload


TREE = [(0, 1), (1, 2), (1, 3)]
VALUES = {0: 0.0, 1: 5.0, 2: 10.0, 3: 6.0}


def test_simplification_payload_records_tree_context():
    payload = build_simplification_payload(
        supernodes=[0, 1, 2, 3],
        superarcs=TREE,
        value_fn=VALUES.__getitem__,
        isovalue=4.0,
        mode="height",
        threshold=1.0,
    )

    assert payload["mode"] == "height"
    assert payload["threshold"] == 1.0
    assert payload["target_edge_count"] is None
    assert payload["component_mapping"] == "interval-only"
    assert payload["original_edge_count"] == 3
    assert payload["simplified_edge_count"] == 1
    assert payload["collapse_record_count"] == 2
    assert payload["active_edge_count"] == 1
    assert payload["simplified_tree"]["edges"][0]["active_at_isovalue"] is True


def test_simplification_payload_includes_json_friendly_collapse_records():
    payload = build_simplification_payload(
        [0, 1, 2, 3],
        TREE,
        VALUES.__getitem__,
        mode="height",
        threshold=1.0,
    )

    vertex_record, leaf_record = payload["collapse_records"]
    assert vertex_record["kind"] == "vertex_collapse"
    assert vertex_record["collapsed_vertex"] == 1
    assert leaf_record["kind"] == "leaf_prune"
    assert leaf_record["removed_edges"] == [2]
    assert leaf_record["leaf"] == 3
    assert json.loads(json.dumps(payload))["collapse_record_count"] == 2


def test_simplification_payload_carries_target_edge_count():
    payload = build_simplification_payload(
        [0, 1, 2, 3],
        TREE,
        VALUES.__getitem__,
        mode="height",
        target_edges=2,
    )

    assert payload["target_edge_count"] == 2
    assert payload["simplified_edge_count"] <= 2


def test_threshold_zero_one_edge_tree_is_no_op():
    payload = build_simplification_payload(
        [0, 1],
        [(0, 1)],
        {0: 0.0, 1: 1.0}.__getitem__,
        mode="height",
        threshold=0.0,
    )

    assert payload["original_edge_count"] == 1
    assert payload["simplified_edge_count"] == 1
    assert payload["collapse_record_count"] == 0
    assert payload["simplified_tree"]["edges"] == [
        {
            "source": 0,
            "target": 1,
            "value_range": [0.0, 1.0],
            "active": False,
            "active_at_isovalue": False,
        }
    ]


def test_viewer_payload_simplification_block_is_json_serialisable():
    data = np.zeros(8)
    data[1] = 1.0
    mesh = GridMesh3D(2, 2, 2, data)

    payload = build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1, 2, 3],
        superarcs=TREE,
        value_fn=VALUES.__getitem__,
        isovalue=0.5,
        simplification={"mode": "height", "threshold": 1.0},
    )

    assert json.loads(json.dumps(payload))["simplification"]["collapse_record_count"] == 2


def test_simplification_block_does_not_change_isosurface_payload():
    data = np.zeros(8)
    data[1] = 1.0
    mesh = GridMesh3D(2, 2, 2, data)

    plain = build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1, 2, 3],
        superarcs=TREE,
        value_fn=VALUES.__getitem__,
        isovalue=0.5,
    )
    simplified = build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1, 2, 3],
        superarcs=TREE,
        value_fn=VALUES.__getitem__,
        isovalue=0.5,
        simplification={"mode": "height", "threshold": 1.0},
    )

    assert simplified["isosurface"] == plain["isosurface"]


def test_viewer_payload_can_include_simplification_block():
    data = np.zeros(8)
    data[1] = 1.0
    mesh = GridMesh3D(2, 2, 2, data)

    payload = build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1],
        superarcs=[(0, 1)],
        isovalue=0.5,
        simplification={"mode": "height", "threshold": 0.0},
    )

    assert payload["simplification"]["mode"] == "height"
    assert payload["simplification"]["simplified_edge_count"] == 1
    assert payload["contour_tree"]["edges"][0]["active_at_isovalue"] is True
