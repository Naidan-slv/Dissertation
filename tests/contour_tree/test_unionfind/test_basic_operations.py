"""
Essential tests for basic UnionFind operations.

Covers: make_set, find, union.

Based on:
    Tarjan, R.E. (1975). "Efficiency of a Good But Not Linear Set Union Algorithm."
    Journal of the ACM, 22(2), 215-225.
"""

import pytest
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


@pytest.fixture
def uf():
    """UnionFind with 4 elements matching the two_peaks_merge synthetic mesh."""
    uf = UnionFind()
    uf.make_set(0, 0.1)
    uf.make_set(1, 0.5)
    uf.make_set(2, 0.8)
    uf.make_set(3, 0.9)
    return uf


def test_singleton_is_own_root(uf):
    """
    Before any unions, every element must be its own root.
    Based on: Tarjan (1975), initial state of make_set.
    """
    for v in [0, 1, 2, 3]:
        assert uf.find(v) == v


def test_find_after_union(uf):
    """
    After union(1, 2), both elements must share the same root.
    Based on: Tarjan (1975), FIND operation.
    """
    uf.union(1, 2)
    assert uf.find(1) == uf.find(2)


def test_redundant_union_does_not_change_structure(uf):
    """
    Calling union on two elements already in the same component
    must not alter the parent structure.
    Based on: Tarjan (1975) -- union returns early if roots are equal.
    """
    uf.union(1, 2)
    parent_before = dict(uf.parent)
    uf.union(1, 2)  # redundant
    assert uf.parent == parent_before
