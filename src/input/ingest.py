"""
Dataset ingestion — central config and raw-data loading.

Reads the dataset manifest (datasets.yaml) and loads raw binary volumes
into numpy arrays.  All path resolution lives here so that loaders and
scripts share one source of truth.
"""

import yaml
import numpy as np
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
YAML_PATH = THIS_DIR / "datasets.yaml"
PROJECT_ROOT = THIS_DIR.parent.parent


def load_config():
    """Load and return the full datasets.yaml manifest."""
    with open(YAML_PATH, "r") as f:
        return yaml.safe_load(f)


def get_dataset_meta(name: str) -> dict:
    """Return the metadata dict for a named dataset."""
    cfg = load_config()
    meta = cfg["datasets"].get(name)
    if meta is None:
        available = ", ".join(sorted(cfg["datasets"].keys()))
        raise KeyError(f"Unknown dataset '{name}'. Available: {available}")
    return meta


def load_raw_volume(name: str) -> tuple:
    """
    Load a raw binary volume by dataset name.

    Returns:
        (data, w, h, d) where data is a flat numpy array and w/h/d are
        the grid dimensions from datasets.yaml.
    """
    meta = get_dataset_meta(name)
    w, h, d = meta["shape_whd"]
    raw_path = PROJECT_ROOT / meta["path"]

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_path}")

    data = np.fromfile(str(raw_path), dtype=meta["dtype"])

    expected = w * h * d
    if data.size != expected:
        raise ValueError(
            f"Size mismatch for '{name}': expected {expected}, got {data.size}"
        )

    return data, w, h, d


def load_raw_volume_single_file(
    file_path: str, shape_whd: tuple, dtype: str = "uint8"
) -> tuple:
    """
    Load a raw binary volume from a single file (not in datasets.yaml).

    Args:
        file_path: Path to .raw file (absolute or relative to project root)
        shape_whd: Tuple of (width, height, depth) dimensions
        dtype: NumPy dtype string (default "uint8")

    Returns:
        (data, w, h, d) where data is a flat numpy array and w/h/d are
        the specified dimensions.

    Example:
        data, w, h, d = load_raw_volume_single_file(
            "datasets/my_data.raw",
            shape_whd=(256, 256, 128),
            dtype="uint16"
        )
    """
    # Handle both relative and absolute paths
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")

    w, h, d = shape_whd
    data = np.fromfile(str(path), dtype=dtype)

    expected = w * h * d
    if data.size != expected:
        raise ValueError(
            f"Size mismatch: Expected {expected} voxels for shape {shape_whd}, "
            f"but got {data.size}. Check dimensions or data type."
        )

    return data, w, h, d