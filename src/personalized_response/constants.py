import os
import yaml
import shutil
from pathlib import Path

ROOT_DIR = os.path.dirname(Path(__file__).parent.parent)


def load_config(file_path):
    with open(file_path, 'r') as file: return yaml.safe_load(file)


general_config = load_config(os.path.join(ROOT_DIR, "configs", "personalized_response_config.yaml"))

for key, value in general_config.items():
    globals()[f"{key.upper()}"] = value
