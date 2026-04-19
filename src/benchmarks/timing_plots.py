"""
Benchmark runner and plot generation for contour tree timing analysis.

Runs the full pipeline (load, join, split, merge, reduce) on each Klacansky
dataset under a vertex count threshold, records per-phase wall-clock times,
and produces matplotlib figures suitable for a dissertation.

Usage:
    python -m src.benchmarks.timing_plots
"""

import json


def collect_timings(max_verts=2_100_000, freudenthal=True):
    """Run the pipeline on every eligible dataset and return a list of
    result dicts with per-phase timings, vertex count, and supernode count."""
    raise NotImplementedError


def plot_total_time_vs_vertices(results, out_path="output/time_vs_vertices.png"):
    """Scatter plot of total computation time (join+split+merge) against
    vertex count. Log-log scale with labelled points."""
    raise NotImplementedError


def plot_phase_breakdown(results, out_path="output/phase_breakdown.png"):
    """Stacked bar chart showing join / split / merge time per dataset."""
    raise NotImplementedError


def save_results_json(results, out_path="output/timing_results.json"):
    """Dump results list to JSON for reproducibility."""
    raise NotImplementedError


if __name__ == "__main__":
    results = collect_timings()
    save_results_json(results)
    plot_total_time_vs_vertices(results)
    plot_phase_breakdown(results)
    print(f"Done -- {len(results)} datasets benchmarked.")
