import json
import os
from datetime import datetime

from services.llm_client import generate_response
from engine.mode_detector import ModeDetector
from engine.evolution_engine import EvolutionEngine
from engine.tool_router import ToolRouter
from utils.state_manager import StateManager
from utils.event_logger import EventLogger


class ConversationManager:
    """
    Orchestrates Luna's behavior.

    Responsibilities:
    - Load personality state
    - Inject identity + behavior rules into prompt
    - Route between conversation and tool mode
    - Log structured interaction events
    - Trigger bounded personality evolution
    """

    def __init__(self):
        self.state = StateManager.load_state()

        self.mode_detector = ModeDetector()
        self.evolution_engine = EvolutionEngine()
        self.tool_router = ToolRouter()
        self.last_event = None
        self.last_response = None
        self.event_logger = EventLogger()

    # ==============================
    # PUBLIC ENTRY POINT
    # ==============================
    def handle_user_input(self, user_input: str):

        mode = self.mode_detector.detect(user_input)

        if mode == "tool":
            response_text, event = self._handle_tool_mode(user_input)
        else:
            response_text, event = self._handle_conversation_mode(user_input)

        # Store memory for next interaction
        self.last_event = event
        self.last_response = response_text

        return response_text

    # ==============================
    # CONVERSATION MODE
    # ==============================
    def _handle_conversation_mode(self, user_input: str):

        system_prompt = self._build_conversation_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response_text = generate_response(messages)

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=response_text,
            interaction_type="conversation"
        )

        self.event_logger.log_event(event)

        self.evolution_engine.process_event(event, self.state)
        StateManager.save_state(self.state)

        return response_text, event

    # ==============================
    # TOOL MODE
    # ==============================
    def _handle_tool_mode(self, user_input: str):

        tool_prompt = self._build_tool_prompt()

        messages = [
            {"role": "system", "content": tool_prompt},
            {"role": "user", "content": user_input}
        ]

        # Tool mode should be precise — override temperature later if needed
        tool_response_raw = generate_response(messages, temperature=0.2)

        tool_response_raw = tool_response_raw.strip()

        # Remove markdown fences if present
        if tool_response_raw.startswith("```"):
            tool_response_raw = tool_response_raw.split("```")[1].strip()
            tool_response_raw = tool_response_raw.strip()

        try:
            tool_call = json.loads(tool_response_raw)
        except json.JSONDecodeError:
            return "Tool request format invalid."

        tool_result = self.tool_router.execute(tool_call)

        # After execution, return to personality layer
        personality_prompt = self._build_conversation_prompt()

        followup_messages = [
            {"role": "system", "content": personality_prompt},
            {"role": "user", "content": f"Tool result: {tool_result}"}
        ]

        personality_response = generate_response(followup_messages)

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=personality_response,
            interaction_type="tool_execution"
        )

        self.event_logger.log_event(event)

        self.evolution_engine.process_event(event, self.state)
        StateManager.save_state(self.state)

        return personality_response, event

    # ==============================
    # PROMPT BUILDERS
    # ==============================
    def _build_conversation_prompt(self):
        core_identity = self._load_file("core/persona/core_identity.txt")
        behavioral_rules = self._load_file("core/persona/behavioral_rules.txt")

        state_context = (
            "\nCurrent Personality State:\n"
            + json.dumps(self.state, indent=2)
        )

        return f"{core_identity}\n\n{behavioral_rules}\n\n{state_context}"

    def _build_tool_prompt(self):
        """
        Strict system tool mode.
        No personality.
        Must output valid JSON only.
        """

        return (
            "You are in strict system execution mode.\n"
            "Output only valid JSON.\n"
            "No personality, no commentary, no explanation.\n"
            "Return structured tool call format.\n"
        )

    # ==============================
    # EVENT BUILDER
    # ==============================
    def _build_interaction_event(self, user_input, response_text, interaction_type):

        lower_user = user_input.lower()
        lower_response = response_text.lower()

        # -----------------------------
        # Directive Detection
        # -----------------------------
        directive_keywords = [
            "start.",
            "do it.",
            "open it.",
            "now.",
            "execute.",
            "five minutes."
        ]

        directive_given = any(k in lower_response for k in directive_keywords)

        directive_strength = "none"
        if directive_given:
            directive_strength = "soft_directive"

        # -----------------------------
        # Insight Detection
        # -----------------------------
        insight_keywords = [
            "i'm noticing",
            "it seems like",
            "you tend to",
            "you usually",
            "you hesitate"
        ]

        insight_given = any(k in lower_response for k in insight_keywords)

        # -----------------------------
        # Misjudgment Detection
        # -----------------------------
        misjudgment_keywords = [
            "i misread",
            "i got that wrong",
            "i misjudged",
            "that wasn't"
        ]

        misjudgment_occurred = any(k in lower_response for k in misjudgment_keywords)

        # -----------------------------
        # Insight Acknowledgment Detection
        # -----------------------------
        insight_acknowledged = False

        if self.last_event and self.last_event.get("insight_given"):
            acknowledgment_phrases = [
                "you're right",
                "that makes sense",
                "true",
                "yeah",
                "i guess",
                "i think so"
            ]

            insight_acknowledged = any(p in lower_user for p in acknowledgment_phrases)

        # -----------------------------
        # Action Completion Detection
        # -----------------------------
        action_completed = False

        if self.last_event and self.last_event.get("directive_given"):
            completion_phrases = [
                "done",
                "finished",
                "completed",
                "i did it",
                "it's done"
            ]

            action_completed = any(p in lower_user for p in completion_phrases)

        # -----------------------------
        # Friction Classification
        # -----------------------------
        friction_type = "none"

        if "confused" in lower_user or "not sure" in lower_user:
            friction_type = "ambiguity"

        elif "too much" in lower_user or "overwhelmed" in lower_user:
            friction_type = "overwhelm"

        elif "tired" in lower_user or "low energy" in lower_user:
            friction_type = "energy_depletion"

        elif "scared" in lower_user or "worried" in lower_user:
            friction_type = "fear_of_imperfection"

        elif "don't feel like" in lower_user:
            friction_type = "avoidance"

        # -----------------------------
        # Emotional Signal Detection
        # -----------------------------
        emotional_signal = "stable"

        if "frustrated" in lower_user:
            emotional_signal = "frustration"

        elif "doubt" in lower_user:
            emotional_signal = "mild_self_doubt"

        elif friction_type == "overwhelm":
            emotional_signal = "overwhelm"

        # -----------------------------
        # Resistance Estimation
        # -----------------------------
        user_resistance_level = 0.2

        if friction_type != "none":
            user_resistance_level = 0.6

        if "no" in lower_user and self.last_event and self.last_event.get("directive_given"):
            user_resistance_level = 0.8

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "interaction_type": interaction_type,
            "task_context": "uncategorized",
            "emotional_signal_detected": emotional_signal,
            "friction_type": friction_type,
            "directive_given": directive_given,
            "directive_strength": directive_strength,
            "action_completed": action_completed,
            "completion_latency_seconds": 0,
            "user_resistance_level": user_resistance_level,
            "insight_given": insight_given,
            "insight_acknowledged": insight_acknowledged,
            "misjudgment_occurred": misjudgment_occurred
        }

        return event

    # ==============================
    # FILE LOADER
    # ==============================
    def _load_file(self, relative_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, relative_path)

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()