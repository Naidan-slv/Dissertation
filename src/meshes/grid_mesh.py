"""
2D rectangular grid mesh with explicit edge connectivity.

Design rationale:
    This mesh exists specifically for the Carr et al. (2003) 9x9 worked example,
    where the paper uses a particular diagonal pattern (NW only, 6-connected) that
    must be matched exactly to reproduce Figure 7.5.  Unlike TriMesh2D, which
    derives edges from triangles, this class accepts an explicit edge list so the
    connectivity can be controlled precisely.  This was essential for validating
    the implementation against the published result.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from src.meshes.mesh import Mesh


class GridMesh(Mesh):
    """
    Regular rectangular grid mesh with explicit edge connectivity.
    
    :parameter width: Width of the grid (columns).
    :parameter height: Height of the grid (rows).
    :parameter values_dict: Dict[int, float] - scalar value at each vertex.
    :parameter edges_list: List[Tuple[int, int]] - explicit edges (undirected).
    """
    
    def __init__(self, width: int, height: int, values_dict: Dict[int, float], edges_list: List[Tuple[int, int]]):
        self.width = width
        self.height = height
        self._values = values_dict
        self._adj = defaultdict(set)
        
        # Build adjacency from edges
        for u, v in edges_list:
            self._adj[u].add(v)
            self._adj[v].add(u)
    
    def vertices(self) -> List[int]:
        """Return all vertex IDs."""
        return list(self._values.keys())
    
    def neighbors(self, v: int) -> List[int]:
        """Return neighboring vertices of v."""
        return sorted(list(self._adj[v]))
    
    def value(self, v: int) -> float:
        """Return scalar value at vertex v."""
        return self._values[v]
