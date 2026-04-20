"""
Example: Load a volumetric dataset from a single .raw file (not in datasets.yaml).

Run with: python scripts/ingest_single_file.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.input.ingest import load_raw_volume_single_file
from src.meshes.grid_mesh_3d import GridMesh3D
import numpy as np


def main():
    """Load and process a single raw file."""
    
    # Example 1: Load a file from datasets folder
    print("="*70)
    print("EXAMPLE 1: Load single .raw file from datasets/")
    print("="*70)
    
    try:
        # Load a fuel dataset as example (128x128x128 uint8)
        file_path = "datasets/klacansky/fuel_128x128x128_uint8.raw"
        shape = (128, 128, 128)  # width, height, depth
        dtype = "uint8"
        
        print(f"\nLoading: {file_path}")
        print(f"Shape (W×H×D): {shape}")
        print(f"Data type: {dtype}")
        
        data, w, h, d = load_raw_volume_single_file(file_path, shape, dtype)
        
        print(f"\n[OK] Loaded successfully!")
        print(f"  Total voxels: {len(data):,}")
        print(f"  Min value: {data.min()}")
        print(f"  Max value: {data.max()}")
        print(f"  Mean value: {data.mean():.2f}")
        print(f"  Memory: {data.nbytes / 1e6:.2f} MB")
        
        # Now you can build mesh and compute contour tree
        print(f"\nBuilding 3D mesh from loaded data...")
        mesh = GridMesh3D(data.astype(int), w, h, d)
        print(f"[OK] Mesh created: {len(mesh.vertices())} vertices")
        
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
    except ValueError as e:
        print(f"[ERROR] Value error: {e}")


    # Example 2: If you have your own file
    print("\n" + "="*70)
    print("EXAMPLE 2: Load your own custom file")
    print("="*70)
    
    print("""
    # Replace these values with your file details:
    data, w, h, d = load_raw_volume_single_file(
        file_path="/path/to/your/volume.raw",  # Full or relative path
        shape_whd=(256, 256, 128),              # YOUR dimensions
        dtype="uint16"                          # uint8 or uint16
    )
    
    # Then build mesh:
    mesh = GridMesh3D(data.astype(int), w, h, d)
    
    # And compute contour tree:
    from src.contour_tree_algo.final_contour_tree import compute_contour_tree
    tree = compute_contour_tree(mesh, mesh.sorted_vertices())
    """)


if __name__ == "__main__":
    main()
