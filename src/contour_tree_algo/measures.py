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
    if ct_edges is None:
        from src.contour_tree_algo.final_contour_tree import compute_contour_tree
        ct_edges = compute_contour_tree(mesh)

    _, superarcs, paths = reduce_with_superarc_vertices(ct_edges)
    cells = _mesh_cells(mesh)
    measures: Dict[Arc, ArcMeasure] = {}

    for arc in superarcs:
        sample_vertices = paths[arc]
        sample_set = set(sample_vertices)
        values = [float(mesh.value(v)) for v in sample_vertices]
        low, high = sorted((float(mesh.value(arc[0])), float(mesh.value(arc[1]))))
        cell_crossing_count = sum(
            1
            for cell in cells
            if sample_set.intersection(cell) and _cell_crosses_interval(cell, mesh.value, low, high)
        )
        measures[arc] = ArcMeasure(
            node_count=len(sample_vertices),
            cell_crossing_count=cell_crossing_count,
            scalar_sum=sum(values),
            scalar_square_sum=sum(value * value for value in values),
            sample_vertices=sample_vertices,
        )

    return measures


def _mesh_cells(mesh) -> List[Tuple[int, ...]]:
    """Return mesh cells used by the cell-crossing approximation."""
    if hasattr(mesh, "triangles"):
        return [tuple(cell) for cell in mesh.triangles()]

    if all(hasattr(mesh, attr) for attr in ("W", "H", "D")):
        from src.meshes.freudenthal_tets import enumerate_tetrahedra
        return enumerate_tetrahedra(mesh.W, mesh.H, mesh.D)

    return []


def _cell_crosses_interval(cell: Tuple[int, ...], value_fn: Callable[[int], float], low: float, high: float) -> bool:
    """Return True if a cell's scalar range intersects a superarc interval."""
    values = [float(value_fn(v)) for v in cell]
    return min(values) <= high and max(values) >= low
