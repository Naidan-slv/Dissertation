"""
Results Table -- Contour tree computation on Klacansky volume datasets.

Produces a table similar to Carr (2004) Table 16.2 with:
    - Dataset dimensions and vertex count
    - Number of critical points (supernodes) and superarcs after reduction
    - Per-phase timing: Join, Split, Merge, Reduce
    - Verification status

Usage:
    python results_table.py              # run all datasets under 2.1M verts
    python results_table.py --all        # run ALL datasets (slow for large ones)
    python results_table.py fuel neghip  # run specific datasets only
"""
import argparse
import time
import sys

from src.input.ingest import load_config
from src.input.loaders.raw_loader import load_raw_dataset
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.reduce import reduce_contour_tree
from src.contour_tree_algo.verify import verify_all


DEFAULT_MAX_VERTS = 2_100_000


def run_dataset(name, freudenthal=True):
    """Run the full pipeline on one dataset, return a results dict."""
    t0 = time.time()
    mesh = load_raw_dataset(name, freudenthal=freudenthal)
    t_load = time.time() - t0
    n = len(mesh.vertices())

    t0 = time.time()
    join_edges = compute_join_tree(mesh)
    t_join = time.time() - t0

    t0 = time.time()
    split_edges = compute_split_tree(mesh)
    t_split = time.time() - t0

    t0 = time.time()
    ct_edges = merge_trees(join_edges, split_edges, mesh.value)
    t_merge = time.time() - t0

    t0 = time.time()
    supernodes, superarcs = reduce_contour_tree(ct_edges)
    t_reduce = time.time() - t0

    errors, info = verify_all(mesh, join_edges, split_edges, ct_edges)

    return {
        "name": name,
        "n_verts": n,
        "n_ct_edges": len(ct_edges),
        "n_supernodes": len(supernodes),
        "n_superarcs": len(superarcs),
        "t_load": t_load,
        "t_join": t_join,
        "t_split": t_split,
        "t_merge": t_merge,
        "t_reduce": t_reduce,
        "t_total": t_join + t_split + t_merge + t_reduce,
        "verified": len(errors) == 0,
        "errors": errors,
        "info": info,
    }


def print_table(results):
    """Print a formatted results table."""
    hdr = "{:20s} {:>10s} {:>10s} {:>8s}  {:>6s} {:>6s} {:>6s} {:>6s} {:>7s}  {:>4s}"
    print(hdr.format(
        "Dataset", "Vertices", "Critical", "Arcs",
        "Join", "Split", "Merge", "Reduc", "Total", "OK?"
    ))
    print("-" * 105)

    for r in results:
        print("{:20s} {:>10,} {:>10,} {:>8,}  {:>5.2f}s {:>5.2f}s {:>5.2f}s {:>5.2f}s {:>6.2f}s  {:>4s}".format(
            r["name"],
            r["n_verts"],
            r["n_supernodes"],
            r["n_superarcs"],
            r["t_join"],
            r["t_split"],
            r["t_merge"],
            r["t_reduce"],
            r["t_total"],
            "PASS" if r["verified"] else "FAIL",
        ))
        if r["errors"]:
            for e in r["errors"]:
                print(f"    ERROR: {e}")
        sys.stdout.flush()

    print("-" * 105)
    print(f"\n{len(results)} datasets processed.")


def main():
    parser = argparse.ArgumentParser(description="Contour tree results table")
    parser.add_argument("datasets", nargs="*", help="Specific dataset names to run")
    parser.add_argument("--all", action="store_true", help="Run ALL datasets (no size limit)")
    parser.add_argument("--max-verts", type=int, default=DEFAULT_MAX_VERTS,
                        help=f"Max vertices per dataset (default: {DEFAULT_MAX_VERTS:,})")
    args = parser.parse_args()

    cfg = load_config()

    if args.datasets:
        # Run only specified datasets
        dataset_list = []
        for name in args.datasets:
            if name not in cfg["datasets"]:
                print(f"Unknown dataset: {name}", file=sys.stderr)
                sys.exit(1)
            w, h, d = cfg["datasets"][name]["shape_whd"]
            dataset_list.append((w * h * d, name))
        dataset_list.sort()
    else:
        # Run all datasets under the size limit
        max_v = None if args.all else args.max_verts
        dataset_list = []
        for name, meta in cfg["datasets"].items():
            w, h, d = meta["shape_whd"]
            n = w * h * d
            if max_v is None or n <= max_v:
                dataset_list.append((n, name))
        dataset_list.sort()

    print(f"Running {len(dataset_list)} dataset(s)...\n")

    results = []
    for _, name in dataset_list:
        result = run_dataset(name)
        results.append(result)
        # Print progress as we go
        r = result
        print(f"  {r['name']:20s}  {r['n_verts']:>10,} verts  →  "
              f"{r['n_supernodes']:>6,} critical pts, "
              f"{r['n_superarcs']:>6,} arcs  "
              f"({r['t_total']:.2f}s)  "
              f"{'PASS' if r['verified'] else 'FAIL'}")
        sys.stdout.flush()

    print("\n" + "=" * 105)
    print("RESULTS TABLE")
    print("=" * 105 + "\n")
    print_table(results)


if __name__ == "__main__":
    main()
