"""
Benchmark runner and plot generation for contour tree timing analysis.

Runs the full pipeline (load, join, split, merge, reduce) on each Klacansky
dataset under a vertex count threshold, records per-phase wall-clock times,
and produces matplotlib figures suitable for a dissertation.

Usage:
    python -m src.benchmarks.timing_plots
"""

import json
import csv
import os
import time
import sys


SCALABILITY_CSV_FIELDS = [
    "dataset",
    "n_vertices",
    "n_supernodes",
    "n_superarcs",
    "tree_ratio",
    "t_load",
    "t_join",
    "t_split",
    "t_merge",
    "t_reduce",
    "t_total",
    "threshold",
    "notes",
]


def _ensure_parent_dir(path):
    parent = os.path.dirname(str(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def _result_value(result, *keys, default=None):
    for key in keys:
        if key in result:
            return result[key]
    return default


def _tree_ratio(n_supernodes, n_vertices):
    if n_vertices == 0:
        return 0.0
    return n_supernodes / n_vertices


def collect_timings(max_verts=2_100_000, freudenthal=True):
    """Run the pipeline on every eligible dataset and return a list of
    result dicts with per-phase timings, vertex count, and supernode count."""
    from src.input.ingest import load_config, load_raw_dataset
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
                "tree_ratio": round(_tree_ratio(len(supernodes), n_verts), 8),
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
    """Bar chart of total computation time (join+split+merge) per dataset,
    sorted by vertex count. Each bar is labelled with the vertex count."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # sort by vertex count
    results = sorted(results, key=lambda r: r["vertices"])
    names = [r["name"] for r in results]
    verts = [r["vertices"] for r in results]
    times = [r["t_join"] + r["t_split"] + r["t_merge"] for r in results]

    labels = [f"{n}\n({v:,})" for n, v in zip(names, verts)]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(results)), times, color="steelblue", edgecolor="white")

    # time label above each bar
    for bar, t in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{t:.1f}s", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(range(len(results)))
    ax.set_xticklabels(labels, fontsize=8, rotation=45, ha="right")
    ax.set_ylabel("Time (s)  [join + split + merge]")
    ax.set_title("Contour Tree Computation Time vs Dataset Size")
    ax.grid(axis="y", ls="--", alpha=0.4)
    fig.tight_layout()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Saved {out_path}")


def plot_phase_breakdown(results, out_path="output/phase_breakdown.png"):
    """Stacked bar chart showing join / split / merge time per dataset."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # sort by total compute time
    results = sorted(results, key=lambda r: r["t_join"] + r["t_split"] + r["t_merge"])

    names = [r["name"] for r in results]
    t_join  = [r["t_join"]  for r in results]
    t_split = [r["t_split"] for r in results]
    t_merge = [r["t_merge"] for r in results]

    x = np.arange(len(names))
    width = 0.6

    fig, ax = plt.subplots(figsize=(12, 6))
    b1 = ax.bar(x, t_join,  width, label="Join sweep")
    b2 = ax.bar(x, t_split, width, bottom=t_join, label="Split sweep")
    bot = [j + s for j, s in zip(t_join, t_split)]
    b3 = ax.bar(x, t_merge, width, bottom=bot, label="Merge")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel("Time (s)")
    ax.set_title("Per-Phase Timing Breakdown by Dataset")
    ax.legend()
    fig.tight_layout()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Saved {out_path}")


def scalability_csv_rows(results, threshold=None, notes=""):
    """Return benchmark rows using the dissertation scalability CSV schema."""
    rows = []
    for result in results:
        n_vertices = int(_result_value(result, "n_vertices", "n_verts", "vertices"))
        n_supernodes = int(_result_value(result, "n_supernodes", "supernodes"))
        n_superarcs = int(_result_value(result, "n_superarcs", "superarcs"))
        rows.append({
            "dataset": _result_value(result, "dataset", "name"),
            "n_vertices": n_vertices,
            "n_supernodes": n_supernodes,
            "n_superarcs": n_superarcs,
            "tree_ratio": _tree_ratio(n_supernodes, n_vertices),
            "t_load": _result_value(result, "t_load", default=0.0),
            "t_join": _result_value(result, "t_join", default=0.0),
            "t_split": _result_value(result, "t_split", default=0.0),
            "t_merge": _result_value(result, "t_merge", default=0.0),
            "t_reduce": _result_value(result, "t_reduce", default=0.0),
            "t_total": _result_value(result, "t_total", default=0.0),
            "threshold": threshold,
            "notes": notes,
        })
    return rows


def save_scalability_csv(results, out_path="output/scalability_results.csv", threshold=None, notes=""):
    """Write benchmark results as a reproducible scalability CSV."""
    rows = scalability_csv_rows(results, threshold=threshold, notes=notes)
    _ensure_parent_dir(out_path)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCALABILITY_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def plot_tree_ratio(results, out_path="output/tree_ratio.png"):
    """Bar chart of reduced-tree size as critical-points / vertices."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = sorted(results, key=lambda r: _result_value(r, "n_vertices", "n_verts", "vertices"))
    rows = scalability_csv_rows(results)
    names = [row["dataset"] for row in rows]
    ratios = [row["tree_ratio"] for row in rows]
    vertices = [row["n_vertices"] for row in rows]
    labels = [f"{name}\n({n:,})" for name, n in zip(names, vertices)]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(rows)), ratios, color="seagreen", edgecolor="white")
    for bar, ratio in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{ratio:.4f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels(labels, fontsize=8, rotation=45, ha="right")
    ax.set_ylabel("Tree ratio (critical points / vertices)")
    ax.set_title("Reduced Contour Tree Size vs Dataset Size")
    ax.grid(axis="y", ls="--", alpha=0.4)
    fig.tight_layout()

    _ensure_parent_dir(out_path)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Saved {out_path}")


def save_results_json(results, out_path="output/timing_results.json"):
    """Dump results list to JSON for reproducibility."""
    _ensure_parent_dir(out_path)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)


def plot_python_vs_cpp(py_results, cpp_json_path="output/cpp_timing_results.json",
                       out_path="output/python_vs_cpp.png"):
    """Side-by-side bar chart comparing Python and C++ computation times
    on the overlapping Klacansky datasets."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    with open(cpp_json_path) as f:
        cpp_data = json.load(f)
    cpp_by_name = {d["name"]: d["t_total"] for d in cpp_data["datasets"]}

    # find overlapping datasets, sorted by vertex count
    pairs = []
    for r in py_results:
        py_compute = r["t_join"] + r["t_split"] + r["t_merge"]
        cpp_t = cpp_by_name.get(r["name"])
        if cpp_t is not None:
            pairs.append((r["name"], r["vertices"], py_compute, cpp_t))
    pairs.sort(key=lambda p: p[1])

    names  = [p[0] for p in pairs]
    verts  = [p[1] for p in pairs]
    py_t   = [p[2] for p in pairs]
    cpp_t  = [p[3] for p in pairs]
    ratios = [p / c for p, c in zip(py_t, cpp_t)]

    x = np.arange(len(names))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(12, 6))

    bars_py  = ax1.bar(x - width/2, py_t,  width, label="Python", color="steelblue")
    bars_cpp = ax1.bar(x + width/2, cpp_t, width, label="C++ (-O3)", color="darkorange")

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{n}\n({v:,})" for n, v in zip(names, verts)],
                        rotation=45, ha="right", fontsize=7)
    ax1.set_ylabel("Computation Time (s)")
    ax1.set_title("Python vs C++ Contour Tree Computation Time")
    ax1.set_yscale("log")
    ax1.legend(loc="upper left")
    ax1.grid(True, which="both", ls="--", alpha=0.3, axis="y")

    # annotate speedup ratios
    for i, ratio in enumerate(ratios):
        y_pos = max(py_t[i], cpp_t[i])
        ax1.annotate(f"{ratio:.0f}x", (x[i], y_pos),
                     textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8, fontweight="bold")

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Saved {out_path}")


if __name__ == "__main__":
    results = collect_timings()
    save_results_json(results)
    save_scalability_csv(results)
    plot_total_time_vs_vertices(results)
    plot_phase_breakdown(results)
    plot_tree_ratio(results)
    print(f"Done -- {len(results)} datasets benchmarked.")
