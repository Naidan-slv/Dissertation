"""Tests for the optional PyVista payload adapter."""

import sys

import pytest

from src.visualization.pyvista_adapter import payload_to_polydata, require_pyvista


class FakePyVista:
    def __init__(self):
        self.last_points = None
        self.last_faces = None

    def PolyData(self, points, faces):
        self.last_points = points
        self.last_faces = faces
        return {"points": points, "faces": faces}


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