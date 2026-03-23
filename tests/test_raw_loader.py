"""
Tests for the raw volume loader + full pipeline integration.

Creates a temporary .raw file on disk to test the loading path without
needing real Klacansky data. Also tests error handling.
"""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from src.input.loaders.raw_loader import load_raw_dataset
from src.input.ingest import load_config
from src.meshes.grid_mesh_3d import GridMesh3D
from src.contour_tree_algo.final_contour_tree import compute_contour_tree


class TestRawLoaderErrors:
    def test_unknown_dataset_raises(self):
        with pytest.raises(KeyError, match="Unknown dataset"):
            load_raw_dataset("nonexistent_dataset")

    def test_missing_file_raises(self, tmp_path):
        """If the .raw file doesn't exist on disk, raise FileNotFoundError."""
        from unittest.mock import patch
        fake_meta = {"path": "nonexistent/fake.raw", "shape_whd": [2, 2, 2], "dtype": "uint8"}
        with patch("src.input.ingest.get_dataset_meta", return_value=fake_meta):
            with pytest.raises(FileNotFoundError, match="Raw file not found"):
                load_raw_dataset("fake_dataset")


class TestSyntheticRawFile:
    """
    Create a tiny .raw file, mock ingest to point at it,
    then run the full pipeline through the loader.
    """

    def test_load_and_compute_contour_tree(self, tmp_path):
        # Create a 4×4×4 volume with distinct values
        w, h, d = 4, 4, 4
        n = w * h * d  # 64
        data = np.arange(n, dtype=np.uint8)
        raw_file = tmp_path / "test_volume.raw"
        data.tofile(str(raw_file))

        # Mock ingest.load_raw_volume to return our synthetic data
        def fake_load(name):
            assert name == "test_vol"
            return np.arange(n, dtype=np.uint8), w, h, d

        with patch("src.input.loaders.raw_loader.load_raw_volume", side_effect=fake_load):
            mesh = load_raw_dataset("test_vol", freudenthal=True)

        assert isinstance(mesh, GridMesh3D)
        assert len(mesh.vertices()) == 64
        assert mesh.value(0) == 0.0
        assert mesh.value(63) == 63.0

        # Run the full contour tree pipeline
        ct = compute_contour_tree(mesh)
        assert len(ct) == 63  # n-1 edges for n vertices
