"""
Split Sweep -- Mirror of Join Sweep (Algorithm 7.2 applied descending).

Computes the split tree of a scalar field on a mesh by processing vertices
in descending order (top to bottom). The split tree captures where connected
components split apart as iso-value decreases.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Topological Manipulation of Isosurfaces."
    Computational Geometry, 24(3), 75-94.
    See: Algorithm 7.2 (join sweep), applied in descending direction.
"""

from src.meshes.mesh import Mesh
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


def compute_split_tree(mesh: Mesh) -> list:
    """
    Compute the split tree of a scalar field defined on a mesh.

    Applies the split sweep algorithm in descending order (maximum to minimum).
    For each vertex, identifies all neighbors with higher values and connects
    their component roots to the current vertex. This records where components
    split as the iso-value decreases.

    See: Carr et al. (2003), p. 50. Algorithm 7.2 (join sweep logic), applied
    descending instead of ascending to compute the split tree.

    Args:
        mesh: Any Mesh instance with vertices, neighbors, and scalar values.

    Returns:
        List of directed edges (root, v) forming the split tree, where root
        is the root of a higher-valued component connecting to v.
    """
    uf = UnionFind()
    edges = []

    sorted_verts = mesh.sorted_vertices(ascending=False)

    for v in sorted_verts:
        uf.make_set(v, mesh.value(v))
        neighbours = mesh.neighbors(v)
        roots = []

        for u in neighbours:
            if mesh.value(u) > mesh.value(v):
                root_u = uf.find(u)
                if root_u not in [r[0] for r in roots]:
                    roots.append((root_u, mesh.value(root_u)))

        roots.sort(key=lambda x: x[1], reverse=True)

        for root, _ in roots:
            if root != v:
                edges.append((root, v))
                uf.union(root, v)

    return edges
