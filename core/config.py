import yaml
import os

# Construct the path to settings.yaml relative to this file's location
# This makes the path independent of the current working directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_path = os.path.join(project_root, "configs", "settings.yaml")

with open(settings_path, "r") as f:
    settings = yaml.safe_load(f)