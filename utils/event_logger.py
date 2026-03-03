import json
import os


class EventLogger:
    """
    Appends structured interaction events
    to interaction_log.json
    """

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_path = os.path.join(base_dir, "core/state/interaction_log.json")

    def log_event(self, event: dict):

        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(self.log_path, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

            data.append(event)

            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()