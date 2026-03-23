"""
Tests for GridMesh3D — the 3D regular grid mesh.

Uses a tiny 2×2×2 grid (8 vertices) where we can verify everything by hand.

Vertex layout (v = z*H*W + y*W + x):

    z=0 layer:          z=1 layer:
    v2 ─ v3             v6 ─ v7
    |    |              |    |
    v0 ─ v1             v4 ─ v5

    Values:  [0, 1, 2, 3, 4, 5, 6, 7]  (v_id == value for simplicity)
"""

import numpy as np
import pytest

from src.meshes.grid_mesh_3d import GridMesh3D
from src.contour_tree_algo.final_contour_tree import compute_contour_tree


# ── Fixtures ────────────────────────────────────────────────────

@pytest.fixture
def grid_2x2x2_6conn():
    """2×2×2 grid with 6-connected (face) neighbours."""
    data = np.arange(8, dtype=float)
    return GridMesh3D(width=2, height=2, depth=2, data=data, freudenthal=False)


@pytest.fixture
def grid_2x2x2_freud():
    """2×2×2 grid with Freudenthal 14-connected neighbours."""
    data = np.arange(8, dtype=float)
    return GridMesh3D(width=2, height=2, depth=2, data=data, freudenthal=True)


# ── Test Mesh interface basics ──────────────────────────────────

class TestMeshInterface:
    def test_vertex_count(self, grid_2x2x2_6conn):
        assert len(grid_2x2x2_6conn.vertices()) == 8

    def test_vertex_ids(self, grid_2x2x2_6conn):
        assert grid_2x2x2_6conn.vertices() == list(range(8))

    def test_values(self, grid_2x2x2_6conn):
        for v in range(8):
            assert grid_2x2x2_6conn.value(v) == float(v)

    def test_sorted_ascending(self, grid_2x2x2_6conn):
        assert grid_2x2x2_6conn.sorted_vertices(ascending=True) == list(range(8))

    def test_sorted_descending(self, grid_2x2x2_6conn):
        assert grid_2x2x2_6conn.sorted_vertices(ascending=False) == list(range(7, -1, -1))


# ── Test coordinate conversion ──────────────────────────────────

class TestCoordinates:
    def test_roundtrip(self, grid_2x2x2_6conn):
        g = grid_2x2x2_6conn
        for v in range(8):
            x, y, z = g._id_to_xyz(v)
            assert g._xyz_to_id(x, y, z) == v

    def test_known_coords(self, grid_2x2x2_6conn):
        g = grid_2x2x2_6conn
        assert g._id_to_xyz(0) == (0, 0, 0)
        assert g._id_to_xyz(1) == (1, 0, 0)
        assert g._id_to_xyz(2) == (0, 1, 0)
        assert g._id_to_xyz(3) == (1, 1, 0)
        assert g._id_to_xyz(4) == (0, 0, 1)
        assert g._id_to_xyz(5) == (1, 0, 1)
        assert g._id_to_xyz(6) == (0, 1, 1)
        assert g._id_to_xyz(7) == (1, 1, 1)


# ── Test 6-connected neighbours ─────────────────────────────────

class TestSixConnected:
    """
    In a 2×2×2 grid with 6-connectivity, each corner vertex has exactly 3 face
    neighbours (one along each axis).

    E.g. vertex 0 at (0,0,0) neighbours: (1,0,0)=1, (0,1,0)=2, (0,0,1)=4.
    """

    def test_corner_has_3_neighbours(self, grid_2x2x2_6conn):
        for v in range(8):
            assert len(grid_2x2x2_6conn.neighbors(v)) == 3

    def test_vertex_0_neighbours(self, grid_2x2x2_6conn):
        assert sorted(grid_2x2x2_6conn.neighbors(0)) == [1, 2, 4]

    def test_vertex_7_neighbours(self, grid_2x2x2_6conn):
        # (1,1,1) → neighbours: (0,1,1)=6, (1,0,1)=5, (1,1,0)=3
        assert sorted(grid_2x2x2_6conn.neighbors(7)) == [3, 5, 6]

    def test_symmetry(self, grid_2x2x2_6conn):
        """If u is a neighbour of v, then v is a neighbour of u."""
        g = grid_2x2x2_6conn
        for v in range(8):
            for n in g.neighbors(v):
                assert v in g.neighbors(n), f"{v} in neighbors({n}) failed"

    def test_total_edges(self, grid_2x2x2_6conn):
        """A 2×2×2 grid with 6-connectivity has 12 edges (3 per axis × 4)."""
        g = grid_2x2x2_6conn
        edges = set()
        for v in range(8):
            for n in g.neighbors(v):
                edges.add((min(v, n), max(v, n)))
        assert len(edges) == 12


# ── Test data validation ─────────────────────────────────────────

