import yaml

with open("datasets.yaml", "r") as f:
    config = yaml.safe_load(f)

print(config)