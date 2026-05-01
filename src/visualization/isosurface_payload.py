"""Build simple JSON-style payloads for isosurface triangle meshes.

This is the small hand-off point between the extraction code and the future
viewer. Keeping it plain Python means PyVista can stay optional.
"""

VIEWER_PAYLOAD_SCHEMA_VERSION = "viewer-payload-v1"


def _dedupe_points(vertices):
    """Return unique points and an old-index to new-index remap."""
    points = []
    remap = []
    seen = {}

    for x, y, z in vertices:
        point = [float(x), float(y), float(z)]
        # The marching code already rounds generated coordinates; this just
        # keeps the viewer payload stable if the same point appears twice.
        key = tuple(round(value, 12) for value in point)
        if key not in seen:
            seen[key] = len(points)
            points.append(point)
        remap.append(seen[key])

    return points, remap


def _bounds(points):
    """Return the mesh bounding box, mainly for later camera setup."""
    if not points:
        return None

    xs, ys, zs = zip(*points)
    return {
        "x": [min(xs), max(xs)],
        "y": [min(ys), max(ys)],
        "z": [min(zs), max(zs)],
    }


def _scalar_range_payload(scalar_range):
    """Store slider range metadata in a JSON-friendly shape."""
    if scalar_range is None:
        return None

    low, high = scalar_range
    return [float(low), float(high)]


def build_isosurface_payload(vertices, triangles, isovalue, dataset_name=None, scalar_range=None):
    """Return a stable viewer payload for an already-extracted isosurface."""
    points, remap = _dedupe_points(vertices)
    faces = []

    for a, b, c in triangles:
        face = [remap[int(a)], remap[int(b)], remap[int(c)]]
        # Once duplicate points are merged, some triangles collapse to a line.
        # Dropping those here avoids odd rendering artefacts later.
        if len(set(face)) == 3:
            faces.append(face)

    return {
        "schema_version": VIEWER_PAYLOAD_SCHEMA_VERSION,
        "dataset_name": dataset_name,
        "isovalue": float(isovalue),
        "scalar_range": _scalar_range_payload(scalar_range),
        "bounds": _bounds(points),
        "points": points,
        "faces": faces,
        "triangle_count": len(faces),
    }
