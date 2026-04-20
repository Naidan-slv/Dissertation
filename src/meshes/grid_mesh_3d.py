"""
3D regular grid mesh with Freudenthal tetrahedralization.

Design rationale:
    This is the primary mesh used for real volumetric datasets (e.g. fuel, hydrogen,
    bonsai from the Klacansky Open SciVis repository).  It takes a flat numpy array
    of scalar values and computes neighbour connectivity automatically from the grid
    structure, avoiding the need to store an explicit edge or triangle list for
    potentially millions of vertices.

    Only the edges of the Freudenthal tetrahedralization are stored (as a 14-offset
    neighbour pattern), not the tetrahedra themselves, because the contour tree
    algorithm only requires adjacency — it never needs to walk through cells.

Implementation (Carr 2004, §4.3 and §5.1):
    Vertex ID scheme:
        v = z * H * W + y * W + x

    Adjacency:
        - 6-connected (face neighbours): offsets (±1, 0, 0), (0, ±1, 0), (0, 0, ±1)
        - Freudenthal tetrahedralization adds 8 more neighbours from the body diagonal
          decomposition, giving 14 total neighbours per interior vertex.

        The Freudenthal triangulation decomposes each unit cube into 6 tetrahedra
        sharing the body diagonal from (0,0,0) to (1,1,1). This produces edges along:
            - 6 face-adjacent directions
            - 6 face-diagonal directions (oriented by the body diagonal)
            - 2 body-diagonal directions
"""

from typing import List

import numpy as np

from src.meshes.mesh import Mesh


# 6-connected face neighbours
_OFFSETS_6 = [
    (+1,  0,  0), (-1,  0,  0),
    ( 0, +1,  0), ( 0, -1,  0),
    ( 0,  0, +1), ( 0,  0, -1),
]

# Freudenthal 14-connected: face + oriented face-diagonals + body diagonal
_OFFSETS_14 = _OFFSETS_6 + [
    (+1, +1,  0), (-1, -1,  0),   # xy face diagonal
    (+1,  0, +1), (-1,  0, -1),   # xz face diagonal
    ( 0, +1, +1), ( 0, -1, -1),   # yz face diagonal
    (+1, +1, +1), (-1, -1, -1),   # body diagonal
]


class GridMesh3D(Mesh):
    """
    3D regular grid mesh.

    :param width:  Grid extent along x (number of samples).
    :param height: Grid extent along y (number of samples).
    :param depth:  Grid extent along z (number of samples).
    :param data:   Flat array of scalar values in row-major (C) order:
                   data[z * H * W + y * W + x] = f(x, y, z).
    :param freudenthal: If True, use 14-connected Freudenthal tetrahedralization.
                        If False, use 6-connected face neighbours only.
    """

    def __init__(self, width: int, height: int, depth: int,
                 data: np.ndarray, freudenthal: bool = True):
        self.W = width
        self.H = height
        self.D = depth
        self._data = np.asarray(data, dtype=float).ravel()
        self._offsets = _OFFSETS_14 if freudenthal else _OFFSETS_6

        expected = width * height * depth
        if self._data.size != expected:
            raise ValueError(
                f"data has {self._data.size} elements, expected {expected} "
                f"for a {width}×{height}×{depth} grid"
            )

    # ── Mesh interface ─────────────────────────────────────────────

    def vertices(self) -> List[int]:
        return list(range(self.W * self.H * self.D))

    def neighbors(self, v: int) -> List[int]:
        x, y, z = self._id_to_xyz(v)
        nbrs = []
        for dx, dy, dz in self._offsets:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.W and 0 <= ny < self.H and 0 <= nz < self.D:
                nbrs.append(self._xyz_to_id(nx, ny, nz))
        return nbrs

    def value(self, v: int) -> float:
        return self._data[v]

    # ── Coordinate helpers ─────────────────────────────────────────

    def _xyz_to_id(self, x: int, y: int, z: int) -> int:
        """Convert (x, y, z) grid coordinates to a vertex ID."""
        return z * self.H * self.W + y * self.W + x

    def _id_to_xyz(self, v: int) -> tuple:
        """Convert a vertex ID back to (x, y, z) grid coordinates."""
        x = v % self.W
        y = (v // self.W) % self.H
        z = v // (self.W * self.H)
        return x, y, z
