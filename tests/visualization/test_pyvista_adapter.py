"""Tests for the optional PyVista payload adapter."""

import sys

import pytest

from src.visualization.pyvista_adapter import (
    build_isosurface_plotter,
    build_isovalue_slider_plotter,
    payload_to_polydata,
    require_pyvista,
    save_isosurface_screenshot,
)


class FakePyVista:
    def __init__(self):
        self.last_points = None
        self.last_faces = None
        self.plotters = []

    def PolyData(self, points, faces):
        self.last_points = points
        self.last_faces = faces
        return {"points": points, "faces": faces}

    def Plotter(self, **kwargs):
        plotter = FakePlotter(**kwargs)
        self.plotters.append(plotter)
        return plotter


class FakePlotter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.meshes = []
        self.axes_shown = False
        self.show_calls = []
        self.slider_widgets = []

    def add_mesh(self, mesh, **kwargs):
        self.meshes.append((mesh, kwargs))

    def show_axes(self):
        self.axes_shown = True

    def show(self, **kwargs):
        self.show_calls.append(kwargs)

    def add_slider_widget(self, callback, **kwargs):
        self.slider_widgets.append((callback, kwargs))


def test_require_pyvista_reports_missing_optional_dependency(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", None)

    with pytest.raises(RuntimeError, match="pip install pyvista"):
        require_pyvista()


def test_payload_to_polydata_uses_vtk_face_layout(monkeypatch):
    fake_pyvista = FakePyVista()
    monkeypatch.setitem(sys.modules, "pyvista", fake_pyvista)
    payload = {
        "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        "faces": [[0, 1, 2]],
    }

    mesh = payload_to_polydata(payload)

    assert mesh == {"points": payload["points"], "faces": [3, 0, 1, 2]}
    assert fake_pyvista.last_faces == [3, 0, 1, 2]


def test_payload_to_polydata_rejects_non_triangle_faces(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyvista", FakePyVista())
    payload = {"points": [], "faces": [[0, 1, 2, 3]]}

    with pytest.raises(ValueError, match="triangle faces"):
        payload_to_polydata(payload)


def test_build_isosurface_plotter_adds_mesh_without_showing_window(monkeypatch):
    fake_pyvista = FakePyVista()
    monkeypatch.setitem(sys.modules, "pyvista", fake_pyvista)
    payload = {
        "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        "faces": [[0, 1, 2]],
    }

    plotter = build_isosurface_plotter(payload)

    assert plotter is fake_pyvista.plotters[0]
    assert plotter.meshes[0][0] == {"points": payload["points"], "faces": [3, 0, 1, 2]}
    assert plotter.meshes[0][1] == {
        "color": "tomato",
        "show_edges": True,
        "opacity": 0.75,
        "name": "isosurface",
    }
    assert plotter.axes_shown is True


def test_save_isosurface_screenshot_uses_off_screen_plotter(monkeypatch, tmp_path):
    fake_pyvista = FakePyVista()
    monkeypatch.setitem(sys.modules, "pyvista", fake_pyvista)
    payload = {
        "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        "faces": [[0, 1, 2]],
    }
    out = tmp_path / "surface.png"

    result = save_isosurface_screenshot(payload, out)

    assert result == str(out)
    assert fake_pyvista.plotters[0].kwargs == {"off_screen": True}
    assert fake_pyvista.plotters[0].show_calls == [{"screenshot": str(out), "auto_close": True}]


def test_build_isovalue_slider_plotter_refreshes_surface(monkeypatch):
    fake_pyvista = FakePyVista()
    monkeypatch.setitem(sys.modules, "pyvista", fake_pyvista)

    def payload_builder(isovalue):
        return {
            "points": [[0.0, 0.0, 0.0], [float(isovalue), 0.0, 0.0], [0.0, 1.0, 0.0]],
            "faces": [[0, 1, 2]],
        }

    plotter = build_isovalue_slider_plotter(
        payload_builder,
        scalar_range=(0.0, 1.0),
        initial_isovalue=0.25,
    )

    callback, slider_kwargs = plotter.slider_widgets[0]
    callback(0.75)

    assert slider_kwargs == {"rng": (0.0, 1.0), "value": 0.25, "title": "isovalue"}
    assert plotter.meshes[-1][0]["points"][1] == [0.75, 0.0, 0.0]
    assert plotter.meshes[-1][1]["name"] == "isosurface"
