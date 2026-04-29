"""
Approximate local measures for contour-tree superarcs.

Reference: Carr (2004) Ch. 10, especially §10.8.
Schneider et al. (2012) motivates geometric feature comparison.
Carr (2004) Ch. 11 uses such measures to rank simplification steps.

This module computes Carr §10.8-style approximations. It does not compute exact
contour area or exact enclosed volume.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Tuple


Arc = Tuple[int, int]


@dataclass(frozen=True)
class ArcMeasure:
    """Approximate measurements attached to one reduced superarc."""

    node_count: int
    cell_crossing_count: int
    scalar_sum: float
    scalar_square_sum: float
    sample_vertices: Tuple[int, ...]


def reduce_with_superarc_vertices(ct_edges: Iterable[Arc]) -> Tuple[List[int], List[Arc], Dict[Arc, Tuple[int, ...]]]:
    """Reduce an augmented tree and keep the vertices absorbed by each superarc."""
    edges = list(ct_edges)
    if not edges:
        return [], [], {}

    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    critical = {v for v, nbrs in adj.items() if len(nbrs) != 2}
    paths: Dict[Arc, Tuple[int, ...]] = {}

    for start in sorted(critical):
        for nbr in sorted(adj[start]):
            path = [start, nbr]
            prev, curr = start, nbr

            while curr not in critical:
                next_vertices = [v for v in adj[curr] if v != prev]
                if not next_vertices:
                    break
                prev, curr = curr, next_vertices[0]
                path.append(curr)

            key = tuple(sorted((start, curr)))
            paths.setdefault(key, tuple(path))

    supernodes = sorted(critical)
    superarcs = sorted(paths)
    return supernodes, superarcs, paths


def compute_arc_measures(mesh, ct_edges: Iterable[Arc] | None = None) -> Dict[Arc, ArcMeasure]:
    """Compute Carr §10.8 approximate measures for each reduced superarc."""
    raise NotImplementedError


def _mesh_cells(mesh) -> List[Tuple[int, ...]]:
    """Return mesh cells used by the cell-crossing approximation."""
    raise NotImplementedError


def _cell_crosses_interval(cell: Tuple[int, ...], value_fn: Callable[[int], float], low: float, high: float) -> bool:
    """Return True if a cell's scalar range intersects a superarc interval."""
    raise NotImplementedError
