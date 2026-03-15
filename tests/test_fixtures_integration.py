"""
Quick test to verify fixtures and datasets work correctly.
"""

import pytest
from datasets.synthetic import simple_meshes


def test_single_peak_mesh_fixture(single_peak_mesh):
    """Test that single_peak_mesh fixture works."""
    assert len(single_peak_mesh.vertices()) == 3
    assert single_peak_mesh.value(0) == 0.0
    assert single_peak_mesh.value(2) == 1.0


def test_two_peaks_mesh_fixture(two_peaks_mesh):
    """Test that two_peaks_mesh fixture works."""
    assert len(two_peaks_mesh.vertices()) == 4
    # Should have two peaks (vertices 2 and 3)
    assert two_peaks_mesh.value(2) == 0.8
    assert two_peaks_mesh.value(3) == 0.9


def test_square_mesh_fixture(square_mesh):
    """Test that square_mesh fixture works."""
    assert len(square_mesh.vertices()) == 4
    # Verify adjacency
    assert 1 in square_mesh.neighbors(0)
    assert 3 in square_mesh.neighbors(0)


def test_direct_import():
    """Test that we can import datasets directly."""
    mesh = simple_meshes.single_peak()
    assert mesh is not None
    assert len(mesh.vertices()) == 3


def test_helper_verify_mesh_invariants(single_peak_mesh):
    """Test the helper function works."""
    from tests.conftest import verify_mesh_invariants
    # Should not raise
    verify_mesh_invariants(single_peak_mesh)


def test_helper_verify_unionfind_invariants(empty_unionfind):
    """Test UnionFind helper."""
    from tests.conftest import verify_unionfind_invariants
    
    # Add some elements
    for i in range(5):
        empty_unionfind.make_set(i, scalar_value=float(i))
    
    # Should not raise
    verify_unionfind_invariants(empty_unionfind, list(range(5)))
