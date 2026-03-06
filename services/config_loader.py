import json
from pathlib import Path


def load_model_config():
    config_path = Path("config/model_config.json")

    with open(config_path, "r") as f:
        return json.load(f)