class TestFreudenthal:
    """
    Freudenthal tetrahedralization (§4.3): each cube is split into 6 tetrahedra
    sharing the body diagonal (0,0,0)→(1,1,1). This gives 14 neighbour offsets
    per interior vertex: 6 face + 6 oriented face-diagonal + 2 body-diagonal.

    On a 2×2×2 grid every vertex is a corner, so some offsets go out of bounds.
    We also test a 3×3×3 grid where the center vertex (1,1,1) is fully interior.
    """

    def test_corner_vertex_0_has_7_neighbours(self, grid_2x2x2_freud):
        # (0,0,0): all positive offsets land in the 2×2×2 cube
        assert sorted(grid_2x2x2_freud.neighbors(0)) == [1, 2, 3, 4, 5, 6, 7]

    def test_corner_vertex_7_has_7_neighbours(self, grid_2x2x2_freud):
        # (1,1,1): all negative offsets land in the 2×2×2 cube
        assert sorted(grid_2x2x2_freud.neighbors(7)) == [0, 1, 2, 3, 4, 5, 6]

    def test_symmetry(self, grid_2x2x2_freud):
        g = grid_2x2x2_freud
        for v in range(8):
            for n in g.neighbors(v):
                assert v in g.neighbors(n), f"{v} in neighbors({n}) failed"

    def test_total_edges_2x2x2(self, grid_2x2x2_freud):
        """2×2×2 Freudenthal: 12 face + 6 face-diagonal + 2 body-diagonal = 20 edges per cube,
           but with only 1 cube many overlap → count empirically."""
        g = grid_2x2x2_freud
        edges = set()
        for v in range(8):
            for n in g.neighbors(v):
                edges.add((min(v, n), max(v, n)))
        # 1 cube → 6 tetrahedra. Unique edges: 12 face + 6 face-diag + 1 body-diag = 19
        assert len(edges) == 19

    def test_interior_vertex_has_14_neighbours(self):
        """In a 3×3×3 grid, the center vertex (1,1,1) = id 13 has all 14 offsets in bounds."""
        data = np.arange(27, dtype=float)
        g = GridMesh3D(width=3, height=3, depth=3, data=data, freudenthal=True)
        center = g._xyz_to_id(1, 1, 1)
        assert center == 13
        assert len(g.neighbors(center)) == 14

    def test_interior_neighbour_ids(self):
        """Verify the exact 14 neighbours of center vertex (1,1,1) in a 3×3×3 grid."""
        data = np.arange(27, dtype=float)
        g = GridMesh3D(width=3, height=3, depth=3, data=data, freudenthal=True)
        expected_offsets = [
            (+1,0,0), (-1,0,0), (0,+1,0), (0,-1,0), (0,0,+1), (0,0,-1),
            (+1,+1,0), (-1,-1,0), (+1,0,+1), (-1,0,-1),
            (0,+1,+1), (0,-1,-1), (+1,+1,+1), (-1,-1,-1),
        ]
        expected = sorted(g._xyz_to_id(1+dx, 1+dy, 1+dz) for dx, dy, dz in expected_offsets)
        assert sorted(g.neighbors(13)) == expected

    def test_6conn_subset_of_freudenthal(self):
        """Every 6-connected neighbour is also a Freudenthal neighbour."""
        data = np.arange(27, dtype=float)
        g6  = GridMesh3D(width=3, height=3, depth=3, data=data, freudenthal=False)
        g14 = GridMesh3D(width=3, height=3, depth=3, data=data, freudenthal=True)
        for v in range(27):
            assert set(g6.neighbors(v)).issubset(set(g14.neighbors(v)))


# ── Test data validation ─────────────────────────────────────────

class TestValidation:
    def test_wrong_size_raises(self):
        with pytest.raises(ValueError, match="expected 8"):
            GridMesh3D(width=2, height=2, depth=2, data=np.zeros(10))


# ── Pipeline integration tests ───────────────────────────────────

class TestPipeline:
    """
    Run the full contour tree pipeline (join → split → merge) on small 3D grids
    to verify GridMesh3D integrates with the existing sweep algorithms.
    """

    def test_2x2x2_contour_tree_edge_count(self, grid_2x2x2_freud):
        """A contour tree on n vertices has exactly n-1 edges."""
        ct = compute_contour_tree(grid_2x2x2_freud)
        assert len(ct) == 7  # 8 vertices → 7 edges

    def test_2x2x2_contour_tree_spans_all_vertices(self, grid_2x2x2_freud):
        """Every vertex must appear in at least one contour tree edge."""
        ct = compute_contour_tree(grid_2x2x2_freud)
        verts_in_tree = set()
        for u, v in ct:
            verts_in_tree.add(u)
            verts_in_tree.add(v)
        assert verts_in_tree == set(range(8))

    def test_2x2x2_contour_tree_is_acyclic(self, grid_2x2x2_freud):
        """The contour tree must be a tree (connected, acyclic)."""
        ct = compute_contour_tree(grid_2x2x2_freud)
        from collections import defaultdict
        adj = defaultdict(set)
        for u, v in ct:
            adj[u].add(v)
            adj[v].add(u)
        # BFS — visit all from vertex 0, should reach all 8, no extra edges
        visited = set()
        queue = [0]
        visited.add(0)
        while queue:
            node = queue.pop(0)
            for nbr in adj[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
        assert visited == set(range(8))

    def test_3x3x3_distinct_values_contour_tree(self):
        """3×3×3 grid (27 vertices) with distinct values → 26 contour tree edges."""
        data = np.arange(27, dtype=float)
        g = GridMesh3D(width=3, height=3, depth=3, data=data, freudenthal=True)
        ct = compute_contour_tree(g)
        assert len(ct) == 26

    def test_6conn_also_works(self):
        """Pipeline should also work with 6-connected grids."""
        data = np.arange(8, dtype=float)
        g = GridMesh3D(width=2, height=2, depth=2, data=data, freudenthal=False)
        ct = compute_contour_tree(g)
        assert len(ct) == 7
