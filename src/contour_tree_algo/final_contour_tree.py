"""
Final Contour Tree -- End-to-end pipeline.

Orchestrates the full contour tree computation by combining three phases:
1. Join sweep (Algorithm 7.2, descending)
2. Split sweep (Algorithm 7.2 applied descending)
3. Merge (Algorithm 7.3)

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Topological Manipulation of Isosurfaces."
    Computational Geometry, 24(3), 75-94.
"""

from src.meshes.mesh import Mesh
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees


def compute_contour_tree(mesh: Mesh) -> list:
    """
    Compute the contour tree of a scalar field on a mesh.

    Pipeline:
    1. Compute join tree (bottom-up sweep)
    2. Compute split tree (top-down sweep)
    3. Merge both into final contour tree

    Args:
        mesh: Any Mesh instance with scalar values and adjacency.

    Returns:
        List of edges (u, v) forming the contour tree.
        Edges represent critical points and their connections.
    """
    join_edges = compute_join_tree(mesh)
    split_edges = compute_split_tree(mesh)
    contour_tree_edges = merge_trees(join_edges, split_edges, mesh.value)

    return contour_tree_edges