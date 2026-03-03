import json

def load_model_config():
    with open("config/model_config.json", "r") as f:
        return json.load(f)