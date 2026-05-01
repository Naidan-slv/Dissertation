"""Tests for contour-tree payloads used by the viewer."""

from src.visualization.contour_tree_payload import build_contour_tree_payload


def test_contour_tree_payload_records_nodes_and_edges():
    values = {8: 0.0, 16: 30.0, 23: 100.0}

    payload = build_contour_tree_payload(
        supernodes=[8, 16, 23],
        superarcs=[(8, 16), (16, 23)],
        value_fn=values.__getitem__,
    )

    assert payload["nodes"] == [
        {"id": 8, "value": 0.0, "kind": "min"},
        {"id": 16, "value": 30.0, "kind": "saddle"},
        {"id": 23, "value": 100.0, "kind": "max"},
    ]
    assert payload["edges"] == [
        {"source": 8, "target": 16, "value_range": [0.0, 30.0], "active": False},
        {"source": 16, "target": 23, "value_range": [30.0, 100.0], "active": False},
    ]


def test_contour_tree_payload_marks_active_arc_for_isovalue():
    values = {8: 0.0, 16: 30.0, 23: 100.0}

    payload = build_contour_tree_payload(
        [8, 16, 23],
        [(8, 16), (16, 23)],
        values.__getitem__,
        isovalue=25.0,
    )

    assert [edge["active"] for edge in payload["edges"]] == [True, False]