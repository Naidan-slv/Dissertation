"""Quick verification on small datasets (under 300K vertices)."""
import time, sys
from src.input.ingest import load_config
from src.input.loaders.raw_loader import load_raw_dataset
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.verify import verify_all

cfg = load_config()
small = []
for name, meta in cfg["datasets"].items():
    w, h, d = meta["shape_whd"]
    n = w * h * d
    if n <= 300000:
        small.append((n, name))
small.sort()

print("6 checks per dataset: tree structure, edge monotonicity,")
print("join validity, split validity, leaf extrema, CT subset of J+S")
print()
hdr = "{:25s} {:>10s} {:>6s} {:>6s} {:>6s} {:>6s} {:>10s}"
print(hdr.format("Dataset", "Verts", "Join", "Split", "Merge", "Total", "Verified"))
print("-" * 80)

for _, name in small:
    mesh = load_raw_dataset(name, freudenthal=True)
    n = len(mesh.vertices())

    t0 = time.time()
    je = compute_join_tree(mesh)
    tj = time.time() - t0

    t0 = time.time()
    se = compute_split_tree(mesh)
    ts = time.time() - t0

    t0 = time.time()
    ct = merge_trees(je, se, mesh.value)
    tm = time.time() - t0

    errors, info = verify_all(mesh, je, se, ct)
    status = "PASS" if not errors else "FAIL"

    print("{:25s} {:>10,} {:>5.2f}s {:>5.2f}s {:>5.2f}s {:>5.2f}s  {}".format(
        name, n, tj, ts, tm, tj + ts + tm, status))
    if errors:
        for e in errors:
            print("    ERROR: " + e)
    if info:
        for i in info:
            print("    " + i)
    sys.stdout.flush()
