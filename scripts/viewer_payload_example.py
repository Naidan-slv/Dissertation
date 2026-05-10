"""Build a tiny linked viewer payload without opening a GUI."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.viewer_payload import build_viewer_payload


def build_example_payload():
    """Return a small payload that exercises the mesh/surface/tree link."""
    data = np.zeros(8)
    data[1] = 1.0  # one high corner in a 2x2x2 grid
    mesh = GridMesh3D(2, 2, 2, data)

    return build_viewer_payload(
        mesh=mesh,
        supernodes=[0, 1],
        superarcs=[(0, 1)],
        isovalue=0.5,
        dataset_name="tiny-example",
    )


if __name__ == "__main__":
    payload = build_example_payload()
    print(json.dumps(payload, indent=2))
