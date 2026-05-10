# Interactive viewer notes

The viewer code is split into two layers:

1. Plain Python payload builders for isosurfaces, contour-tree arcs, and linked viewer state.
2. Optional PyVista adapters for rendering those payloads.

This keeps the contour-tree pipeline testable without installing VTK/PyVista.

## Claim boundary

The viewer extracts isosurface geometry with marching tetrahedra over the
project's Freudenthal tetrahedra. The extracted triangles are stored in a
versioned payload before any rendering step. PyVista is only the optional
VTK-backed renderer for that payload.

Contour-tree linking is interval based. An arc is marked active when the current
isovalue lies inside that arc's scalar interval. This follows Carr's active
contour model for the first viewer, but it is not an exact triangle-component to
superarc assignment.

Simplification is displayed as tree context. The payload stores the simplified
tree, active simplified arcs, and Carr-style collapse records. It does not alter
the scalar data, does not re-extract different geometry, and does not implement
Weber-style branch transfer functions or topology-controlled volume rendering.

## Install optional viewer dependencies

From the repository root:

```bash
pip install -r requirements-viewer.txt
```

## Run the tiny viewer example

```bash
python scripts/interactive_viewer_example.py
```

The example uses a `2x2x2` `GridMesh3D` with one high corner and a one-arc contour tree. It is only meant to check the slider and payload wiring before using real datasets.

## Run a Klacansky dataset viewer

The Klacansky script defaults to the small `fuel` dataset:

```bash
python scripts/klacansky_viewer.py
```

You can pass another dataset key from `src/input/datasets.yaml`:

```bash
python scripts/klacansky_viewer.py nucleon --isovalue 42
```

For large datasets, contour-tree computation can still be slow. Start with
`fuel`, `nucleon`, `marschner_lobb`, or another small volume first.

## Export repeatable viewer assets

For dissertation evidence or debugging, export the non-GUI asset bundle:

```bash
python scripts/export_viewer_assets.py fuel --threshold 5 --output-dir output/viewer
```

This writes:

- a linked viewer payload JSON file
- a manifest JSON file recording command, outputs, paper-basis metadata, and `component_mapping = "interval-only"`
- a Graphviz DOT contour-tree graph with interval-active arcs highlighted

Screenshots are optional because PyVista/VTK is not a core dependency:

```bash
python scripts/export_viewer_assets.py fuel --threshold 5 --screenshot
```

If PyVista or off-screen rendering is unavailable, rerun without `--screenshot`.
The JSON and DOT assets do not require PyVista.

## Current limitation

Active contour-tree arcs are marked with interval-only logic:

```text
arc is active if low_value <= isovalue <= high_value
```

This is useful for the MVP viewer, but it is not yet exact connected-component-to-superarc tracking.

Simplification output has the same limitation. It shows how the tree changes and
which simplified arcs are active at the chosen isovalue; it does not label each
rendered triangle by branch.
