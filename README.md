# Contour Tree Algorithm Implementation - Complete Guide

**University Dissertation Project**  
Implementing the Carr et al. (2003) contour tree algorithm for volumetric scalar fields.

---

## Quick Navigation

- [Quick Start](#quick-start)
- [Key Concepts](#key-concepts--terminology)
- [Meshes in This Project](#meshes-in-this-project-and-why-they-exist)
- [How Everything Fits Together](#how-everything-fits-together)
- [How to Run](#how-to-run-the-code)
- [Dataset Files](#dataset-files-and-attribution)
- [Critical Points & Super-arcs](#critical-points--super-arcs-explained)
- [Pipeline Overview](#complete-pipeline-workflow)
- [Advanced Features](#advanced-features)
- [Isosurface Extraction and Viewer](#isosurface-extraction-and-viewer)
- [File Structure](#file-structure)
- [Examples](#examples)
- [References](#references)

---

## Quick Start

### One-Minute Setup

```bash
# Activate environment
source .venv/bin/activate

# Run full benchmark (generates results table)
python scripts/results_table.py

# Run specific datasets
python scripts/results_table.py fuel neghip hydrogen_atom
```

### Expected Output

```
Running 10 dataset(s)...

  marschner_lobb        68,921 verts  →   1,506 critical pts,  1,505 arcs  (1.18s)  PASS
  nucleon               68,921 verts  →     579 critical pts,    578 arcs  (1.16s)  PASS
  fuel                 262,144 verts  →     344 critical pts,    343 arcs  (4.62s)  PASS
```

---

## Key Concepts & Terminology

### Scalar Field / Volumetric Data

A 3D array of numerical values representing a measured property at each location.

**Examples:**
- Medical imaging (CT/MRI): density values
- Simulation data: pressure, temperature, velocity
- Scientific data: mineral concentration, electron density

**Storage:** Binary `.raw` files (little-endian format), size = width × height × depth

### Mesh / Tetrahedral Mesh

Representation of the scalar field as:
- **Vertices**: points with coordinates and scalar values
- **Tetrahedra**: 4-vertex 3D elements (simplices)
- **Adjacency**: neighbor relationships

The contour-tree algorithms only need vertices, neighbours, and scalar values.
The tetrahedra matter because they define the 3D grid connectivity and later
provide the cells used by marching tetrahedra for isosurface extraction.

### Critical Point (Supernode)

A vertex where scalar field topology changes:

| Type | Degree | Example |
|------|--------|---------|
| Local Minimum | 1 | Valley, ocean depth |
| Local Maximum | 1 | Mountain peak, high pressure |
| Saddle Point | ≥3 | Mountain pass, river confluence |

**Key insight:** Regular (non-critical) points have degree 2.

### Super-arc (Superarc)

An edge connecting two critical points in the reduced contour tree.

**One super-arc represents an entire path** with no critical points in between.

**Example:**
```
Original mesh:    Min -- V1 -- V2 -- V3 -- Saddle
After reduction:  Min ================ Saddle (1 super-arc)
```

### Join Tree

Tracks how upper/ascending components merge. In this code it is implemented by
processing vertices from **highest to lowest** scalar value and looking at
higher-valued neighbours that have already been inserted.

- Records merge events as join-tree edges
- Uses union-find to maintain connected components
- Algorithm: Union-Find based, O(n α(n))

### Split Tree

Dual of the join tree. It tracks how lower/descending components split. In this
code it is implemented by processing vertices from **lowest to highest** scalar
value and looking at lower-valued neighbours that have already been inserted.

- Records split events as split-tree edges
- Uses the same union-find idea with highest-vertex tracking

### Merge Algorithm

Combines join + split trees to create **canonical contour tree**.

**Why:** Join/split trees are not unique; merge produces THE minimal representation.

### Union-Find

Data structure efficiently tracking components:

| Operation | Purpose | Time |
|-----------|---------|------|
| make_set(v) | Create singleton {v} | O(1) |
| find(v) | Get component representative | O(α(n)) |
| union(a, b) | Merge two sets | O(α(n)) |
| lowest_in_component(v) | Get min element in component | O(1) |

**Performance:** Nearly O(1) per operation (α(n) ≈ 4-5 for practical sizes)

### Reduce Algorithm

Converts fully augmented tree to reduced form:

1. Identify critical points (degree ≠ 2)
2. Contract all degree-2 paths into super-arcs
3. Result: only critical points + super-arcs

**Formula:**
```
superarcs = critical_points - 1  (for connected component)
```

### Verification

6 correctness checks per dataset:
1. Tree structure (acyclic + connected)
2. Edge monotonicity (f(u) ≤ f(v))
3. Join validity
4. Split validity
5. Leaf extrema
6. Contour tree ⊆ join tree ∪ split tree

---

## Meshes in This Project and Why They Exist

The project has several mesh classes because each stage needs a slightly
different level of control. The contour-tree code itself is generic: it accepts
anything implementing the `Mesh` interface, meaning it can run on tiny hand-made
examples and real volumetric datasets without changing the algorithm.

| Mesh / helper | File | Why it exists | Used in |
|---|---|---|---|
| `Mesh` | `src/meshes/mesh.py` | Abstract interface: `vertices()`, `neighbors(v)`, `value(v)`, and deterministic scalar sorting. | All join/split/merge tests and all real runs. |
| `TriMesh2D` | `src/meshes/mesh2d.py` | Small 2D triangulated meshes where expected contour-tree behaviour can be checked by hand. | Early unit tests and synthetic fixtures. |
| `GridMesh` | `src/meshes/grid_mesh.py` | 2D grid with explicit edges, needed to match the Carr 9×9 paper example exactly. | Carr paper validation tests. |
| `GridMesh3D` | `src/meshes/grid_mesh_3d.py` | Main mesh for `.raw` volumes. Stores scalar samples on a regular 3D grid and exposes Freudenthal-style 14-neighbour adjacency. | Klacansky datasets, full pipeline, viewer, benchmarks. |
| Freudenthal tetrahedra | `src/meshes/freudenthal_tets.py` | Enumerates six tetrahedra per grid cube around a fixed body diagonal. | Marching tetrahedra isosurface extraction. |

### Why both adjacency and tetrahedra are present

For the contour tree, only graph adjacency is required. That is why `GridMesh3D`
stores neighbour relationships rather than a large explicit tetrahedron list for
every dataset. For isosurface extraction, the cells are needed, so
`freudenthal_tets.py` enumerates tetrahedra when marching tetrahedra is run.

This keeps the tree computation memory-light while still using the same
Freudenthal grid model for visualisation.

---

## How Everything Fits Together

The implementation is a pipeline of small algorithms. Each stage has a clear
input and output, and later stages reuse those outputs rather than recomputing
the whole structure.

| Stage | Main function/module | Input | Output | Why it matters |
|---|---|---|---|---|
| Load data | `load_raw_volume()` / `load_raw_dataset()` | Dataset name or `.raw` file | Flat data array and dimensions, or `GridMesh3D` | Converts raw volumes into a mesh the algorithms can use. |
| Join sweep | `compute_join_tree()` | `Mesh` | Join-tree edges | Captures where upper components merge. |
| Split sweep | `compute_split_tree()` | `Mesh` | Split-tree edges | Captures the dual splitting structure. |
| Merge | `merge_trees()` | Join edges, split edges, scalar values | Augmented contour-tree edges | Produces the full contour tree. |
| Reduce | `reduce_contour_tree()` | Augmented contour-tree edges | `supernodes`, `superarcs` | Contracts regular degree-2 paths into critical-point arcs. |
| Verify | `verify_all()` | Mesh and tree outputs | Errors/info lists | Checks the computed tree structure. |
| Persistence ranking | `compute_persistence_pairs()` | `supernodes`, `superarcs`, values | Leaf-saddle feature records | Ranks branches by height difference. |
| Local measures | `compute_arc_measures()` | Mesh and tree paths | Per-arc measure records | Gives geometric/count-based branch information. |
| Simplification | `simplify_contour_tree()` | Tree, values, optional measures | Simplified tree and collapse records | Applies Carr-style leaf pruning and vertex collapse. |
| Marching tetrahedra | `extract_isosurface()` | Grid dimensions, data, isovalue | Triangle vertices and faces | Extracts the visible isosurface. |
| Viewer payload | `build_viewer_payload()` | Mesh, tree, isovalue | JSON-style linked payload | Connects isosurface geometry with active tree arcs. |
| PyVista adapter | `pyvista_adapter.py` | Viewer/isurface payload | `PolyData` / plotter | Optional rendering layer. |

The most important split is this:

- **Topology pipeline:** mesh → join/split → merge → reduce → simplify.
- **Geometry pipeline:** grid data → Freudenthal tetrahedra → marching tetrahedra → triangle payload.
- **Viewer pipeline:** tree payload + isosurface payload → optional PyVista rendering.

---

## How to Run the Code

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Main Commands

| Command | Purpose |
|---------|---------|
| `python scripts/results_table.py` | Full benchmark all datasets below the default size limit |
| `python scripts/results_table.py fuel neghip` | Specific datasets |
| `python scripts/results_table.py --all` | All configured datasets, including large ones |
| `python scripts/run_full_pipeline.py fuel` | Full pipeline with detailed output for one dataset |
| `python scripts/run_full_pipeline.py --file volume.raw --shape 64 64 64 --dtype uint8` | Load and process a custom `.raw` file |
| `python scripts/viewer_payload_example.py` | Build a tiny linked viewer payload without opening a GUI |
| `python scripts/export_viewer_assets.py fuel --threshold 5` | Export viewer JSON, manifest, and DOT graph assets |
| `python scripts/export_viewer_assets.py fuel --screenshot` | Also request an optional PyVista screenshot |
| `python scripts/klacansky_viewer.py fuel --isovalue 42` | Open the optional PyVista viewer for a Klacansky dataset |
| `python scripts/klacansky_viewer.py --file volumes/demo.raw --shape 128 128 64 --dtype uint16` | Open the optional PyVista viewer for an arbitrary raw volume |
| `python scripts/export_viewer_assets.py --file volumes/demo.raw --shape 128 128 64 --dtype uint16 --output-dir output/viewer` | Export viewer assets for an arbitrary raw volume |
| `python -m src.benchmarks.timing_plots` | Generate serial Python timing JSON/CSV files and plots under `output/` |
| `python scripts/ttk_comparison.py --project-nodes 4 --project-arcs 3 --ttk-summary ttk.txt` | Compare project counts with a saved TTK-style summary |

Interactive viewing and screenshot export require the optional viewer dependency file:

```bash
pip install -r requirements-viewer.txt
```

Generated evidence files are ignored by git. Regenerate them with the scripts
above, or copy selected final figures into a separate dissertation-assets folder
if they must be archived outside the source history.

### Dataset files and attribution

The raw volumes used by this project come from Pavol Klacansky's Open Scientific
Visualization Datasets collection:

- Open SciVis page: <http://klacansky.com/open-scivis-datasets/>
- Open SciVis metadata: <http://klacansky.com/open-scivis-datasets/datasets.json>
- Local manifest used by the loader: `src/input/datasets.yaml`
- Local data folder expected by the loader: `datasets/klacansky/`

The repository keeps the smaller configured raw volumes locally. Larger raw
volumes can be installed when needed by downloading the original `.raw` file
from Open SciVis and placing it in `datasets/klacansky/` with the same file name
used in `src/input/datasets.yaml`.

For example, the `fuel` entry expects:

```text
datasets/klacansky/fuel_64x64x64_uint8.raw
```

Each entry in `src/input/datasets.yaml` contains:

| Field | Meaning |
|---|---|
| `path` | Path to the `.raw` file, relative to the repository root. |
| `shape_whd` | Dimensions as `[width, height, depth]`, matching the Open SciVis size and file name. |
| `dtype` | NumPy dtype string such as `uint8`, `uint16`, `int16` or `float32`. |
| `category` | Descriptive category used in reports/manifests. It is not used by the algorithm. |

The raw stream is interpreted in C-style order as `array[z][y][x]`, so `x`
changes fastest, then `y`, then `z`. If a configured raw file is not present,
the loader raises `FileNotFoundError`.

Klacansky/Open SciVis is the place this project obtained the volumes from. The
individual datasets were not all created by Klacansky, so the original Open
SciVis acknowledgements are preserved below.

| Dataset key | Source file | Role | Original acknowledgement / citation note |
|---|---|---|---|
| `aneurism` | <http://klacansky.com/open-scivis-datasets/aneurism/aneurism_256x256x256_uint8.raw> | 15-dataset comparison | volvis.org and Philips Research, Hamburg, Germany |
| `blunt_fin` | <http://klacansky.com/open-scivis-datasets/blunt_fin/blunt_fin_256x128x64_uint8.raw> | viewer example | NASA Advanced Supercomputing Division, USA |
| `bonsai` | <http://klacansky.com/open-scivis-datasets/bonsai/bonsai_256x256x256_uint8.raw> | 15-dataset comparison | volvis.org and S. Roettger, VIS, University of Stuttgart |
| `boston_teapot` | <http://klacansky.com/open-scivis-datasets/boston_teapot/boston_teapot_256x256x178_uint8.raw> | 15-dataset comparison | volvis.org and Terarecon Inc, MERL, Brigham and Women's Hospital |
| `carp` | <http://klacansky.com/open-scivis-datasets/carp/carp_256x256x512_uint16.raw> | optional local dataset | Michael Scheuring, Computer Graphics Group, University of Erlangen, Germany |
| `csafe_heptane` | <http://klacansky.com/open-scivis-datasets/csafe_heptane/csafe_heptane_302x302x302_uint8.raw> | optional local dataset | The University of Utah Center for the Simulation of Accidental Fires and Explosions |
| `engine` | <http://klacansky.com/open-scivis-datasets/engine/engine_256x256x128_uint8.raw> | 15-dataset comparison | volvis.org and General Electric |
| `foot` | <http://klacansky.com/open-scivis-datasets/foot/foot_256x256x256_uint8.raw> | 15-dataset comparison | volvis.org and Philips Research, Hamburg, Germany |
| `frog` | <http://klacansky.com/open-scivis-datasets/frog/frog_256x256x44_uint8.raw> | viewer example | Lawrence Berkeley Laboratory, USA |
| `fuel` | <http://klacansky.com/open-scivis-datasets/fuel/fuel_64x64x64_uint8.raw> | 15-dataset comparison and examples | volvis.org and SFB 382 of the German Research Council (DFG) |
| `hydrogen_atom` | <http://klacansky.com/open-scivis-datasets/hydrogen_atom/hydrogen_atom_128x128x128_uint8.raw> | 15-dataset comparison and viewer example | volvis.org and SFB 382 of the German Research Council (DFG) |
| `lobster` | <http://klacansky.com/open-scivis-datasets/lobster/lobster_301x324x56_uint8.raw> | 15-dataset comparison | volvis.org and VolVis distribution of SUNY Stony Brook, NY, USA |
| `marschner_lobb` | <http://klacansky.com/open-scivis-datasets/marschner_lobb/marschner_lobb_41x41x41_uint8.raw> | 15-dataset comparison and examples | volvis.org and Marschner and Lobb |
| `mri_ventricles` | <http://klacansky.com/open-scivis-datasets/mri_ventricles/mri_ventricles_256x256x124_uint8.raw> | optional local dataset | volvis.org and Dirk Bartz, VCM, University of Tübingen, Germany |
| `mri_woman` | <http://klacansky.com/open-scivis-datasets/mri_woman/mri_woman_256x256x109_uint16.raw> | optional local dataset | Siemens Medical Systems, Inc., Iselin, NJ, USA |
| `mrt_angio` | <http://klacansky.com/open-scivis-datasets/mrt_angio/mrt_angio_416x512x112_uint16.raw> | optional local dataset | volvis.org and Özlem Gürvit, Institute for Neuroradiology, Frankfurt, Germany |
| `neghip` | <http://klacansky.com/open-scivis-datasets/neghip/neghip_64x64x64_uint8.raw> | 15-dataset comparison | volvis.org and VolVis distribution of SUNY Stony Brook, NY, USA. Open SciVis also supplies the VolVis paper citation: Avila et al., “VolVis: A Diversified System for Volume Research and Development”, Proceedings Visualization '94, DOI `10.1109/VISUAL.1994.346340`. |
| `neocortical_layer_1_axons` | <http://klacansky.com/open-scivis-datasets/neocortical_layer_1_axons/neocortical_layer_1_axons_1464x1033x76_uint8.raw> | install locally if needed | V. De Paola, MRC Clinical Sciences Center, Imperial College London. Open SciVis also supplies the article citation: De Paola et al., “Cell Type-Specific Structural Plasticity of Axonal Branches and Boutons in the Adult Neocortex”, Neuron 49(6), 2006, DOI `10.1016/j.neuron.2006.02.017`. |
| `nucleon` | <http://klacansky.com/open-scivis-datasets/nucleon/nucleon_41x41x41_uint8.raw> | 15-dataset comparison and examples | volvis.org and SFB 382 of the German Research Council (DFG) |
| `pancreas` | <http://klacansky.com/open-scivis-datasets/pancreas/pancreas_240x512x512_int16.raw> | install locally if needed | Roth HR, Lu L, Farag A, Shin H-C, Liu J, Turkbey EB, Summers RM. DeepOrgan: Multi-level Deep Convolutional Networks for Automated Pancreas Segmentation. MICCAI 2015, LNCS 9349, pp. 556--564. |
| `shockwave` | <http://klacansky.com/open-scivis-datasets/shockwave/shockwave_64x64x512_uint8.raw> | 15-dataset comparison | volvis.org |
| `silicium` | <http://klacansky.com/open-scivis-datasets/silicium/silicium_98x34x34_uint8.raw> | 15-dataset comparison | volvis.org and VolVis distribution of SUNY Stony Brook, NY, USA. Open SciVis also supplies the VolVis paper citation: Avila et al., “VolVis: A Diversified System for Volume Research and Development”, Proceedings Visualization '94, DOI `10.1109/VISUAL.1994.346340`. |
| `skull` | <http://klacansky.com/open-scivis-datasets/skull/skull_256x256x256_uint8.raw> | 15-dataset comparison and viewer example | volvis.org and Siemens Medical Solutions, Forchheim, Germany |
| `statue_leg` | <http://klacansky.com/open-scivis-datasets/statue_leg/statue_leg_341x341x93_uint8.raw> | 15-dataset comparison | volvis.org and German Federal Institute for Material Research and Testing (BAM), Berlin, Germany |
| `stent` | <http://klacansky.com/open-scivis-datasets/stent/stent_512x512x174_uint16.raw> | optional local dataset | volvis.org and Michael Meißner, Viatronix Inc., USA |
| `tacc_turbulence` | <http://klacansky.com/open-scivis-datasets/tacc_turbulence/tacc_turbulence_256x256x256_float32.raw> | optional local dataset | Dataset provided by Gregory D. Abram and Gregory P. Johnson, Texas Advanced Computing Center, The University of Texas at Austin. Simulation by Diego A. Donzis, Texas A&M University, and P. K. Yeung, Georgia Tech. |
| `tooth` | <http://klacansky.com/open-scivis-datasets/tooth/tooth_103x94x161_uint8.raw> | optional local dataset | No acknowledgement string supplied in the Open SciVis metadata. |
| `vis_male` | <http://klacansky.com/open-scivis-datasets/vis_male/vis_male_128x256x256_uint8.raw> | optional local dataset | National Library of Medicine, National Institutes of Health, USA |

### Save Results

```bash
python scripts/results_table.py > results.txt
cat results.txt
```

### Python Interactive Mode

```python
# Load dataset
from src.input.ingest import load_raw_volume
data, w, h, d = load_raw_volume("fuel")
print(f"Loaded: {w}×{h}×{d}")

# Create mesh
from src.meshes.grid_mesh_3d import GridMesh3D
mesh = GridMesh3D(width=w, height=h, depth=d, data=data)

# Compute join tree
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
edges = compute_join_tree(mesh)
print(f"Join tree: {len(edges)} edges")
```

### Run Tests

```bash
pytest                         # All tests
pytest tests/contour_tree -v   # Specific module
pytest -k "join" -v            # Match by name
```

---

## Critical Points & Super-arcs Explained

### How They're Calculated

**STEP 1: JOIN SWEEP**
```
Implementation order: high → low
Tracks: where upper/ascending components merge
Result: Join tree edges
```

**STEP 2: SPLIT SWEEP**
```
Implementation order: low → high
Tracks: where lower/descending components split
Result: Split tree edges
```

**STEP 3: MERGE**
```
Combine join + split trees
Remove redundant edges
Result: Canonical contour tree
```

**STEP 4: REDUCE**
```
Contract all degree-2 vertices into super-arcs
Result: Critical points + super-arcs
```

### Formula

For one connected component:
```
# super-arcs = # critical points - 1
```

**Validation from your table:**
- marschner_lobb: 1,506 critical pts -> 1,505 arcs
- fuel: 344 critical pts -> 343 arcs
- tooth: 231,242 critical pts -> 231,241 arcs

---

## Complete Pipeline Workflow

```
.raw File → 1D Array → 3D Array → Tetrahedral Mesh
   ↓
Sort vertices by scalar value
   ↓
JOIN SWEEP (high → low) → Join tree edges
   ↓
SPLIT SWEEP (low → high) → Split tree edges
   ↓
MERGE → Canonical contour tree
   ↓
REDUCE → Critical points + super-arcs
   ↓
VERIFY → 6 correctness checks
   ↓
Results: timing + statistics
```

### Timing Breakdown

Example (marschner_lobb):
```
Join:    0.46s  (12%)
Split:   0.44s  (12%)
Merge:   0.21s  (6%)
Reduce:  0.07s  (2%)
─────────────────
Total:   1.18s
```

---

## Advanced Features

The core contour tree is only the first layer. The dissertation code also adds
feature ranking, local measures, simplification, and visualisation support.

### Persistence / height feature ranking

`src/contour_tree_algo/persistence.py` works on the reduced contour tree. It
finds leaf-to-saddle branches and records a height difference:

```
persistence = |f(leaf) - f(saddle)|
```

The output is a list of `PersistencePair` records. These records are useful for
ranking which small branches should be simplified first. This is contour-tree
feature ranking, not a full persistent-homology diagram.

### Local arc measures

`src/contour_tree_algo/measures.py` stores per-superarc information such as
vertex counts, path lengths, and cell counts. These values provide geometric or
count-based feature information for comparison and simplification.

### Simplification

`src/contour_tree_algo/simplification.py` implements Carr-style simplification:

1. Collapse regular degree-2 vertices.
2. Put legal leaf edges in a priority queue.
3. Prune the least important legal leaf.
4. If pruning makes the neighbouring vertex regular, collapse it immediately.
5. Store `CollapseRecord` entries so the simplification can be inspected.

The simplification output is a `SimplificationResult` containing the simplified
edges, removed edge ids, and collapse records. The viewer later packages this as
a simplification payload.

### TTK comparison fallback

`scripts/ttk_comparison.py` is a fallback comparison helper for saved TTK-style
text or CSV summaries. It compares only contour-tree node and arc counts. It is
not a live TTK validation unless TTK is installed and a live TTK run has actually
been performed.

The parser deliberately distinguishes input mesh vertices from contour-tree
nodes: labels such as `vertices` are ignored, while labels such as
`critical_points`, `supernodes`, `nodes`, or `tree nodes` are accepted.

### Scalability outputs

`src/benchmarks/timing_plots.py` reports serial Python timings for selected
datasets. The scalability CSV records dataset name, vertex count, reduced tree
size, tree ratio, join/split/merge/reduce timings, threshold, and notes. It does
not claim parallel speedups or TTK performance parity.

---

## Isosurface Extraction and Viewer

The contour tree describes topology, but the viewer also needs geometry. That is
handled by the marching tetrahedra path.

### Marching tetrahedra

`src/isosurface/marching_tet.py` extracts triangles for one isovalue:

1. `freudenthal_tets.py` splits each grid cube into six tetrahedra.
2. Each tetrahedron is classified against the isovalue.
3. Edge crossings are linearly interpolated.
4. The output is a list of triangle vertices and triangle faces.

This keeps the rendered isosurface in the same piecewise-linear setting as the
3D grid used by the contour-tree computation.

### Viewer payloads

The viewer code is split so tests can run without PyVista:

| Payload | File | Meaning |
|---|---|---|
| Isosurface payload | `src/visualization/isosurface_payload.py` | Points, triangle faces, bounds, scalar range. |
| Contour-tree payload | `src/visualization/contour_tree_payload.py` | Nodes, arcs, scalar intervals, active arcs at an isovalue. |
| Linked viewer payload | `src/visualization/viewer_payload.py` | Combines surface geometry and contour-tree state. |
| Simplification payload | `src/visualization/simplification_payload.py` | Simplified tree, active simplified arcs, and collapse records. |

The simplification viewer payload is tree/context data. It does not change the
isosurface geometry; it shows how the contour tree changes after simplification.

### Optional rendering

`src/visualization/pyvista_adapter.py` converts triangle payloads into PyVista
`PolyData`. `src/visualization/interactive_viewer.py` wires that into a simple
isovalue slider. `src/visualization/dot_export.py` exports Graphviz DOT text for
tree inspection, with active arcs highlighted when an isovalue is supplied.

`scripts/export_viewer_assets.py` writes a repeatable asset bundle for a dataset:

- linked viewer payload JSON
- manifest JSON with command, output paths, paper-basis metadata, and
   `component_mapping = "interval-only"`
- Graphviz DOT contour-tree graph
- optional PyVista screenshot when `--screenshot` is supplied

The screenshot path is optional because PyVista/VTK is not a core dependency.

### What the 3D visualisation path supports

There are three practical outputs in this repository:

1. **Interactive 3D isosurface viewing** via `scripts/klacansky_viewer.py`.
2. **Static screenshot export** via `scripts/export_viewer_assets.py --screenshot`.
3. **Non-GUI viewer payload export** (JSON + DOT) for later inspection or custom front ends.

The 3D rendered object is the project's own marching-tetrahedra isosurface.
PyVista is only the optional renderer.

### Named datasets vs arbitrary raw files

The viewer/export scripts now support both:

- named datasets from `src/input/datasets.yaml`
- arbitrary `.raw` files when you supply shape and dtype explicitly

For arbitrary raw files, the scripts need:

- `--file path/to/data.raw`
- `--shape W H D`
- optional `--dtype` (default `uint8`)

The shape order is:

- `W = width = x dimension`
- `H = height = y dimension`
- `D = depth = z dimension`

So:

```text
--shape W H D  ==  --shape X Y Z
```

The raw file is interpreted in C-style order:

```text
array[z][y][x]
```

meaning:

- `x` changes fastest in the file,
- then `y`,
- then `z`.

Example viewer command:

```bash
python scripts/klacansky_viewer.py \
   --file datasets/my_volume.raw \
   --shape 128 128 64 \
   --dtype uint16 \
   --isovalue 42
```

Example asset export command:

```bash
python scripts/export_viewer_assets.py \
   --file datasets/my_volume.raw \
   --shape 128 128 64 \
   --dtype uint16 \
   --output-dir output/viewer
```

The exported payload uses the raw file stem as `dataset_name`.

Example interpretation:

```text
--shape 128 128 64
```

means:

- width/x = 128
- height/y = 128
- depth/z = 64

This is a volume with 128 samples along x, 128 along y, and 64 along z.

The current viewer marks arcs by scalar interval only:

```
arc is active if low_value <= isovalue <= high_value
```

It does not yet assign every rendered triangle component to a specific contour
tree branch.

### Practical limitations users should expect

The viewer path is general, but not every dataset is equally convenient to view.

- **Memory use:** the workflow loads the full volume, builds a `GridMesh3D`, computes the reduced contour tree, and extracts an isosurface. Large volumes can therefore be expensive before rendering even begins.
- **Interactive performance:** very large volumes may be slow to open or update when the slider moves. Start with `fuel`, `nucleon`, `marschner_lobb`, or `neghip` first.
- **Raw-file metadata is manual:** for arbitrary `.raw` files the code cannot infer width, height, depth, dtype, or semantic axis meaning. You must provide correct shape/dtype yourself.
- **No arbitrary file manifest metadata:** named datasets carry category/source metadata in `datasets.yaml`; arbitrary files do not.
- **Viewer linkage is interval only:** an arc is marked active if the isovalue lies within that arc's scalar interval. This is not exact connected-component-to-superarc tracking.
- **Simplification is tree context only:** simplification changes the stored tree payload, not the extracted triangle mesh.
- **PyVista is optional:** JSON/DOT asset export works without PyVista, but interactive viewing and screenshots require `requirements-viewer.txt`.

---

## File Structure

```
Diss Code/
├── datasets/
│   ├── klacansky/             # Real volumetric .raw datasets
│   └── synthetic/             # Small hand-built fixtures
├── docs/
│   └── interactive_viewer.md  # Optional viewer notes and limitations
├── src/
│   ├── input/
│   │   ├── ingest.py          # .raw file loading
│   │   ├── datasets.yaml      # Dataset manifest
│   ├── meshes/
│   │   ├── mesh.py            # Abstract interface
│   │   ├── mesh2d.py          # 2D triangle mesh
│   │   ├── grid_mesh.py       # 2D grid mesh
│   │   ├── grid_mesh_3d.py    # 3D Freudenthal-adjacency grid mesh
│   │   └── freudenthal_tets.py # Six tetrahedra per grid cube
│   ├── contour_tree_algo/
│   │   ├── sub_algorithms/
│   │   │   ├── join_sweep.py      # Join tree sweep
│   │   │   ├── split_sweep.py     # Split tree sweep
│   │   │   ├── merge.py           # Merge join + split trees
│   │   │   └── unionFind.py       # Union-Find
│   │   ├── reduce.py              # Algorithm 7.4 (Reduce)
│   │   ├── final_contour_tree.py  # Full pipeline entry point
│   │   ├── persistence.py         # Leaf-saddle feature ranking
│   │   ├── measures.py            # Local arc measures
│   │   ├── simplification.py      # Leaf pruning + vertex collapse
│   │   └── verify.py              # Correctness checks
│   ├── isosurface/
│   │   └── marching_tet.py        # Marching tetrahedra extraction
│   ├── visualization/
│   │   ├── isosurface_payload.py
│   │   ├── contour_tree_payload.py
│   │   ├── viewer_payload.py
│   │   ├── simplification_payload.py
│   │   ├── pyvista_adapter.py
│   │   ├── interactive_viewer.py
│   │   ├── dataset_viewer.py
│   │   └── dot_export.py
│   └── benchmarks/
│       └── timing_plots.py
├── scripts/
│   ├── results_table.py
│   ├── run_full_pipeline.py
│   ├── export_viewer_assets.py
│   ├── ttk_comparison.py
│   ├── viewer_payload_example.py
│   ├── interactive_viewer_example.py
│   └── klacansky_viewer.py
├── tests/
│   ├── contour_tree/
│   │   ├── test_join_sweep/
│   │   ├── test_split_sweep/
│   │   ├── test_merge/
│   │   ├── test_reduce/
│   │   ├── test_persistence/
│   │   ├── test_measures/
│   │   ├── test_simplification/
│   │   ├── test_unionfind/
│   │   └── integration/
│   ├── isosurface/
│   ├── visualization/
│   └── conftest.py
├── requirements.txt
└── requirements-viewer.txt    # Optional PyVista/VTK dependency set
```

---

## Examples

### Example 1: Run Full Benchmark

```bash
$ python scripts/results_table.py

Output:
  marschner_lobb     68,921 verts  →   1,506 crit pts,  1,505 arcs  (1.18s)  PASS
  nucleon            68,921 verts  →     579 crit pts,    578 arcs  (1.16s)  PASS
  fuel              262,144 verts  →     344 crit pts,    343 arcs  (4.62s)  PASS
```

### Example 2: Load Data

```python
from src.input.ingest import load_raw_volume
from src.meshes.grid_mesh_3d import GridMesh3D

# Load
data, w, h, d = load_raw_volume("fuel")

# Create mesh
mesh = GridMesh3D(width=w, height=h, depth=d, data=data)
print(f"Mesh: {len(mesh.vertices()):,} vertices")
```

### Example 3: Full Pipeline

```python
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.reduce import reduce_contour_tree

# Compute
join_edges = compute_join_tree(mesh)
split_edges = compute_split_tree(mesh)
ct_edges = merge_trees(join_edges, split_edges, mesh.value)
supernodes, superarcs = reduce_contour_tree(ct_edges)

print(f"Critical points: {len(supernodes)}")
print(f"Super-arcs: {len(superarcs)}")
```

---

## References

**PRIMARY:**
- Carr, H., Snoeyink, J., Axen, U. (2003)
  "Computing Contour Trees in All Dimensions"
  *Computational Geometry*, 24(3), 75-94.

- Carr, H. (2004)
   "Topological Manipulation of Isosurfaces"
   PhD thesis. Used for implementation details on contour-tree construction,
   local measures, simplification, and viewer concepts.

**INTRODUCTION:**
- van Kreveld, M., van Oostrum, R., Bajaj, C., Pascucci, V., Schikore, D.R. (1997)
  "Contour Trees and Small Seed Sets for Isosurface Traversal"
  *Symposium on Computational Geometry*, pp. 212-220.

**UNION-FIND:**
- Tarjan, R.E. (1975)
  "Efficiency of a Good But Not Linear Set Union Algorithm"
  *Journal of the ACM*, 22(2), 215-225.

**FREUDENTHAL / ISOSURFACES:**
- Carr, H., Möller, T., Snoeyink, J. (2001)
   "Simplicial Subdivisions and Sampling Artifacts"

- Lorensen, W.E., Cline, H.E. (1987)
   "Marching Cubes: A High Resolution 3D Surface Construction Algorithm"

- Van Gelder, A., Wilhelms, J. (1994)
   "Topological Considerations in Isosurface Generation"

**SIMPLIFICATION / MEASURES:**
- Edelsbrunner, H., Letscher, D., Zomorodian, A. (2002)
   "Topological Persistence and Simplification"

- Takahashi, S., Takeshima, Y., Fujishiro, I. (2004)
   Scalar-field-difference simplification for volume skeleton trees.

- Schneider, J. et al. (2012)
   Local geometric measures for scalar-field comparison and simplification.

**VISUALISATION:**
- Sullivan, C.B., Kaszynski, A. (2019)
   "PyVista: 3D plotting and mesh analysis through a streamlined interface for VTK"

- Weber, G.H. et al. (2007)
   "Topology-Controlled Volume Rendering"
   Used as visualisation context and future target; this project currently uses
   interval-only active arcs, not full topology-controlled volume rendering.

---

**Status:** Core contour-tree pipeline, simplification, isosurface extraction,
and viewer payloads are implemented and tested. Optional rendering and benchmark
scripts are provided for dissertation figures and experiments.


