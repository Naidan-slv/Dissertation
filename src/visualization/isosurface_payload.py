"""Build simple JSON-style payloads for isosurface triangle meshes."""


def build_isosurface_payload(vertices, triangles, isovalue):
    """Return points/faces for an already-extracted isosurface."""
    points = [[float(x), float(y), float(z)] for x, y, z in vertices]
    faces = [[int(a), int(b), int(c)] for a, b, c in triangles]
    return {
        "isovalue": float(isovalue),
        "points": points,
        "faces": faces,
        "triangle_count": len(faces),
    }
