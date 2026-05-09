"""Tests for the TTK comparison fallback helpers."""

import json
import shutil

import pytest

from scripts.ttk_comparison import (
    compare_summaries,
    load_ttk_summary,
    main,
    parse_ttk_summary,
    project_summary_from_tree,
    ttk_available,
)


def test_parse_ttk_summary_csv_counts():
    text = """metric,value
critical_points,4
superarcs,3
"""

    assert parse_ttk_summary(text) == {"nodes": 4, "arcs": 3}


def test_parse_ttk_summary_text_counts():
    text = """[ttkContourForests] Number of vertices: 5
[ttkContourForests] Number of arcs: 4
"""

    assert parse_ttk_summary(text) == {"nodes": 5, "arcs": 4}


def test_load_ttk_summary_reads_saved_file(tmp_path):
    summary_path = tmp_path / "ttk_summary.txt"
    summary_path.write_text("nodes: 6\narcs: 5\n")

    assert load_ttk_summary(summary_path) == {"nodes": 6, "arcs": 5}


def test_project_summary_from_tree_counts_nodes_and_arcs():
    summary = project_summary_from_tree([0, 1, 2], [(0, 1), (1, 2)])

    assert summary == {"nodes": 3, "arcs": 2}


def test_compare_summaries_reports_deltas():
    comparison = compare_summaries(
        {"nodes": 4, "arcs": 3},
        {"nodes": 4, "arcs": 2},
    )

    assert comparison == {
        "nodes": {"project": 4, "ttk": 4, "delta": 0, "matches": True},
        "arcs": {"project": 3, "ttk": 2, "delta": 1, "matches": False},
    }


def test_main_writes_comparison_json(tmp_path):
    ttk_summary_path = tmp_path / "ttk.csv"
    output_path = tmp_path / "comparison.json"
    ttk_summary_path.write_text("metric,value\nnodes,4\narcs,3\n")

    result = main(
        [
            "--project-nodes",
            "4",
            "--project-arcs",
            "3",
            "--ttk-summary",
            str(ttk_summary_path),
            "--output",
            str(output_path),
        ]
    )

    assert result["matches"] is True
    assert json.loads(output_path.read_text()) == result


def test_live_ttk_check_skips_when_ttk_is_absent():
    if shutil.which("ttkContourForests") is None:
        pytest.skip("TTK is not installed in this environment")

    assert ttk_available("ttkContourForests") is True