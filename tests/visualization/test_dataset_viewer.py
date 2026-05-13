"""Tests for dataset-backed interactive viewer inputs."""

import sys

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.dataset_viewer import (
    build_grid_viewer_inputs,
    build_klacansky_viewer,
    build_klacansky_viewer_inputs,
    build_raw_file_viewer_inputs,
)
from src.visualization.interactive_viewer import current_viewer_payload


class FakePyVista:
    def __init__(self):
        self.plotters = []

    def PolyData(self, points, faces):
        return {"points": points, "faces": faces}

    def Plotter(self, **kwargs):
        plotter = FakePlotter(**kwargs)
        self.plotters.append(plotter)
        return plotter


class FakePlotter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.meshes = []
        self.slider_widgets = []
        self.axes_shown = False

    def add_mesh(self, mesh, **kwargs):
        self.meshes.append((mesh, kwargs))

    def add_slider_widget(self, callback, **kwargs):
        self.slider_widgets.append((callback, kwargs))

    def show_axes(self):
        self.axes_shown = True


def tiny_grid_mesh():
    data = np.zeros(8)
    data[1] = 1.0
    return GridMesh3D(2, 2, 2, data)


def tiny_tree(_mesh):
    return [0, 1], [(0, 1)]


def test_grid_viewer_inputs_choose_midpoint_isovalue():
    inputs = build_grid_viewer_inputs(
        tiny_grid_mesh(),
        dataset_name="tiny grid",
        contour_tree_fn=tiny_tree,
    )

    assert inputs["dataset_name"] == "tiny grid"
    assert inputs["supernodes"] == [0, 1]
    assert inputs["superarcs"] == [(0, 1)]
    assert inputs["initial_isovalue"] == 0.5


def test_grid_viewer_inputs_allow_explicit_isovalue():
    inputs = build_grid_viewer_inputs(
        tiny_grid_mesh(),
        initial_isovalue=0.25,
        contour_tree_fn=tiny_tree,
    )

    assert inputs["initial_isovalue"] == 0.25


def test_klacansky_viewer_inputs_use_named_dataset_loader():
    calls = []

    def fake_loader(name, freudenthal=True):
        calls.append((name, freudenthal))
        return tiny_grid_mesh()

    inputs = build_klacansky_viewer_inputs(
        "fuel",
        loader=fake_loader,
        contour_tree_fn=tiny_tree,
        freudenthal=False,
    )

    assert calls == [("fuel", False)]
    assert inputs["dataset_name"] == "fuel"
    assert inputs["initial_isovalue"] == 0.5


def test_raw_file_viewer_inputs_use_single_file_loader(monkeypatch):
    calls = []

    def fake_single_file_loader(file_path, shape_whd, dtype):
        calls.append((file_path, shape_whd, dtype))
        data = np.zeros(8)
        data[1] = 1.0
        return data, 2, 2, 2

    monkeypatch.setattr(
        "src.visualization.dataset_viewer.load_raw_volume_single_file",
        fake_single_file_loader,
    )

    inputs = build_raw_file_viewer_inputs(
        "volumes/demo.raw",
        (2, 2, 2),
        dtype="uint16",
        freudenthal=False,
        contour_tree_fn=tiny_tree,
    )

    assert calls == [("volumes/demo.raw", (2, 2, 2), "uint16")]
    assert inputs["dataset_name"] == "volumes/demo.raw"
    assert inputs["initial_isovalue"] == 0.5


def test_build_klacansky_viewer_returns_slider_plotter(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", FakePyVista())

    plotter = build_klacansky_viewer(
        "fuel",
        loader=lambda *_args, **_kwargs: tiny_grid_mesh(),
        contour_tree_fn=tiny_tree,
    )

    payload = current_viewer_payload(plotter)
    assert payload["dataset_name"] == "fuel"
    assert payload["component_mapping"] == "interval-only"
    assert plotter.slider_widgets[0][1]["title"] == "isovalue"
