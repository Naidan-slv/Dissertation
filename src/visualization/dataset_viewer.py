"""Dataset-backed helpers for the interactive viewer.

The tiny viewer example proves the UI wiring. This module is the bridge from
project datasets, including Klacansky raw volumes, into that same viewer path.
"""

from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree
from src.input.ingest import load_raw_dataset, load_raw_volume_single_file
from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.interactive_viewer import build_interactive_viewer, show_interactive_viewer


def _mesh_scalar_range(mesh):
    values = [mesh.value(v) for v in mesh.vertices()]
    if not values:
        raise ValueError("viewer inputs need at least one mesh vertex")
    return float(min(values)), float(max(values))


def _default_isovalue(mesh):
    low, high = _mesh_scalar_range(mesh)
    return (low + high) / 2.0


def build_grid_viewer_inputs(
    mesh,
    dataset_name=None,
    initial_isovalue=None,
    contour_tree_fn=compute_unaugmented_contour_tree,
):
    """Prepare arguments accepted by ``build_interactive_viewer``."""
    supernodes, superarcs = contour_tree_fn(mesh)
    if initial_isovalue is None:
        initial_isovalue = _default_isovalue(mesh)

    return {
        "mesh": mesh,
        "supernodes": list(supernodes),
        "superarcs": list(superarcs),
        "initial_isovalue": float(initial_isovalue),
        "dataset_name": dataset_name,
    }


def build_klacansky_viewer_inputs(
    dataset_name,
    initial_isovalue=None,
    freudenthal=True,
    loader=load_raw_dataset,
    contour_tree_fn=compute_unaugmented_contour_tree,
):
    """Load a named Klacansky dataset and prepare viewer arguments."""
    mesh = loader(dataset_name, freudenthal=freudenthal)
    return build_grid_viewer_inputs(
        mesh,
        dataset_name=dataset_name,
        initial_isovalue=initial_isovalue,
        contour_tree_fn=contour_tree_fn,
    )


def build_raw_file_viewer_inputs(
    file_path,
    shape_whd,
    dtype="uint8",
    initial_isovalue=None,
    freudenthal=True,
    contour_tree_fn=compute_unaugmented_contour_tree,
):
    """Load an arbitrary raw volume file and prepare viewer arguments."""
    data, w, h, d = load_raw_volume_single_file(file_path, shape_whd, dtype)
    mesh = GridMesh3D(width=w, height=h, depth=d, data=data, freudenthal=freudenthal)
    return build_grid_viewer_inputs(
        mesh,
        dataset_name=str(file_path),
        initial_isovalue=initial_isovalue,
        contour_tree_fn=contour_tree_fn,
    )


def build_klacansky_viewer(dataset_name, **kwargs):
    """Build, but do not show, the interactive viewer for a Klacansky dataset."""
    viewer_inputs = build_klacansky_viewer_inputs(dataset_name, **kwargs)
    return build_interactive_viewer(**viewer_inputs)


def show_klacansky_viewer(dataset_name, **kwargs):
    """Load a Klacansky dataset and open the interactive viewer."""
    viewer_inputs = build_klacansky_viewer_inputs(dataset_name, **kwargs)
    return show_interactive_viewer(**viewer_inputs)


def build_raw_file_viewer(file_path, shape_whd, **kwargs):
    """Build, but do not show, the interactive viewer for an arbitrary raw file."""
    viewer_inputs = build_raw_file_viewer_inputs(file_path, shape_whd, **kwargs)
    return build_interactive_viewer(**viewer_inputs)


def show_raw_file_viewer(file_path, shape_whd, **kwargs):
    """Load an arbitrary raw file and open the interactive viewer."""
    viewer_inputs = build_raw_file_viewer_inputs(file_path, shape_whd, **kwargs)
    return show_interactive_viewer(**viewer_inputs)
