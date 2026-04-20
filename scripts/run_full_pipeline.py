"""
Run the complete contour tree pipeline on a dataset:
  Load → Mesh → Join Tree → Split Tree → Merge → Reduce → Analysis

Run with: python scripts/run_full_pipeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.input.ingest import load_raw_volume
from src.meshes.grid_mesh_3d import GridMesh3D
from src.contour_tree_algo.final_contour_tree import compute_unaugmented_contour_tree
import time


def run_pipeline(dataset_name="fuel"):
    """Run the full contour tree pipeline on a dataset."""
    
    print("\n" + "="*80)
    print(f"CONTOUR TREE PIPELINE: {dataset_name.upper()}")
    print("="*80)
    
    # =========================================================================
    # STEP 1: LOAD DATA
    # =========================================================================
    print("\n[1/5] LOADING DATA...")
    t0 = time.time()
    try:
        data, w, h, d = load_raw_volume(dataset_name)
        t_load = time.time() - t0
        print(f"  [OK] Loaded {dataset_name}")
        print(f"    Shape: {w} × {h} × {d} = {len(data):,} voxels")
        print(f"    Memory: {data.nbytes / 1e6:.2f} MB")
        print(f"    Time: {t_load:.3f}s")
    except Exception as e:
        print(f"  [FAIL] Failed to load: {e}")
        return
    
    # =========================================================================
    # STEP 2: BUILD 3D MESH
    # =========================================================================
    print("\n[2/5] BUILDING 3D MESH...")
    t0 = time.time()
    try:
        mesh = GridMesh3D(w, h, d, data.astype(int))
        t_mesh = time.time() - t0
        
        vertices = mesh.vertices()
        print(f"  [OK] Mesh created")
        print(f"    Vertices: {len(vertices):,}")
        print(f"    Time: {t_mesh:.3f}s")
    except Exception as e:
        print(f"  [FAIL] Failed to build mesh: {e}")
        return
    
    # =========================================================================
    # STEP 3: COMPUTE CONTOUR TREE
    # =========================================================================
    print("\n[3/5] COMPUTING CONTOUR TREE...")
    print("  (Join sweep → Split sweep → Merge → Reduce)")
    t0 = time.time()
    try:
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)
        t_tree = time.time() - t0
        print(f"  [OK] Contour tree computed")
        print(f"    Time: {t_tree:.3f}s")
    except Exception as e:
        print(f"  [FAIL] Failed to compute tree: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # STEP 4: EXTRACT CRITICAL POINTS & SUPER-ARCS
    # =========================================================================
    print("\n[4/5] EXTRACTING RESULTS...")
    try:
        print(f"  [OK] Results extracted")
        print(f"    Critical Points (Supernodes): {len(supernodes)}")
        print(f"    Super-Arcs (Superarcs): {len(superarcs)}")
        print(f"    Relationship: superarcs = supernodes - 1 = {len(supernodes) - 1}")
        
    except Exception as e:
        print(f"  [FAIL] Failed to extract results: {e}")
        return
    
    # =========================================================================
    # STEP 5: DETAILED ANALYSIS
    # =========================================================================
    print("\n[5/5] DETAILED ANALYSIS...")
    
    print(f"\n  CRITICAL POINTS (Supernodes):")
    print(f"     Total: {len(supernodes)}")
    try:
        critical_values = sorted([(v, mesh.value(v)) for v in supernodes], key=lambda x: x[1])
        print(f"     Values (min to max): {critical_values[0][1]} → {critical_values[-1][1]}")
        print(f"     First 5 IDs: {supernodes[:5]}")
        if supernodes:
            print(f"     First 5 with values:")
            for v in supernodes[:5]:
                print(f"       vertex {v:6d} → f(v) = {mesh.value(v)}")
    except Exception as e:
        print(f"     Error displaying values: {e}")
    
    print(f"\n  SUPER-ARCS (Connections):")
    print(f"     Total: {len(superarcs)}")
    if superarcs:
        print(f"     First 10 arcs:")
        try:
            for u, v in superarcs[:10]:
                val_u, val_v = mesh.value(u), mesh.value(v)
                print(f"       {u} (f={val_u}) ←→ {v} (f={val_v})")
        except Exception as e:
            print(f"       Error: {e}")
            print(f"       First 10: {superarcs[:10]}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    t_total = t_load + t_mesh + t_tree
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"  Dataset:              {dataset_name}")
    print(f"  Input voxels:         {len(data):,}")
    print(f"  Mesh vertices:        {len(vertices):,}")
    print(f"  Critical points:      {len(supernodes)}")
    print(f"  Super-arcs:           {len(superarcs)}")
    print(f"\n  Timing breakdown:")
    print(f"    Load data:          {t_load:.3f}s")
    print(f"    Build mesh:         {t_mesh:.3f}s")
    print(f"    Compute tree:       {t_tree:.3f}s")
    print(f"    TOTAL:              {t_total:.3f}s")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run on small dataset (fast)
    run_pipeline("fuel")
    
    # Or try other datasets:
    # run_pipeline("engine")
    # run_pipeline("hydrogen_atom")
