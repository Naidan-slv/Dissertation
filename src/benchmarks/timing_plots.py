"""
Benchmark runner and plot generation for contour tree timing analysis.

Runs the full pipeline (load, join, split, merge, reduce) on each Klacansky
dataset under a vertex count threshold, records per-phase wall-clock times,
and produces matplotlib figures suitable for a dissertation.

Usage:
    python -m src.benchmarks.timing_plots
"""

import json
import os
import time
import sys


def collect_timings(max_verts=2_100_000, freudenthal=True):
    """Run the pipeline on every eligible dataset and return a list of
    result dicts with per-phase timings, vertex count, and supernode count."""
    from src.input.ingest import load_config
    from src.input.loaders.raw_loader import load_raw_dataset
    from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
    from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
    from src.contour_tree_algo.sub_algorithms.merge import merge_trees
    from src.contour_tree_algo.reduce import reduce_contour_tree
    from src.contour_tree_algo.verify import verify_all

    cfg = load_config()
    eligible = []
    for name, meta in cfg["datasets"].items():
        w, h, d = meta["shape_whd"]
        n = w * h * d
        if n < max_verts:
            eligible.append((n, name))
    eligible.sort()

    results = []
    for _, name in eligible:
        print(f"  {name}...", end=" ", flush=True)
        try:
            t0 = time.time()
            mesh = load_raw_dataset(name, freudenthal=freudenthal)
            t_load = time.time() - t0
            n_verts = len(mesh.vertices())

            t0 = time.time()
            join_edges = compute_join_tree(mesh)
            t_join = time.time() - t0

            t0 = time.time()
            split_edges = compute_split_tree(mesh)
            t_split = time.time() - t0

            t0 = time.time()
            ct = merge_trees(join_edges, split_edges, mesh.value)
            t_merge = time.time() - t0

            t0 = time.time()
            supernodes, superarcs = reduce_contour_tree(ct)
            t_reduce = time.time() - t0

            errors, _ = verify_all(mesh, join_edges, split_edges, ct)

            t_total = t_load + t_join + t_split + t_merge + t_reduce
            results.append({
                "name": name,
                "vertices": n_verts,
                "supernodes": len(supernodes),
                "superarcs": len(superarcs),
                "t_load": round(t_load, 4),
                "t_join": round(t_join, 4),
                "t_split": round(t_split, 4),
                "t_merge": round(t_merge, 4),
                "t_reduce": round(t_reduce, 4),
                "t_total": round(t_total, 4),
                "verified": len(errors) == 0,
            })
            print(f"{n_verts:,} verts, {t_total:.2f}s")
        except Exception as e:
            print(f"FAILED: {e}")
    return results


def plot_total_time_vs_vertices(results, out_path="output/time_vs_vertices.png"):
    """Scatter plot of total computation time (join+split+merge) against
    vertex count. Log-log scale with labelled points."""
    raise NotImplementedError


def plot_phase_breakdown(results, out_path="output/phase_breakdown.png"):
    """Stacked bar chart showing join / split / merge time per dataset."""
    raise NotImplementedError


def save_results_json(results, out_path="output/timing_results.json"):
    """Dump results list to JSON for reproducibility."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    results = collect_timings()
    save_results_json(results)
    plot_total_time_vs_vertices(results)
    plot_phase_breakdown(results)
    print(f"Done -- {len(results)} datasets benchmarked.")
