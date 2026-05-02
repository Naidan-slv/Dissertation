"""Tests for the high-level interactive viewer wiring."""

import sys

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.interactive_viewer import build_interactive_viewer, show_interactive_viewer


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
        self.show_calls = []
        self.axes_shown = False

    def add_mesh(self, mesh, **kwargs):
        self.meshes.append((mesh, kwargs))

    def add_slider_widget(self, callback, **kwargs):
        self.slider_widgets.append((callback, kwargs))

    def show_axes(self):
        self.axes_shown = True

    def show(self):
        self.show_calls.append({})


def tiny_grid_mesh():
    data = np.zeros(8)
    data[1] = 1.0
    return GridMesh3D(2, 2, 2, data)


def test_build_interactive_viewer_links_grid_surface_and_tree(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", FakePyVista())

    plotter = build_interactive_viewer(
        mesh=tiny_grid_mesh(),
        supernodes=[0, 1],
        superarcs=[(0, 1)],
        initial_isovalue=0.25,
        dataset_name="tiny interactive",
    )

    callback, slider_kwargs = plotter.slider_widgets[0]
    callback(0.75)

    assert slider_kwargs == {"rng": (0.0, 1.0), "value": 0.25, "title": "isovalue"}
    assert plotter.viewer_payload["dataset_name"] == "tiny interactive"
    assert plotter.viewer_payload["isovalue"] == 0.75
    assert plotter.viewer_payload["component_mapping"] == "interval-only"
    assert plotter.viewer_payload["contour_tree"]["edges"][0]["active_at_isovalue"] is True
    assert plotter.meshes[-1][1]["name"] == "isosurface"


def test_show_interactive_viewer_calls_show_after_build(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", FakePyVista())

    plotter = show_interactive_viewer(
        mesh=tiny_grid_mesh(),
        supernodes=[0, 1],
        superarcs=[(0, 1)],
        initial_isovalue=0.5,
    )

    assert plotter.show_calls == [{}]
    assert plotter.viewer_payload["isovalue"] == 0.5
