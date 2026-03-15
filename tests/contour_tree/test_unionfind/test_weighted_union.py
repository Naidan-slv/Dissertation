"""
Essential tests for the weighted union rule in UnionFind.

Note on path compression:
    This implementation deliberately omits path compression.
    Path compression is a performance optimisation (Tarjan 1975) that
    would obscure the algorithm during development.
    It can be added later once correctness is fully verified.

What is tested here:
    The weighted union rule -- always attach the smaller tree under
    the larger tree to keep depth logarithmic.

Based on:
    Tarjan, R.E. (1975). "Efficiency of a Good But Not Linear Set Union Algorithm."
    Journal of the ACM, 22(2), 215-225.
"""

import pytest
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


@pytest.fixture
def uf():
    """UnionFind with 5 elements, values 0.0 to 4.0."""
    uf = UnionFind()
    for i in range(5):
        uf.make_set(i, scalar_value=float(i))
    return uf


def test_larger_component_stays_root(uf):
    """
    When merging a larger component with a smaller one,
    the root of the larger component must remain the root.
    Based on: Tarjan (1975) -- weighted union rule.
    """
    uf.union(0, 1)
    uf.union(0, 2)          # component {0,1,2} now has size 3
    large_root = uf.find(0)

    uf.union(0, 3)          # merge singleton {3} into size-3 component
    assert uf.find(0) == large_root
    assert uf.find(3) == large_root


def test_size_updates_correctly_after_merge(uf):
    """
    After merging two components, the root must report the correct combined size.
    Based on: Tarjan (1975) -- size tracking for weighted union.
    """
    uf.union(0, 1)   # size 2
    uf.union(2, 3)   # size 2
    uf.union(0, 2)   # merge -> size 4
    root = uf.find(0)
    assert uf.size[root] == 4
