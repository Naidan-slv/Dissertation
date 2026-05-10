"""
Tests for timing_plots module.

Uses fake result dicts so we don't need real datasets to test
the plotting and JSON export logic.
"""

import json
import csv
import pytest
from src.benchmarks.timing_plots import (
    collect_timings,
    plot_total_time_vs_vertices,
    plot_phase_breakdown,
    plot_tree_ratio,
    save_results_json,
    save_scalability_csv,
    scalability_csv_rows,
    SCALABILITY_CSV_FIELDS,
)


FAKE_RESULTS = [
    {
        "name": "small",
        "vertices": 1000,
        "supernodes": 12,
        "superarcs": 11,
        "t_load": 0.01,
        "t_join": 0.05,
        "t_split": 0.04,
        "t_merge": 0.03,
        "t_reduce": 0.001,
        "t_total": 0.12,
        "verified": True,
    },
    {
        "name": "medium",
        "vertices": 50000,
        "supernodes": 150,
        "superarcs": 149,
        "t_load": 0.1,
        "t_join": 1.2,
        "t_split": 1.1,
        "t_merge": 0.8,
        "t_reduce": 0.01,
        "t_total": 3.1,
        "verified": True,
    },
]


class TestSaveResultsJson:

    def test_writes_valid_json(self, tmp_path):
        out = tmp_path / "results.json"
        save_results_json(FAKE_RESULTS, str(out))
        data = json.loads(out.read_text())
        assert len(data) == 2
        assert data[0]["name"] == "small"

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "nested" / "dir" / "results.json"
        save_results_json(FAKE_RESULTS, str(out))
        assert out.exists()


class TestScalabilityCsv:

    def test_rows_include_schema_and_tree_ratio(self):
        rows = scalability_csv_rows(FAKE_RESULTS, threshold=0.5, notes="smoke")

        assert list(rows[0].keys()) == SCALABILITY_CSV_FIELDS
        assert rows[0]["dataset"] == "small"
        assert rows[0]["n_vertices"] == 1000
        assert rows[0]["n_supernodes"] == 12
        assert rows[0]["n_superarcs"] == 11
        assert rows[0]["tree_ratio"] == pytest.approx(12 / 1000)
        assert rows[0]["threshold"] == 0.5
        assert rows[0]["notes"] == "smoke"

    def test_save_scalability_csv_writes_header_and_rows(self, tmp_path):
        out = tmp_path / "scalability.csv"

        save_scalability_csv(FAKE_RESULTS, str(out), threshold=None, notes="baseline")

        with out.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert reader.fieldnames == SCALABILITY_CSV_FIELDS
        assert rows[0]["dataset"] == "small"
        assert rows[0]["threshold"] == ""
        assert rows[0]["notes"] == "baseline"


class TestPlotTotalTime:

    def test_creates_png(self, tmp_path):
        out = tmp_path / "time.png"
        plot_total_time_vs_vertices(FAKE_RESULTS, str(out))
        assert out.exists()
        assert out.stat().st_size > 1000  # not an empty file

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "sub" / "time.png"
        plot_total_time_vs_vertices(FAKE_RESULTS, str(out))
        assert out.exists()


class TestPlotPhaseBreakdown:

    def test_creates_png(self, tmp_path):
        out = tmp_path / "phases.png"
        plot_phase_breakdown(FAKE_RESULTS, str(out))
        assert out.exists()


class TestPlotTreeRatio:

    def test_creates_png(self, tmp_path):
        out = tmp_path / "tree_ratio.png"
        plot_tree_ratio(FAKE_RESULTS, str(out))
        assert out.exists()
        assert out.stat().st_size > 1000
        assert out.stat().st_size > 1000

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "sub" / "phases.png"
        plot_phase_breakdown(FAKE_RESULTS, str(out))
        assert out.exists()


class TestCollectTimings:

    def test_returns_list(self, monkeypatch):
        """Smoke test: if no datasets are eligible, returns empty list."""
        # force max_verts=0 so nothing qualifies
        result = collect_timings(max_verts=0)
        assert result == []
