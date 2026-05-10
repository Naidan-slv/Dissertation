"""Smoke test for the non-GUI viewer payload example."""

from scripts.viewer_payload_example import build_example_payload


def test_example_payload_can_be_built_without_pyvista():
    payload = build_example_payload()

    assert payload["dataset_name"] == "tiny-example"
    assert payload["isovalue"] == 0.5
    assert payload["isosurface"]["triangle_count"] > 0
    assert payload["contour_tree"]["edges"][0]["active"] is True
