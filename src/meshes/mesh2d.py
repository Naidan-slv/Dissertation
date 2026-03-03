"""
Minimal 2D mesh implementation.

For now:
- store scalar values per vertex
- implement vertices() and value()
- no adjacency yet
"""

from __future__ import annotations

from typing import Dict, List

from src.meshes.mesh import Mesh


class TriMesh2D(Mesh):
    def __init__(self, values: Dict[int, float]):
        self._values = values

    def vertices(self) -> List[int]:
        return list(self._values.keys())

    def neighbors(self, v: int) -> List[int]:
        # not implemented yet
        raise NotImplementedError("neighbors() not implemented yet (Step 1)")

    def value(self, v: int) -> float:
        return self._values[v]


