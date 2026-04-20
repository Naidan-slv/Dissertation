"""
Run the complete contour tree pipeline on a dataset.

Two modes:
  1. Named dataset from datasets.yaml:
       python scripts/run_full_pipeline.py fuel
       python scripts/run_full_pipeline.py hydrogen_atom

  2. Arbitrary .raw file:
       python scripts/run_full_pipeline.py --file path/to/volume.raw --shape 64 64 64 --dtype uint8
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.input.ingest import load_raw_volume, load_raw_volume_single_file
from src.meshes.grid_mesh_3d import GridMesh3D
from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree


def load_data(args):
    """Load data from either a named dataset or a raw file."""
    if args.file:
        if not args.shape or len(args.shape) != 3:
            print("ERROR: --shape W H D is required when using --file")
            sys.exit(1)
        w, h, d = args.shape
        dtype = args.dtype or "uint8"
        data, w, h, d = load_raw_volume_single_file(args.file, (w, h, d), dtype)
        name = Path(args.file).stem
    else:
        name = args.dataset
        data, w, h, d = load_raw_volume(name)
    return name, data, w, h, d


def run_pipeline(name, data, w, h, d):
    """Run the full contour tree pipeline."""
    
    print("\n" + "="*80)
    print(f"CONTOUR TREE PIPELINE: {name.upper()}")
    print("="*80)
    
    print(f"\n[1/3] LOADING DATA...")
    print(f"  Shape: {w} x {h} x {d} = {len(data):,} voxels")
    print(f"  Memory: {data.nbytes / 1e6:.2f} MB")

    print("\n[2/3] BUILDING 3D MESH...")
    t0 = time.time()
    mesh = GridMesh3D(width=w, height=h, depth=d, data=data)
    t_mesh = time.time() - t0
    vertices = mesh.vertices()
    print(f"  Vertices: {len(vertices):,}  ({t_mesh:.3f}s)")

    print("\n[3/3] COMPUTING CONTOUR TREE...")
    print("  (Join sweep -> Split sweep -> Merge -> Reduce)")
    t0 = time.time()
    supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
    t_tree = time.time() - t0
    print(f"  Done ({t_tree:.3f}s)")

    # results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"  Dataset:         {name}")
    print(f"  Vertices:        {len(vertices):,}")
    print(f"  Critical points: {len(supernodes)}")
    print(f"  Super-arcs:      {len(superarcs)}")
    print(f"  Build mesh:      {t_mesh:.3f}s")
    print(f"  Compute tree:    {t_tree:.3f}s")

    critical_values = sorted([(v, mesh.value(v)) for v in supernodes], key=lambda x: x[1])
    print(f"\n  Critical points (by value):")
    for vid, val in critical_values[:15]:
        print(f"    vertex {vid:>8d}  f = {val}")
    if len(critical_values) > 15:
        print(f"    ... ({len(critical_values) - 15} more)")

    print(f"\n  Super-arcs:")
    for u, v in superarcs[:15]:
        print(f"    {u:>8d} (f={mesh.value(u)})  ---  {v:>8d} (f={mesh.value(v)})")
    if len(superarcs) > 15:
        print(f"    ... ({len(superarcs) - 15} more)")
    print("="*80 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute the contour tree of a volumetric dataset.",
        epilog="Examples:\n"
               "  python scripts/run_full_pipeline.py fuel\n"
               "  python scripts/run_full_pipeline.py --file my_data.raw --shape 128 128 128\n"
               "  python scripts/run_full_pipeline.py --file vol.raw --shape 256 256 64 --dtype uint16",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("dataset", nargs="?", default=None,
                        help="Dataset name from datasets.yaml (e.g. fuel, neghip)")
    parser.add_argument("--file", "-f", type=str,
                        help="Path to a .raw binary volume file")
    parser.add_argument("--shape", "-s", type=int, nargs=3, metavar=("W", "H", "D"),
                        help="Dimensions: width height depth")
    parser.add_argument("--dtype", "-d", type=str, default="uint8",
                        help="Data type: uint8 (default) or uint16")
    args = parser.parse_args()

    if not args.dataset and not args.file:
        parser.error("Provide a dataset name or --file path")
    if args.dataset and args.file:
        parser.error("Use either a dataset name or --file, not both")

    name, data, w, h, d = load_data(args)
    run_pipeline(name, data, w, h, d)
