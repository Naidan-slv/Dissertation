"""
Join Sweep -- Algorithm 7.2 from Carr et al. (2003).

Computes the fully augmented join tree of a scalar field on a mesh.
The join tree records where ascending connected components merge
as the scalar value increases from the global minimum upward.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
        "Computing Contour Trees in All Dimensions."
        Computational Geometry, 24(3), 75-94.
        Algorithm 7.2 (join sweep for fully augmented tree).
"""

from src.meshes.mesh import Mesh
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


def compute_join_tree(mesh: Mesh) -> list:
    """
    Compute the join tree of a scalar field defined on a mesh.

    Processes vertices in descending order (highest first).
    For each vertex v, examines all higher-valued neighbours.
    When a higher neighbour n belongs to a different component,
    an edge is added from the lowest vertex in n's component to v,
    then the two components are merged.

    After processing all neighbours of v, the component's lowest
    vertex is explicitly set to v (since v is the current minimum).

    Args:
        mesh: Any Mesh instance with vertices, neighbors, and scalar values.

    Returns:
        A list of directed edges (u, v) forming the join tree,
        where u is the lowest vertex of the merging component
        and v is the vertex where the merge occurs.
    """
    uf = UnionFind()
    edges = []

    # Step 1: Initialise every vertex as a singleton component.
    for v in mesh.vertices():
        uf.make_set(v, mesh.value(v))

    # Step 2: Process vertices from highest to lowest scalar value.
    sorted_verts = mesh.sorted_vertices(ascending=False)

    for v in sorted_verts:
        # Step 3: For each higher-valued neighbour, merge components.
        for n in mesh.neighbors(v):
            if mesh.value(n) > mesh.value(v) or (
                mesh.value(n) == mesh.value(v) and n > v
            ):
                if uf.find(n) != uf.find(v):
                    u = uf.lowest_in_component(n)
                    edges.append((u, v))
                    uf.union(n, v)

        # Step 4: v is now the lowest vertex in its component.
        root = uf.find(v)
        uf.comp_low[root] = v

    return edges
