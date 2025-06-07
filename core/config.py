import yaml
import os

with open("configs/settings.yaml", "r") as f:
    settings = yaml.safe_load(f)