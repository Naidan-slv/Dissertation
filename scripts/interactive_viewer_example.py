"""Tiny runnable interactive-viewer example.

This uses the same 2x2x2 grid as the payload example. It is deliberately small
so the slider/tree wiring can be checked before pointing the viewer at large data.
"""

import numpy as np

from src.meshes.grid_mesh_3d import GridMesh3D
from src.visualization.interactive_viewer import build_interactive_viewer, show_interactive_viewer


def build_example_inputs():
    """Return the mesh and one-arc contour tree used by the demo."""
    data = np.zeros(8)
    data[1] = 1.0  # vertex id 1 is (x=1, y=0, z=0)

    return {
        "mesh": GridMesh3D(2, 2, 2, data),
        "supernodes": [0, 1],
        "superarcs": [(0, 1)],
        "initial_isovalue": 0.5,
        "dataset_name": "tiny-interactive-example",
    }


def build_example_viewer():
    """Build the example plotter without calling show()."""
    return build_interactive_viewer(**build_example_inputs())


def main():
    """Open the example viewer window."""
    return show_interactive_viewer(**build_example_inputs())


if __name__ == "__main__":
    main()
