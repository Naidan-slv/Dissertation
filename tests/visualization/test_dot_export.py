"""
Tests for dot_export — contour tree to Graphviz DOT conversion.

Uses a small hand-crafted Y-shaped tree as the main fixture:

    0 (val=0) -- 2 (val=5) -- 3 (val=10)
                 |
                 1 (val=3)

Node 2 is a saddle (degree 3), 0 and 1 are minima, 3 is the max.
"""

import pytest
from src.visualization.dot_export import classify_nodes, ct_to_dot, save_dot


Y_NODES = [0, 1, 2, 3]
Y_ARCS  = [(0, 2), (1, 2), (2, 3)]
Y_VALS  = {0: 0, 1: 3, 2: 5, 3: 10}


class TestClassifyNodes:

    def test_leaves_identified_as_extrema(self):
        result = classify_nodes(Y_NODES, Y_ARCS, Y_VALS.get)
        assert result[0] == "min"
        assert result[1] == "min"
        assert result[3] == "max"

    def test_branch_point_is_saddle(self):
        result = classify_nodes(Y_NODES, Y_ARCS, Y_VALS.get)
        assert result[2] == "saddle"

    def test_two_node_tree(self):
        """Simplest possible tree — one min, one max."""
        vals = {0: 5, 1: 10}
        result = classify_nodes([0, 1], [(0, 1)], vals.get)
        assert result[0] == "min"
        assert result[1] == "max"


class TestCtToDot:

    def test_output_is_valid_dot(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get)
        assert dot.startswith("graph")
        assert "}" in dot

    def test_all_nodes_appear(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get)
        for n in Y_NODES:
            assert str(n) in dot

    def test_edges_appear(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get)
        # should contain edge syntax for each arc
        for u, v in Y_ARCS:
            assert str(u) in dot and str(v) in dot

    def test_labels_contain_scalar_values(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get)
        assert "10" in dot  # max value should be in a label

    def test_different_colours_for_each_type(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get)
        # min, max, and saddle should each get a distinct colour
        assert "lightblue" in dot
        assert "tomato" in dot
        assert "lightgrey" in dot

    def test_active_arc_is_highlighted_for_isovalue(self):
        dot = ct_to_dot(Y_NODES, Y_ARCS, Y_VALS.get, isovalue=7)

        assert "2 -- 3 [color=gold penwidth=3];" in dot
        assert "0 -- 2;" in dot


class TestSaveDot:

    def test_writes_file(self, tmp_path):
        out = tmp_path / "test.dot"
        save_dot("graph { }", str(out))
        assert out.exists()
        assert out.read_text() == "graph { }"

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "nested" / "dir" / "tree.dot"
        save_dot("graph { }", str(out))
        assert out.exists()
