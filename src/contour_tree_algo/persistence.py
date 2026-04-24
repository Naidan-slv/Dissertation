"""
Persistence pairs for the unaugmented contour tree.

For each leaf, walk superarcs to the nearest saddle and compute
persistence = |f(saddle) - f(leaf)|. Used to rank branches by
importance before simplification.

Refs: Topological Manipulation of Isosurfaces, Ch 11;
      Topological Persistence and Simplification.
"""


def compute_persistence_pairs(supernodes, superarcs, value_fn):
    """Return list of (leaf, saddle, persistence) sorted by persistence asc."""
    if not superarcs:
        return []
    from collections import defaultdict
    adj = defaultdict(set)
    for u, v in superarcs:
        adj[u].add(v)
        adj[v].add(u)
    leaves = [v for v in supernodes if len(adj[v]) == 1]
    pairs = []
    for leaf in leaves:
        saddle = _walk_to_saddle(leaf, adj)
        p = abs(value_fn(saddle) - value_fn(leaf))
        pairs.append((leaf, saddle, p))
    pairs.sort(key=lambda t: (t[2], t[0]))
    return pairs


def _walk_to_saddle(leaf, adj):
    """Walk from leaf along superarcs until reaching a saddle (degree >= 3)."""
    prev, curr = None, leaf
    while True:
        neighbours = adj[curr]
        if len(neighbours) >= 3:
            return curr
        if len(neighbours) == 1 and curr != leaf:
            return curr
        nxt = next(n for n in neighbours if n != prev)
        prev, curr = curr, nxt
