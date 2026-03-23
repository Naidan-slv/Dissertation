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
    if not ct_edges:
        return [], []

    # Build adjacency
    adj = defaultdict(set)
    for u, v in ct_edges:
        adj[u].add(v)
        adj[v].add(u)

    # Critical = degree != 2 (leaves have deg 1, saddles have deg >= 3)
    critical = {v for v, nbrs in adj.items() if len(nbrs) != 2}

    # For each critical vertex, walk along each incident edge until we
    # reach another critical vertex — that walk defines one superarc.
    superarc_set = set()
    for v in critical:
        for nbr in adj[v]:
            # Walk from v through nbr until we hit a critical vertex
            prev, curr = v, nbr
            while curr not in critical:
                # curr is degree-2, keep walking
                nxt = next(w for w in adj[curr] if w != prev)
                prev, curr = curr, nxt
            # curr is the other critical endpoint
            superarc_set.add(tuple(sorted((v, curr))))

    supernodes = sorted(critical)
    superarcs = [tuple(e) for e in superarc_set]
    return supernodes, superarcs