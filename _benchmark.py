"""Benchmark: per-phase timing + correctness verification on Klacansky datasets (< 2.1M vertices)."""
import time, sys
from src.input.ingest import load_config
from src.input.loaders.raw_loader import load_raw_dataset
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.verify import verify_all

MAX_VERTS = 2_100_000

cfg = load_config()
all_datasets = []
for name, meta in cfg["datasets"].items():
    w, h, d = meta["shape_whd"]
    n = w * h * d
    if n < MAX_VERTS:
        all_datasets.append((n, name, w, h, d))
all_datasets.sort()

print(f"Datasets under {MAX_VERTS:,} vertices: {len(all_datasets)}")
print()
fmt = "{:25s} {:>12s} {:>7s} {:>7s} {:>7s} {:>7s} {:>7s} {:>10s}"
print(fmt.format("Dataset", "Verts", "Load", "Join", "Split", "Merge", "Total", "Verified"))
print("-" * 100)

for _, name, w, h, d in all_datasets:
    t0 = time.time()
    mesh = load_raw_dataset(name, freudenthal=True)
    t_load = time.time() - t0
    n = len(mesh.vertices())

    t0 = time.time()
    join_edges = compute_join_tree(mesh)
    t_join = time.time() - t0

    t0 = time.time()
    split_edges = compute_split_tree(mesh)
    t_split = time.time() - t0

    t0 = time.time()
    ct = merge_trees(join_edges, split_edges, mesh.value)
    t_merge = time.time() - t0

    t_total = t_join + t_split + t_merge

    # Run all verification checks
    errors, info = verify_all(mesh, join_edges, split_edges, ct)
    status = "PASS" if not errors else "FAIL"

    print("{:25s} {:>12,} {:>6.2f}s {:>6.2f}s {:>6.2f}s {:>6.2f}s {:>6.2f}s  {}".format(
        name, n, t_load, t_join, t_split, t_merge, t_total, status))
    if errors:
        for e in errors:
            print("    ERROR: " + e)
    sys.stdout.flush()
