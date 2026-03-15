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


def compute_join_tree(mesh: Mesh) -> list:
    """
    Compute the join tree of a scalar field defined on a mesh.

    Args:
        mesh: Any Mesh instance with vertices, neighbors, and scalar values.

    Returns:
        A list of directed edges (child, parent) forming the join tree.
        Each edge (u, v) means the arc bottoming at u merges into v.

    Based on:
        Carr et al. (2003), Algorithm 4.1.
        Tarjan (1975), Union-Find with weighted union.
    """
    uf = UnionFind()
    edges = []

    # -----------------------------------------
    # Step 1 -- Sort vertices bottom to top
    # Vertices must be processed in ascending scalar value order so that
    # when we process vertex v, all lower neighbours are already in the Union-Find. 
    # Tiebreaker by vertex ID ensures deterministic ordering.
    # -----------------------------------------
    sorted_verts = mesh.sorted_vertices(ascending=True)

    # -----------------------------------------
    # Step 2 -- Register each vertex in the UnionFind
    # Before we process any vertex, it must exist as a singleton component.
    # Based on: Carr et al. (2003) Algorithm 4.1 -- "for i := 1 to n, make_set(i)"
    # -----------------------------------------
    for v in sorted_verts:
        uf.make_set(v, mesh.value(v))

    # -----------------------------------------
    # Step 3 -- Main sweep: process vertices bottom to top
    # For each vertex v (in ascending order):
    #   - Union v with each lower neighbour (where f(u) < f(v))
    #   - After all unions, find the lowest vertex in the merged component
    #   - If lowest != v, record a join edge from lowest to v
    # Based on: Carr et al. (2003) Algorithm 4.1, p. 82
    # -----------------------------------------
    for v in sorted_verts:
        # Find all neighbours of v
        neighbours = mesh.neighbors(v)
        
        # For each neighbour u with f(u) < f(v), merge v and u
        for u in neighbours:
            if mesh.value(u) < mesh.value(v):
                uf.union(v, u)
        
        # After merging with all lower neighbours,
        # find the lowest vertex in the merged component
        lowest = uf.lowest_in_component(v)
        
        # If the lowest vertex is not v itself,
        # record a join edge from lowest to v
        if lowest != v:
            edges.append((lowest, v))

    return edges
