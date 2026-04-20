"""
2D triangulated mesh.

Design rationale:
    This mesh is used for small, hand-built test fixtures (diamond, linear chain,
    Y-fork, etc.) where the expected contour tree is known and can be verified by
    hand.  Testing on these simple cases first ensures the algorithm is correct
    before it is applied to large 3D volumes where manual verification is
    impossible.  Adjacency is derived automatically from a list of triangles,
    which is the natural way to define small 2D meshes.
"""

from __future__ import annotations

from collections import defaultdict
# we use default dict since this creates a dictionary where missing keys
# automatically create an empty set
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
        self._adj = defaultdict(set)

        # Build adjacency from the triangle list
        self._build_adjacency()

    def _build_adjacency(self) -> None:
        """
        Build vertex adjacency from triangle connectivity.

        For each triangle (a, b, c), we add the three undirected edges:
            (a, b), (b, c), (c, a)

        Using sets avoids duplicate neighbors when two triangles share an edge.
        """
        for a, b, c in self._triangles:
            self._adj[a].update([b, c])
            self._adj[b].update([a, c])
            self._adj[c].update([a, b])

    def vertices(self) -> List[int]:
        return list(self._values.keys())

    def neighbors(self, v: int) -> List[int]:
        """
        Return the neighboring vertices of v.
        We convert the internal set to a sorted list so output is deterministic.
        """
        return sorted(self._adj[v])

    def value(self, v: int) -> float:
        return self._values[v]

    def triangles(self) -> List[Tuple[int, int, int]]:
        """Return the list of triangles in the mesh."""
        return self._triangles


