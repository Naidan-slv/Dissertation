"""
Abstract mesh interface for contour tree algorithms.

Design rationale:
    The contour tree algorithm only needs three operations: iterate vertices,
    query neighbours, and query scalar values. By defining this as an abstract
    interface, the algorithm is decoupled from any specific mesh representation.
    This allows the same join/split/merge/reduce pipeline to run on small 2D
    test meshes (for verification against known results) and large 3D volumetric
    datasets (for real-world use) without any code changes.

Concrete implementations:
    - TriMesh2D:   2D triangulated mesh, used for small hand-built test fixtures.
    - GridMesh:    2D grid with explicit edges, used for the Carr 9x9 paper example.
    - GridMesh3D:  3D structured grid with Freudenthal connectivity, used for
                   real volumetric datasets.
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