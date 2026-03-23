"""
Raw volume loader.

Thin wrapper that delegates to src.input.ingest for config/loading,
then wraps the result in a GridMesh3D.

Reference: Carr (2004) §5.1 — data representation for regular grids.
Datasets sourced from Klacansky's Open SciVis Datasets.
"""

from src.input.ingest import load_raw_volume
from src.meshes.grid_mesh_3d import GridMesh3D


def load_raw_dataset(name: str, freudenthal: bool = True) -> GridMesh3D:
    """
    Load a named dataset from datasets.yaml and return a GridMesh3D.

    :param name: Dataset key in datasets.yaml (e.g. "fuel", "aneurism").
    :param freudenthal: If True, use 14-connected Freudenthal adjacency.
    :returns: GridMesh3D ready for contour tree computation.
    """
    data, w, h, d = load_raw_volume(name)
    return GridMesh3D(width=w, height=h, depth=d, data=data,
                      freudenthal=freudenthal)
