"""Fallback helpers for comparing project contour-tree counts with TTK output."""

import argparse
import csv
import json
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TTK_COMPARISON_SCHEMA_VERSION = "ttk-comparison-v1"


def _normalise_metric(raw_key):
    key = re.sub(r"\[[^\]]+\]", " ", str(raw_key)).lower()
    key = key.replace("_", " ").replace("-", " ")
    key = re.sub(r"\s+", " ", key).strip()

    if "critical point" in key or "vertex" in key or "vertices" in key or "node" in key:
        return "nodes"
    if "superarc" in key or "super arc" in key or "arc" in key or "edge" in key:
        return "arcs"
    return None


def _first_int(raw_value):
    match = re.search(r"[-+]?\d+", str(raw_value))
    if match is None:
        return None
    return int(match.group(0))


def _parse_metric_value(raw_key, raw_value, counts):
    metric = _normalise_metric(raw_key)
    value = _first_int(raw_value)
    if metric is not None and value is not None:
        counts[metric] = value


def build_parser():
    """Return the command line parser for TTK comparison summaries."""
    parser = argparse.ArgumentParser(
        description="Compare project contour-tree counts with a saved TTK summary."
    )
    parser.add_argument("--project-nodes", type=int, required=True)
    parser.add_argument("--project-arcs", type=int, required=True)
    parser.add_argument("--ttk-summary", required=True)
    parser.add_argument("--output", default=None)
    return parser


def ttk_available(executable="ttkContourForests"):
    """Return whether a TTK executable is available on PATH."""
    return shutil.which(executable) is not None


def parse_ttk_summary(text):
    """Parse a saved TTK CSV/text summary into normalised counts."""
    counts = {}

    rows = csv.reader(text.splitlines())
    for row in rows:
        if len(row) >= 2:
            _parse_metric_value(row[0], row[1], counts)
            continue

        if not row:
            continue

        line = row[0]
        if ":" in line:
            raw_key, raw_value = line.rsplit(":", 1)
            _parse_metric_value(raw_key, raw_value, counts)

    missing = [metric for metric in ("nodes", "arcs") if metric not in counts]
    if missing:
        raise ValueError(f"TTK summary missing metrics: {', '.join(missing)}")

    return {"nodes": counts["nodes"], "arcs": counts["arcs"]}


def load_ttk_summary(path):
    """Load and parse a saved TTK summary file."""
    return parse_ttk_summary(Path(path).read_text())


def project_summary_from_tree(supernodes, superarcs):
    """Return project contour-tree counts in the same shape as TTK counts."""
    return {"nodes": len(list(supernodes)), "arcs": len(list(superarcs))}


def compare_summaries(project_summary, ttk_summary):
    """Return per-metric project-vs-TTK deltas."""
    comparison = {}
    for metric in ("nodes", "arcs"):
        project_value = int(project_summary[metric])
        ttk_value = int(ttk_summary[metric])
        delta = project_value - ttk_value
        comparison[metric] = {
            "project": project_value,
            "ttk": ttk_value,
            "delta": delta,
            "matches": delta == 0,
        }
    return comparison


def main(argv=None):
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    project_summary = {
        "nodes": args.project_nodes,
        "arcs": args.project_arcs,
    }
    ttk_summary = load_ttk_summary(args.ttk_summary)
    comparison = compare_summaries(project_summary, ttk_summary)
    result = {
        "schema_version": TTK_COMPARISON_SCHEMA_VERSION,
        "project": project_summary,
        "ttk": ttk_summary,
        "comparison": comparison,
        "matches": all(item["matches"] for item in comparison.values()),
    }

    if args.output is not None:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    return result


if __name__ == "__main__":
    main()