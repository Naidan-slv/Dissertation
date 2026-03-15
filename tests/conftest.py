"""
Root conftest.py for all pytest tests.

Provides shared fixtures and utilities available to all test modules.

Fixtures defined here can be used in any test file without importing.
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import datasets and src
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datasets.synthetic import simple_meshes
from src.contour_tree_algo.sub_algorithms.unionFind import UnionFind


# -----------------------------------------
# Mesh Fixtures
# -----------------------------------------

@pytest.fixture
def single_peak_mesh():
    """
    Single peak mesh - simplest test case.
    Linear path with no joins or splits.
    """
    return simple_meshes.single_peak()


@pytest.fixture
def two_peaks_mesh():
    """
    Two peaks merging at one join point.
    Classic join tree test case.
    """
    return simple_meshes.two_peaks_merge()


@pytest.fixture
def square_mesh():
    """
    Square mesh for adjacency and basic operations testing.
    """
    return simple_meshes.square_mesh()


@pytest.fixture
def three_peaks_mesh():
    """
    Three peaks merging at one point.
    Tests multi-way join behavior.
    """
    return simple_meshes.three_peaks_merge()


@pytest.fixture
def saddle_mesh():
    """
    Mesh with saddle point.
    Has both join and split critical points.
    """
    return simple_meshes.saddle_mesh()


# -----------------------------------------
# Algorithm Fixtures
# -----------------------------------------

@pytest.fixture
def empty_unionfind():
    """
    Fresh UnionFind instance for testing.
    """
    return UnionFind()


# -----------------------------------------
# Helper Functions
# These are utilities, not fixtures.
# Import them explicitly in tests that need them.
# -----------------------------------------

def verify_mesh_invariants(mesh):
    """
    Verify basic mesh properties are satisfied.
    
    Checks:
    - Mesh has vertices
    - Every vertex has a scalar value
    - Neighbors are valid vertex IDs
    - Neighbor lists are deterministic (sorted)
    
    Args:
        mesh: Any Mesh instance
        
    Raises:
        AssertionError: If any invariant is violated
    """
    verts = mesh.vertices()
    assert len(verts) > 0, "Mesh should have at least one vertex"
    
    for v in verts:
        # Every vertex should have a value
        val = mesh.value(v)
        assert val is not None, f"Vertex {v} should have a value"
        assert isinstance(val, (int, float)), f"Value should be numeric, got {type(val)}"
        
        # Neighbors should be valid vertices
        neighbors = mesh.neighbors(v)
        assert isinstance(neighbors, list), "neighbors() should return a list"
        
        for n in neighbors:
            assert n in verts, f"Neighbor {n} of vertex {v} is not in mesh"
        
        # Neighbors should be sorted (deterministic)
        assert neighbors == sorted(neighbors), \
            f"Neighbors of {v} should be sorted: {neighbors}"


def verify_unionfind_invariants(uf, elements):
    """
    Verify UnionFind maintains correct invariants.
    
    Checks:
    - Every element has a parent
    - Every element has a size
    - find() is consistent
    - Root elements are their own parent
    
    Args:
        uf: UnionFind instance
        elements: List of elements that should be in the structure
    """
    for elem in elements:
        # Every element should have a parent
        assert elem in uf.parent, f"Element {elem} missing from parent map"
        assert elem in uf.size, f"Element {elem} missing from size map"
        
        # find() should be consistent
        root = uf.find(elem)
        assert root in uf.parent, f"Root {root} not in parent map"
        
        # Root should be its own parent
        assert uf.parent[root] == root, f"Root {root} should be its own parent"
        
        # Size should be positive
        assert uf.size[root] > 0, f"Component size should be positive"
