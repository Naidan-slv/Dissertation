"""
Marching tetrahedra isosurface extraction.

Refs: Topological Manipulation of Isosurfaces, Ch 5;
      Simplicial Subdivisions and Sampling Artifacts.
"""

from src.meshes.freudenthal_tets import enumerate_tetrahedra


def tetrahedron_triangles(points, values, isovalue):
    """Return triangles cut from one tetrahedron."""
    inside = [value > isovalue for value in values]
    n_inside = sum(inside)
    if n_inside == 0 or n_inside == 4:
        return []
    if n_inside in (1, 3):
        side = True if n_inside == 1 else False
        pivot = inside.index(side)
        tri = []
        for i in range(4):
            if i != pivot:
                point = interpolate_edge(
                    points[pivot], points[i],
                    values[pivot], values[i],
                    isovalue,
                )
                if point is not None:
                    tri.append(point)
        return _valid_triangles([tuple(tri)])

    a, b = [i for i, flag in enumerate(inside) if flag]
    c, d = [i for i, flag in enumerate(inside) if not flag]
    ac = interpolate_edge(points[a], points[c], values[a], values[c], isovalue)
    ad = interpolate_edge(points[a], points[d], values[a], values[d], isovalue)
    bc = interpolate_edge(points[b], points[c], values[b], values[c], isovalue)
    bd = interpolate_edge(points[b], points[d], values[b], values[d], isovalue)
    return _valid_triangles([(ac, ad, bc), (ad, bd, bc)])


def interpolate_edge(p0, p1, v0, v1, isovalue):
    """Linearly interpolate one isosurface edge crossing."""
    if v0 == v1:
        return None
    t = (isovalue - v0) / (v1 - v0)
    return tuple(a + t * (b - a) for a, b in zip(p0, p1))


def _valid_triangles(triangles):
    """Drop triangles with missing or repeated points."""
    valid = []
    for tri in triangles:
        if any(point is None for point in tri):
            continue
        if len(set(tri)) != 3:
            continue
        valid.append(tri)
    return valid


def extract_isosurface(width, height, depth, data, isovalue):
    """Extract vertices and triangles from a regular grid."""
    vertices = []
    triangles = []
    vertex_ids = {}

    def coords(v):
        x = v % width
        y = (v // width) % height
        z = v // (width * height)
        return (x, y, z)

    def add_vertex(point):
        key = tuple(round(coord, 12) for coord in point)
        if key not in vertex_ids:
            vertex_ids[key] = len(vertices)
            vertices.append(point)
        return vertex_ids[key]

    for tet in enumerate_tetrahedra(width, height, depth):
        points = [coords(v) for v in tet]
        values = [data[v] for v in tet]
        for tri in tetrahedron_triangles(points, values, isovalue):
            triangle = tuple(add_vertex(point) for point in tri)
            if len(set(triangle)) == 3:
                triangles.append(triangle)

    return vertices, triangles
