import yaml
import numpy as np
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent

# Path to datasets.yaml
YAML_PATH = THIS_DIR / "datasets.yaml"

with open(YAML_PATH, "r") as f:
    cfg = yaml.safe_load(f)

meta = cfg["datasets"]["aneurism"]

print(meta)

w, h, d = meta["shape_whd"]
print("Shape (w,h,d):", w, h, d)

PROJECT_ROOT = THIS_DIR.parent.parent

# Construct absolute path to raw file
raw_path = PROJECT_ROOT / meta["path"]

print("Resolved path:", raw_path)

data = np.fromfile(raw_path, dtype=meta["dtype"])

vol = data.reshape((d, h, w), order="C")

print("Min:", vol.min(), "Max:", vol.max())