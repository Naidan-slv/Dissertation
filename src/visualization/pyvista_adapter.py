"""Optional PyVista adapter for isosurface viewer payloads.

The payload layer stays plain Python. This module is where the PyVista-specific
conversion will live, so importing the rest of the project does not require VTK.
"""


def require_pyvista():
    """Return the PyVista module, or explain that the viewer extra is missing."""
    try:
        import pyvista
    except ImportError as exc:
        raise RuntimeError(
            "PyVista is optional for this project. Install it with `pip install pyvista` "
            "to use the interactive viewer."
        ) from exc

    return pyvista


def _vtk_faces(faces):
    """Flatten triangle faces into PyVista/VTK's [3, a, b, c] layout."""
    vtk_faces = []
    for face in faces:
        if len(face) != 3:
            raise ValueError("PyVista adapter expects triangle faces")
        a, b, c = face
        vtk_faces.extend([3, int(a), int(b), int(c)])
    return vtk_faces


def payload_to_polydata(payload):
    """Convert an isosurface payload into a PyVista PolyData mesh."""
    pyvista = require_pyvista()
    return pyvista.PolyData(payload["points"], _vtk_faces(payload["faces"]))


def build_isosurface_plotter(payload, color="tomato", opacity=0.75, show_edges=True):
    """Build a plotter for the mesh without opening a window.

    Tests can check this safely because callers decide when to call ``show()``.
    """
    pyvista = require_pyvista()
    mesh = payload_to_polydata(payload)
    plotter = pyvista.Plotter()
    plotter.add_mesh(mesh, color=color, show_edges=show_edges, opacity=opacity)
    plotter.show_axes()
    return plotter
