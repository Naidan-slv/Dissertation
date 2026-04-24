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
    raise NotImplementedError


def _walk_to_saddle(leaf, adj):
    """Walk from leaf along superarcs until reaching a saddle (degree >= 3)."""
    raise NotImplementedError
