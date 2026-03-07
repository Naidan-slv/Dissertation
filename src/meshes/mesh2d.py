"""
Minimal 2D mesh implementation.

For now:
- store scalar values per vertex
- implement vertices() and value()
- no adjacency yet
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.meshes.mesh import Mesh


class TriMesh2D(Mesh):
    """
    Simple 2D mesh triangulated mesh.
    
    :parameter values: Dict[int, float]
        Scalar value f(v) for each vertex.
    :parameter triangles: List[Tuple[int, int, int]]
        List of triangles defined by vertex IDs.
    """

    def __init__(
            self,
            values: Dict[int, float],
            triangles: List[Tuple[int, int, int]]
        ):
        # store scalar values
        self._values = values
        # store triangle connectivity
        self._triangles = triangles

    def vertices(self) -> List[int]:
        return list(self._values.keys())

    def neighbors(self, v: int) -> List[int]:
        # not implemented yet
        raise NotImplementedError("neighbors() not implemented yet (Step 1)")

    def value(self, v: int) -> float:
        return self._values[v]

    def triangles(self) -> List[Tuple[int, int, int]]:
        """Return the list of triangles in the mesh."""
        return self._triangles


