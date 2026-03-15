"""
Simple synthetic 2D meshes for testing contour tree algorithms.

Each mesh is small enough to verify by hand.
Used for unit testing and algorithm development.

Based on:
- Standard test cases for topological data analysis
- Hand-designed examples for join/split tree verification
"""

from src.meshes.mesh2d import TriMesh2D


def single_peak():
    r"""
    Single peak mesh - simplest possible case.
    No joins or splits - just a monotonic path.
    
    Structure (linear path):
        2 (1.0)  <- peak
        |
        1 (0.5)
        |
        0 (0.0)  <- minimum
    
    Expected behavior:
    - Join tree: linear path 0 → 1 → 2
    - Split tree: linear path 2 → 1 → 0
    - Contour tree: single arc
    """
    values = {
        0: 0.0,
        1: 0.5,
        2: 1.0,
    }
    
    # Single triangle forming a path
    triangles = [
        (0, 1, 2),
    ]
    
    return TriMesh2D(values, triangles)


def two_peaks_merge():
    r"""
    Two peaks merging at one join point.
    Classic test case for join tree construction.
    
    Structure:
       2(0.8)  3(0.9)  <- two peaks
          \   /
          1(0.5)       <- join point
            |
          0(0.1)       <- minimum
    
    Expected behavior:
    - Join tree: 0 → 1, then 2 → 1 and 3 → 1 (join at 1)
    - Split tree: no splits (monotonic from peaks down)
    - Contour tree: Y-shape with join at vertex 1
    """
    values = {
        0: 0.1,
        1: 0.5,
        2: 0.8,
        3: 0.9,
    }
    
    triangles = [
        (0, 1, 2),  # Left branch
        (0, 1, 3),  # Right branch
    ]
    
    return TriMesh2D(values, triangles)


def square_mesh():
    """
    Square mesh split into two triangles.
    Used for testing basic adjacency and mesh operations.
    
    Structure:
        2(0.2) ---- 3(0.9)
        |       /   |
        |    /      |
        0(0.1) ---- 1(0.7)
    
    Triangles: (0,1,3) and (0,3,2)
    
    Expected behavior:
    - All vertices connected (no isolated components)
    - Vertex 0 has degree 3 (connected to 1, 2, 3)
    - Vertices 1 and 2 have degree 2
    - Vertex 3 has degree 3
    """
    values = {
        0: 0.1,
        1: 0.7,
        2: 0.2,
        3: 0.9,
    }
    
    triangles = [
        (0, 1, 3),  # Lower-right triangle
        (0, 3, 2),  # Upper-left triangle
    ]
    
    return TriMesh2D(values, triangles)


def three_peaks_merge():
    r"""
    Three peaks merging at a single join point.
    Tests more complex join behavior.
    
    Structure:
        4(1.0)  3(0.9)  2(0.8)  <- three peaks
           \     |     /
               1(0.5)            <- join point
                 |
               0(0.1)            <- minimum
    
    Expected behavior:
    - Join tree: three branches merging at vertex 1
    - Demonstrates multi-way join
    """
    values = {
        0: 0.1,
        1: 0.5,
        2: 0.8,
        3: 0.9,
        4: 1.0,
    }
    
    triangles = [
        (0, 1, 2),  # Right branch
        (0, 1, 3),  # Middle branch
        (0, 1, 4),  # Left branch
    ]
    
    return TriMesh2D(values, triangles)


def saddle_mesh():
    r"""
    Mesh with a saddle point (both join and split).
    
    Structure:
            3(0.9)           <- peak
           / \
        1(0.5) 2(0.5)       <- saddle region
           \ /
            0(0.1)           <- minimum
    
    Expected behavior:
    - Has both join and split critical points
    - Tests contour tree merge algorithm
    """
    values = {
        0: 0.1,
        1: 0.5,
        2: 0.5,
        3: 0.9,
    }
    
    triangles = [
        (0, 1, 3),
        (0, 2, 3),
    ]
    
    return TriMesh2D(values, triangles)
