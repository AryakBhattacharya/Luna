import json
import os


class EvolutionEngine:
    """
    Handles controlled personality drift.

    Responsibilities:
    - Adjust dominance level
    - Adjust trust level
    - Adjust directive success rate
    - Adjust resistance tracking
    - Enforce schema bounds + max delta
    """

    def __init__(self):
        self.schema = self._load_schema()

    # ==============================
    # PUBLIC METHOD
    # ==============================
    def process_event(self, event: dict, state: dict):
        """
        Update personality state based on structured interaction event.
        """

        self._update_directive_success(event, state)
        self._update_resistance(event, state)
        self._update_dominance(event, state)
        self._update_trust(event, state)

        if state.get("directive_success_rate", 0.5) > 0.65 and \
            state.get("trust_level", 0.5) > 0.6:
                state["proactivity_enabled"] = True

    # ==============================
    # UPDATE METHODS
    # ==============================

    def _update_resistance(self, event, state):
        # If user completed directive, do NOT apply resistance penalty
        if event.get("action_completed"):
            return  # do not apply resistance penalty
        
        resistance = event.get("user_resistance_level", 0.2)

        self._bounded_update(
            state,
            "recent_resistance_level",
            resistance
        )

    def _update_directive_success(self, event, state):
        if event.get("directive_given"):
            success = 1.0 if event.get("action_completed") else 0.0
            current = state.get("directive_success_rate", 0.5)
            new_value = (current * 0.8) + (success * 0.2)

            self._bounded_update(
                state,
                "directive_success_rate",
                new_value
            )

    def _update_dominance(self, event, state):
        dominance = state.get("dominance_level", 0.4)

        if event.get("directive_given") and event.get("action_completed"):
            dominance += 0.04

        if event.get("directive_given") and not event.get("action_completed"):
            dominance -= 0.01

        if event.get("misjudgment_occurred"):
            dominance -= 0.03

        if state.get("recent_resistance_level", 0.2) > 0.6:
            dominance -= 0.02

        self._bounded_update(
            state,
            "dominance_level",
            dominance
        )

    def _update_trust(self, event, state):
        trust = state.get("trust_level", 0.5)

        if event.get("insight_given") and event.get("insight_acknowledged"):
            trust += 0.03

        if event.get("misjudgment_occurred"):
            trust += 0.02  # honesty builds trust

        if event.get("directive_given") and not event.get("action_completed"):
            trust -= 0.02

        self._bounded_update(
            state,
            "trust_level",
            trust
        )

    # ==============================
    # BOUNDED UPDATE CORE
    # ==============================

    def _bounded_update(self, state, key, proposed_value):
        """
        Enforces:
        - min
        - max
        - max_delta_per_update
        """

        if key not in self.schema:
            return

        schema_entry = self.schema[key]

        if schema_entry["type"] != "float":
            state[key] = proposed_value
            return

        min_val = schema_entry["min"]
        max_val = schema_entry["max"]
        max_delta = schema_entry["max_delta_per_update"]

        current = state.get(key, schema_entry["default"])

        delta = proposed_value - current

        # Clamp delta
        if delta > max_delta:
            delta = max_delta
        elif delta < -max_delta:
            delta = -max_delta

        new_value = current + delta

        # Clamp to bounds
        new_value = max(min_val, min(max_val, new_value))

        state[key] = round(new_value, 4)

    # ==============================
    # SCHEMA LOADER
    # ==============================

    def _load_schema(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "core/schemas/personality_state_schema.json")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)