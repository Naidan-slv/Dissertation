"""
Freudenthal tetrahedra for regular 3D grids.

Refs: Simplicial Subdivisions and Sampling Artifacts;
      Topological Manipulation of Isosurfaces.
"""


def enumerate_tetrahedra(width, height, depth):
    """Return tetrahedra for all grid cubes."""
    tets = []

    def vid(x, y, z):
        return z * height * width + y * width + x

    for z in range(depth - 1):
        for y in range(height - 1):
            for x in range(width - 1):
                tets.extend(cube_tetrahedra(
                    vid(x, y, z),
                    vid(x + 1, y, z),
                    vid(x, y + 1, z),
                    vid(x + 1, y + 1, z),
                    vid(x, y, z + 1),
                    vid(x + 1, y, z + 1),
                    vid(x, y + 1, z + 1),
                    vid(x + 1, y + 1, z + 1),
                ))
    return tets


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
