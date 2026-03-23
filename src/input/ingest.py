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