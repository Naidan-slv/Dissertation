"""Build simple JSON-style payloads for isosurface triangle meshes."""

VIEWER_PAYLOAD_SCHEMA_VERSION = "viewer-payload-v1"


def build_isosurface_payload(vertices, triangles, isovalue, dataset_name=None):
    """Return points/faces for an already-extracted isosurface."""
    points = [[float(x), float(y), float(z)] for x, y, z in vertices]
    faces = [[int(a), int(b), int(c)] for a, b, c in triangles]
    return {
        "schema_version": VIEWER_PAYLOAD_SCHEMA_VERSION,
        "dataset_name": dataset_name,
        "isovalue": float(isovalue),
        "points": points,
        "faces": faces,
        "triangle_count": len(faces),
    }
