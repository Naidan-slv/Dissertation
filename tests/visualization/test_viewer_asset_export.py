"""Tests for repeatable viewer asset export."""

import json

import numpy as np

from scripts.export_viewer_assets import (
    asset_paths,
    build_parser,
    export_viewer_assets,
    main,
)
from src.meshes.grid_mesh_3d import GridMesh3D


def tiny_grid_mesh():
    data = np.zeros(8)
    data[1] = 1.0
    return GridMesh3D(2, 2, 2, data)


def tiny_tree(_mesh):
    return [0, 1], [(0, 1)]


def test_parser_defaults_to_fuel_export():
    args = build_parser().parse_args([])

    assert args.dataset == "fuel"
    assert args.isovalue is None
    assert args.threshold is None
    assert args.output_dir == "output/viewer"
    assert args.no_freudenthal is False


def test_asset_paths_are_dataset_specific(tmp_path):
    payload_path, manifest_path, dot_path = asset_paths(tmp_path, "fuel")

    assert payload_path == tmp_path / "fuel_viewer_payload.json"
    assert manifest_path == tmp_path / "fuel_viewer_manifest.json"
    assert dot_path == tmp_path / "fuel_contour_tree.dot"


def test_export_viewer_assets_writes_payload_and_manifest(tmp_path):
    result = export_viewer_assets(
        "tiny",
        isovalue=0.5,
        threshold=0.25,
        output_dir=tmp_path,
        loader=lambda *_args, **_kwargs: tiny_grid_mesh(),
        contour_tree_fn=tiny_tree,
        command=["export", "tiny"],
    )

    payload_path = tmp_path / "tiny_viewer_payload.json"
    manifest_path = tmp_path / "tiny_viewer_manifest.json"
    dot_path = tmp_path / "tiny_contour_tree.dot"
    assert result == {
        "viewer_payload": payload_path,
        "manifest": manifest_path,
        "dot_graph": dot_path,
    }

    payload = json.loads(payload_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    dot_text = dot_path.read_text()

    assert payload["dataset_name"] == "tiny"
    assert payload["isovalue"] == 0.5
    assert payload["component_mapping"] == "interval-only"
    assert payload["isosurface"]["triangle_count"] > 0
    assert payload["simplification"]["threshold"] == 0.25

    assert manifest["schema_version"] == "viewer-assets-manifest-v1"
    assert manifest["dataset"] == "tiny"
    assert manifest["isovalue"] == 0.5
    assert manifest["simplification_threshold"] == 0.25
    assert manifest["component_mapping"] == "interval-only"
    assert manifest["outputs"] == {
        "viewer_payload": str(payload_path),
        "manifest": str(manifest_path),
        "dot_graph": str(dot_path),
        "screenshot": None,
    }
    assert manifest["command"] == ["export", "tiny"]
    assert "Carr" in manifest["paper_basis"]["contour_tree"]
    assert "marching tetrahedra" in manifest["paper_basis"]["isosurface"]
    assert "graph contour_tree" in dot_text
    assert "color=gold" in dot_text


def test_export_viewer_assets_dot_uses_interval_highlighting(tmp_path):
    export_viewer_assets(
        "tiny",
        isovalue=0.5,
        output_dir=tmp_path,
        loader=lambda *_args, **_kwargs: tiny_grid_mesh(),
        contour_tree_fn=tiny_tree,
    )

    dot_text = (tmp_path / "tiny_contour_tree.dot").read_text()

    assert "0 -- 1 [color=gold penwidth=3];" in dot_text


def test_export_viewer_assets_uses_midpoint_isovalue_by_default(tmp_path):
    export_viewer_assets(
        "tiny",
        output_dir=tmp_path,
        loader=lambda *_args, **_kwargs: tiny_grid_mesh(),
        contour_tree_fn=tiny_tree,
    )

    payload = json.loads((tmp_path / "tiny_viewer_payload.json").read_text())

    assert payload["isovalue"] == 0.5


def test_main_passes_cli_options_to_exporter(monkeypatch):
    calls = []

    def fake_export(**kwargs):
        calls.append(kwargs)
        return {"viewer_payload": "payload.json", "manifest": "manifest.json"}

    monkeypatch.setattr("scripts.export_viewer_assets.export_viewer_assets", fake_export)

    result = main(["nucleon", "--isovalue", "42", "--threshold", "3", "--output-dir", "out", "--no-freudenthal"])

    assert result == {"viewer_payload": "payload.json", "manifest": "manifest.json"}
    assert calls == [
        {
            "dataset_name": "nucleon",
            "isovalue": 42.0,
            "threshold": 3.0,
            "output_dir": "out",
            "freudenthal": False,
            "command": [
                "scripts/export_viewer_assets.py",
                "nucleon",
                "--isovalue",
                "42",
                "--threshold",
                "3",
                "--output-dir",
                "out",
                "--no-freudenthal",
            ],
        }
    ]