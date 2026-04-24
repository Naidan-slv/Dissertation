"""
Freudenthal tetrahedra for regular 3D grids.

Refs: Simplicial Subdivisions and Sampling Artifacts;
      Topological Manipulation of Isosurfaces.
"""


def enumerate_tetrahedra(width, height, depth):
    """Return tetrahedra for all grid cubes."""
    raise NotImplementedError


def cube_tetrahedra(c000, c100, c010, c110, c001, c101, c011, c111):
    """Return the six tetrahedra for one cube."""
    return [
        (c000, c100, c110, c111),
        (c000, c100, c101, c111),
        (c000, c010, c110, c111),
        (c000, c010, c011, c111),
        (c000, c001, c101, c111),
        (c000, c001, c011, c111),
    ]
