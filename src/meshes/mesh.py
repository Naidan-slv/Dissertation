"""
src/mesh.py

Generic mesh interface for contour-tree-style algorithms.

Key idea:
- The algorithms should operate on "a set of vertices with scalar values + adjacency".

This file defines the abstract interface.Concrete meshes (e.g., TriMesh2D, TetraGridMesh)
will implement it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
# abstract base classes
# abstract base methods mark methods that must be implemented by any subclass
from typing import List


class Mesh(ABC):
    """
    Abstract base class for a mesh / graph with a scalar function on vertices.

    Required by join/split/merge algorithms:
    - iterate vertices
    - query neighbors
    - query scalar value
    - get deterministic sorted vertex order (with tie-breaking)
    """

    @abstractmethod
    def vertices(self) -> List[int]:
        """Return a list of all vertex IDs."""
        raise NotImplementedError

    @abstractmethod
    def neighbors(self, v: int) -> List[int]:
        """Return the neighbor vertex IDs of vertex v."""
        raise NotImplementedError

    @abstractmethod
    def value(self, v: int) -> float:
        """Return the scalar value f(v) for vertex v."""
        raise NotImplementedError

    def sorted_vertices(self, ascending: bool = True) -> List[int]:
        """
        Return vertices sorted by scalar value, with deterministic tie-breaking.
        verts = [v1, v2, v3, ...]
        vid = vertex id

        """
        verts = self.vertices()
        verts.sort(key=lambda vid: (self.value(vid), vid), reverse=not ascending)
        return verts