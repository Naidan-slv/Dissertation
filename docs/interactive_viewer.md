# Interactive viewer notes

The viewer code is split into two layers:

1. Plain Python payload builders for isosurfaces, contour-tree arcs, and linked viewer state.
2. Optional PyVista adapters for rendering those payloads.

This keeps the contour-tree pipeline testable without installing VTK/PyVista.

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

## Current limitation

Active contour-tree arcs are marked with interval-only logic:

```text
arc is active if low_value <= isovalue <= high_value
```

This is useful for the MVP viewer, but it is not yet exact connected-component-to-superarc tracking.
