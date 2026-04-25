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
    if n_inside in (1, 3):
        side = True if n_inside == 1 else False
        pivot = inside.index(side)
        tri = []
        for i in range(4):
            if i != pivot:
                tri.append(interpolate_edge(
                    points[pivot], points[i],
                    values[pivot], values[i],
                    isovalue,
                ))
        return [tuple(tri)]
    raise NotImplementedError


def interpolate_edge(p0, p1, v0, v1, isovalue):
    """Linearly interpolate one isosurface edge crossing."""
    t = (isovalue - v0) / (v1 - v0)
    return tuple(a + t * (b - a) for a, b in zip(p0, p1))


def extract_isosurface(width, height, depth, data, isovalue):
    """Extract vertices and triangles from a regular grid."""
    raise NotImplementedError
