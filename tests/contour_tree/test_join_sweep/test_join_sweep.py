"""
Tests for the join sweep (Algorithm 4.1, Carr et al. 2003).

Built incrementally -- one test per step of the algorithm.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    "Computing Contour Trees in All Dimensions."
    Computational Geometry, 24(3), 75-94.
    Algorithm 4.1.
"""

import pytest
from src.contour_tree_algo.sub_algorithms.join_sweep import JoinSweep


# -----------------------------------------
# Step 1 -- Class is instantiable and compute() returns a list
# -----------------------------------------

def test_join_sweep_is_callable(single_peak_mesh):
    """
    JoinSweep must accept a mesh, and compute() must return a list.
    This is the minimal contract before any logic is implemented.
    """
    sweep = JoinSweep(single_peak_mesh)
    result = sweep.compute()
    assert isinstance(result, list)
