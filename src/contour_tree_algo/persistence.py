"""
Persistence pairs for the unaugmented contour tree.

For each leaf, walk superarcs to the nearest saddle and compute
persistence = |f(saddle) - f(leaf)|. Used to rank branches by
importance before simplification.

Refs: Topological Manipulation of Isosurfaces, Ch 11;
      Topological Persistence and Simplification.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PersistencePair:
    """Leaf-saddle branch ranking record."""
    leaf: int
    saddle: int
    persistence: float
    direction: str
    path: tuple


def compute_persistence_pairs(supernodes, superarcs, value_fn):
    """Return leaf-saddle records sorted by persistence ascending."""
    if not superarcs:
        return []

    adj = defaultdict(set)
    for u, v in superarcs:
        adj[u].add(v)
        adj[v].add(u)

    if len(superarcs) == 1:
        u, v = superarcs[0]
        leaf, saddle = sorted((u, v), key=lambda vertex: (value_fn(vertex), vertex))
        p = abs(value_fn(saddle) - value_fn(leaf))
        return [PersistencePair(leaf, saddle, p, _branch_direction(leaf, saddle, value_fn), (leaf, saddle))]

    leaves = [v for v in supernodes if len(adj[v]) == 1]
    pairs = []
    for leaf in leaves:
        saddle, path = _walk_to_saddle(leaf, adj)
        p = abs(value_fn(saddle) - value_fn(leaf))
        direction = _branch_direction(leaf, saddle, value_fn)
        pairs.append(PersistencePair(leaf, saddle, p, direction, path))
    pairs.sort(key=lambda pair: (pair.persistence, value_fn(pair.leaf), pair.leaf))
    return pairs


def _branch_direction(leaf, saddle, value_fn):
    """Classify a leaf branch as a min or max branch."""
    if value_fn(leaf) <= value_fn(saddle):
        return "min"
    return "max"


def _walk_to_saddle(leaf, adj):
    """Walk from leaf to the nearest saddle, returning saddle and path."""
    prev, curr = None, leaf
    path = [leaf]
    while True:
        neighbours = adj[curr]
        if len(neighbours) >= 3:
            return curr, tuple(path)
        if len(neighbours) == 1 and curr != leaf:
            return curr, tuple(path)
        nxt = next(n for n in neighbours if n != prev)
        prev, curr = curr, nxt
        path.append(curr)
