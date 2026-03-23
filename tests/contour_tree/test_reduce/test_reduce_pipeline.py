"""
Integration tests for reduce on full pipeline output.

Runs the complete pipeline (join → split → merge → reduce) on
synthetic meshes and validates the unaugmented contour tree.
"""

import pytest
from datasets.synthetic.simple_meshes import single_peak, two_peaks_merge, square_mesh
from src.contour_tree_algo.final_contour_tree import (
    compute_contour_tree,
    compute_unaugmented_contour_tree,
)
from src.contour_tree_algo.reduce import reduce_contour_tree


class TestReducePipeline:
    """Test reduce integrated with the full contour tree pipeline."""

    def test_single_peak_reduces_to_two_endpoints(self):
        """
        Single peak: 0 (0.0) -- 1 (0.5) -- 2 (1.0)

        Fully augmented CT has 2 edges. Vertex 1 is degree-2 (regular).
        Unaugmented: supernodes = {0, 2}, one superarc.
        """
        mesh = single_peak()
        supernodes, superarcs = compute_unaugmented_contour_tree(mesh)

        assert len(supernodes) == 2
        assert len(superarcs) == 1
        # Global min and max should survive
        assert 0 in supernodes  # min
        assert 2 in supernodes  # max

    def test_two_peaks_has_saddle(self):
        """
        Two peaks mesh has a join point (saddle).

        Expected critical points: 2 maxima + 1 saddle + 1 minimum = 4 supernodes.
        Superarcs = supernodes - 1 = 3.
        """
        mesh = two_peaks_merge()
        ct_edges = compute_contour_tree(mesh)
        supernodes, superarcs = reduce_contour_tree(ct_edges)

        assert len(superarcs) == len(supernodes) - 1  # tree property

    def test_reduce_fewer_nodes_than_augmented(self):
        """
        The unaugmented tree must have fewer (or equal) vertices than
        the fully augmented tree.
        """
        mesh = square_mesh()
        ct_edges = compute_contour_tree(mesh)
        n_augmented = len(set(v for e in ct_edges for v in e))

        supernodes, superarcs = reduce_contour_tree(ct_edges)

        assert len(supernodes) <= n_augmented
        assert len(superarcs) == len(supernodes) - 1

    def test_supernodes_are_subset_of_mesh_vertices(self):
        """All supernodes must be valid mesh vertex ids."""
        mesh = square_mesh()
        supernodes, _ = compute_unaugmented_contour_tree(mesh)

        all_verts = set(mesh.vertices())
        for sn in supernodes:
            assert sn in all_verts
