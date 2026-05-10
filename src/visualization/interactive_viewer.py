"""High-level wiring for the interactive isosurface viewer.

This module is the first place where the project mesh, linked viewer payload, and
PyVista adapter meet. The functions still avoid opening a window unless the
caller asks for it.
"""

from src.visualization.pyvista_adapter import build_isosurface_plotter, payload_to_polydata
from src.visualization.viewer_payload import build_viewer_payload


def current_viewer_payload(plotter):
    return plotter._viewer_payload


def _mesh_scalar_range(mesh):
    """Return the scalar range from a project mesh."""
    values = [mesh.value(v) for v in mesh.vertices()]
    if not values:
        raise ValueError("interactive viewer needs at least one mesh vertex")
    return float(min(values)), float(max(values))


def _refresh_isosurface(plotter, isosurface_payload):
    """Replace the named isosurface actor on an existing plotter."""
    mesh = payload_to_polydata(isosurface_payload)
    plotter.add_mesh(
        mesh,
        color="tomato",
        show_edges=True,
        opacity=0.75,
        name="isosurface",
    )


def build_interactive_viewer(
    mesh,
    supernodes,
    superarcs,
    initial_isovalue,
    dataset_name=None,
    value_fn=None,
):
    """Build a PyVista plotter with a linked isovalue slider."""
    if value_fn is None:
        value_fn = mesh.value

    def linked_payload(isovalue):
        return build_viewer_payload(
            mesh=mesh,
            supernodes=supernodes,
            superarcs=superarcs,
            isovalue=isovalue,
            dataset_name=dataset_name,
            value_fn=value_fn,
        )

    initial_payload = linked_payload(initial_isovalue)
    plotter = build_isosurface_plotter(initial_payload["isosurface"])
    plotter._viewer_payload = initial_payload

    def update_isovalue(isovalue):
        payload = linked_payload(isovalue)
        plotter._viewer_payload = payload
        _refresh_isosurface(plotter, payload["isosurface"])

    plotter.add_slider_widget(
        update_isovalue,
        rng=_mesh_scalar_range(mesh),
        value=float(initial_isovalue),
        title="isovalue",
    )
    return plotter


def show_interactive_viewer(*args, **kwargs):
    """Build and show the interactive viewer, returning the plotter for scripts."""
    plotter = build_interactive_viewer(*args, **kwargs)
    plotter.show()
    return plotter
