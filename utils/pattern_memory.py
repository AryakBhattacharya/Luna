import json
import os


class PatternMemory:

    FILE_PATH = "core/state/pattern_memory.json"


    @classmethod
    def load(cls):

        if not os.path.exists(cls.FILE_PATH):
            return {}

        with open(cls.FILE_PATH, "r") as f:
            return json.load(f)


    @classmethod
    def save(cls, memory):

        with open(cls.FILE_PATH, "w") as f:
            json.dump(memory, f, indent=2)