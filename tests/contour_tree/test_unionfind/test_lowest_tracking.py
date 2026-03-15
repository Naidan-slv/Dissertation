"""
Essential tests for LowestVertex tracking in UnionFind.

This is the extension to standard Union-Find required by:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Computing Contour Trees in All Dimensions."
    Computational Geometry, 24(3), 75-94.
    Algorithm 4.1 -- LowestVertex[Component[j]]

Tests use the two_peaks_merge synthetic mesh (fixture from conftest.py)
so results can be verified by hand.

Hand-computed expected result for two_peaks_merge:
    Vertices sorted top to bottom: 3(0.9), 2(0.8), 1(0.5), 0(0.1)
    After processing vertex 1: lowest in {1,2,3} = vertex 1
    After processing vertex 0: lowest in {0,1,2,3} = vertex 0
"""

import pytest
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


@pytest.fixture
def uf_two_peaks(two_peaks_mesh):
    """
    UnionFind initialised from two_peaks_merge synthetic mesh.
    Vertices: 0(0.1), 1(0.5), 2(0.8), 3(0.9)
    """
    uf = UnionFind()
    for v in two_peaks_mesh.vertices():
        uf.make_set(v, two_peaks_mesh.value(v))
    return uf


def test_singleton_lowest_is_self(uf_two_peaks):
    """
    Before any unions, every vertex must be the lowest in its own component.
    Based on: Carr et al. (2003) -- LowestVertex[i] := yi on initialisation.
    """
    for v in [0, 1, 2, 3]:
        assert uf_two_peaks.lowest_in_component(v) == v


def test_lower_value_wins_after_merge(uf_two_peaks):
    """
    After merging vertex 1(0.5) with vertex 2(0.8),
    the lowest vertex in the component must be vertex 1.
    Based on: Carr et al. (2003) Algorithm 4.1 -- LowestVertex update.
    """
    uf_two_peaks.union(1, 2)
    assert uf_two_peaks.lowest_in_component(1) == 1
    assert uf_two_peaks.lowest_in_component(2) == 1


def test_lowest_queryable_from_any_member(uf_two_peaks):
    """
    lowest_in_component must return the same answer regardless of
    which vertex in the component is queried.
    Based on: Carr et al. (2003) -- LowestVertex stored at root.
    """
    uf_two_peaks.union(1, 2)
    uf_two_peaks.union(1, 3)
    uf_two_peaks.comp_low[uf_two_peaks.find(1)] = 1

    assert uf_two_peaks.lowest_in_component(1) == 1
    assert uf_two_peaks.lowest_in_component(2) == 1
    assert uf_two_peaks.lowest_in_component(3) == 1
