"""
Marching tetrahedra isosurface extraction.

Refs: Topological Manipulation of Isosurfaces, Ch 5;
      Simplicial Subdivisions and Sampling Artifacts.
"""


def tetrahedron_triangles(points, values, isovalue):
    """Return triangles cut from one tetrahedron."""
    inside = [value >= isovalue for value in values]
    n_inside = sum(inside)
    if n_inside == 0 or n_inside == 4:
        return []
    raise NotImplementedError


def interpolate_edge(p0, p1, v0, v1, isovalue):
    """Linearly interpolate one isosurface edge crossing."""
    raise NotImplementedError


def extract_isosurface(width, height, depth, data, isovalue):
    """Extract vertices and triangles from a regular grid."""
    raise NotImplementedError
