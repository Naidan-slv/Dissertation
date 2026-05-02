"""Smoke tests for the interactive viewer example script."""

import sys

from scripts.interactive_viewer_example import build_example_inputs, build_example_viewer
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


def test_example_inputs_use_tiny_grid_and_interval_tree():
    inputs = build_example_inputs()

    assert inputs["dataset_name"] == "tiny-interactive-example"
    assert inputs["initial_isovalue"] == 0.5
    assert inputs["supernodes"] == [0, 1]
    assert inputs["superarcs"] == [(0, 1)]


def test_example_viewer_builds_without_opening_window(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", FakePyVista())

    plotter = build_example_viewer()

    payload = current_viewer_payload(plotter)
    assert payload["dataset_name"] == "tiny-interactive-example"
    assert payload["summary"]["active_arc_count"] == 1
    assert plotter.slider_widgets[0][1]["title"] == "isovalue"
