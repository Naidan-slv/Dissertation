"""
Split Sweep -- Dual of Algorithm 7.2 from Carr et al. (2003).

Computes the fully augmented split tree of a scalar field on a mesh.
The split tree records where descending connected components split
as the scalar value decreases from the global maximum downward.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
        "Computing Contour Trees in All Dimensions."
        Computational Geometry, 24(3), 75-94.
        Algorithm 7.2 applied in the ascending direction.
"""

from src.meshes.mesh import Mesh
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


def compute_split_tree(mesh: Mesh) -> list:
    """
    Compute the split tree of a scalar field defined on a mesh.

    Processes vertices in ascending order (lowest first).
    For each vertex v, examines all lower-valued neighbours.
    When a lower neighbour n belongs to a different component,
    an edge is added from the highest vertex in n's component to v,
    then the two components are merged.

    After processing all neighbours of v, the component's highest
    vertex is explicitly set to v (since v is the current maximum).

    Args:
        mesh: Any Mesh instance with vertices, neighbors, and scalar values.

    Returns:
        A list of directed edges (u, v) forming the split tree,
        where u is the highest vertex of the merging component
        and v is the vertex where the split occurs.
    """
    uf = UnionFind()
    edges = []

    # Step 1: Initialise every vertex as a singleton component.
    for v in mesh.vertices():
        uf.make_set(v, mesh.value(v))

    # Step 2: Process vertices from lowest to highest scalar value.
    sorted_verts = mesh.sorted_vertices(ascending=True)

    for v in sorted_verts:
        # Step 3: For each lower-valued neighbour, merge components.
        for n in mesh.neighbors(v):
            if mesh.value(n) < mesh.value(v) or (
                mesh.value(n) == mesh.value(v) and n < v
            ):
                if uf.find(n) != uf.find(v):
                    u = uf.highest_in_component(n)
                    edges.append((u, v))
                    uf.union(n, v)

        # Step 4: v is now the highest vertex in its component.
        root = uf.find(v)
        uf.comp_high[root] = v

    return edges
