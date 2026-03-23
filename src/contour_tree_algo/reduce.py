"""
Reduce -- Convert fully augmented contour tree to unaugmented form.

Algorithm 7.4 from Carr (2004), §7.2.

The fully augmented contour tree contains every mesh vertex. The
unaugmented (reduced) contour tree keeps only *critical points*:
    - Local minima  (degree 1, lower leaf)
    - Local maxima  (degree 1, upper leaf)
    - Saddles        (degree >= 3, branch points)

Degree-2 vertices (regular points) are removed by contracting their
two incident edges into a single superarc.

Output:
    supernodes  – list of critical vertex ids
    superarcs   – list of (u, v) edges between supernodes
"""

from collections import defaultdict


def reduce_contour_tree(ct_edges):
    """
    Reduce a fully augmented contour tree to its unaugmented form.

    Removes all degree-2 (regular) vertices, keeping only critical points
    (leaves and branch vertices). Degree-2 paths are contracted into
    single superarcs.

    Args:
        ct_edges: List of (u, v) edges from the fully augmented contour tree.

    Returns:
        (supernodes, superarcs) where:
            supernodes: sorted list of critical vertex ids
            superarcs:  list of (u, v) edges connecting supernodes
    """
    raise NotImplementedError("reduce_contour_tree not yet implemented")