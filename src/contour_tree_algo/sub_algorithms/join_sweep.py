"""
Join Sweep -- Algorithm 4.1 from Carr et al. (2003).

Computes the join tree of a scalar field on a mesh.

The join tree records where ascending connected components merge
as the scalar value increases from the global minimum upward.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Computing Contour Trees in All Dimensions."
    Computational Geometry, 24(3), 75-94.
    Algorithm 4.1, p. 82.
"""

from src.meshes.mesh import Mesh
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


class JoinSweep:
    """
    Computes the join tree of a scalar field defined on a mesh.

    Usage:
        sweep = JoinSweep(mesh)
        edges = sweep.compute()

    Attributes:
        mesh:          the input mesh
        uf:            UnionFind instance (populated after compute())
        sorted_verts:  vertices in ascending order (populated after compute())
        edges:         join tree edges as (child, parent) tuples

    Based on:
        Carr et al. (2003), Algorithm 4.1.
        Tarjan (1975), Union-Find with weighted union.
    """

    def __init__(self, mesh: Mesh):
        self.mesh = mesh
        self.uf = UnionFind()
        self.sorted_verts = []
        self.edges = []

    def compute(self) -> list:
        """
        Run the join sweep and return the join tree edges.

        Returns:
            List of (child, parent) tuples representing join tree edges.
        """
        return self.edges
