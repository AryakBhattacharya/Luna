import json
import os


class StateManager:
    """
    Handles loading and saving persistent personality state.
    """

    @staticmethod
    def _get_state_path():
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "core", "state", "persistent_state.json")

    @classmethod
    def load_state(cls):
        path = cls._get_state_path()

        if not os.path.exists(path):
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save_state(cls, state: dict):
        path = cls._get_state_path()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)