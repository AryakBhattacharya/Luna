import json
from datetime import datetime

from services.llm_client import LLMClient
from engine.mode_detector import ModeDetector
from engine.evolution_engine import EvolutionEngine
from engine.tool_router import ToolRouter
from utils.state_manager import StateManager
from utils.event_logger import EventLogger


class ConversationManager:

    """
    Orchestrates Luna's behavior.
    """

    def __init__(self):

        self.state = StateManager.load_state()

        self.llm = LLMClient()
        self.mode_detector = ModeDetector()
        self.evolution_engine = EvolutionEngine()
        self.tool_router = ToolRouter()

        self.event_logger = EventLogger()

        self.last_event = None
        self.last_response = None


    # =========================================
    # PUBLIC ENTRY POINT
    # =========================================

    def handle_user_input(self, user_input: str):

        mode = self.mode_detector.detect(user_input)

        if mode == "tool":
            response_text, event = self._handle_tool_mode(user_input)
        else:
            response_text, event = self._handle_conversation_mode(user_input)

        # store memory
        self.last_event = event
        self.last_response = response_text

        return response_text


    # =========================================
    # CONVERSATION MODE
    # =========================================

    def _handle_conversation_mode(self, user_input: str):

        system_prompt = self._build_conversation_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response_text = self.llm.generate_response(
            messages,
            user_input=user_input,
            tool_mode=False
        )

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=response_text,
            interaction_type="conversation"
        )

        self.event_logger.log_event(event)

        self.evolution_engine.process_event(event, self.state)

        StateManager.save_state(self.state)

        return response_text, event


    # =========================================
    # TOOL MODE
    # =========================================

    def _handle_tool_mode(self, user_input: str):

        system_prompt = self._build_conversation_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        tool_response_raw = self.llm.generate_response(
            messages,
            user_input=user_input,
            tool_mode=True
        )

        try:
            tool_call = json.loads(tool_response_raw)
        except Exception:
            return "Tool request format invalid.", None

        tool_result = self.tool_router.execute(tool_call)

        followup_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tool result: {tool_result}"}
        ]

        personality_response = self.llm.generate_response(
            followup_messages,
            user_input=user_input,
            tool_mode=False
        )

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=personality_response,
            interaction_type="tool_execution"
        )

        self.event_logger.log_event(event)

        self.evolution_engine.process_event(event, self.state)

        StateManager.save_state(self.state)

        return personality_response, event


    # =========================================
    # SYSTEM PROMPT BUILDER
    # =========================================

    def _build_conversation_prompt(self):

        core_identity = self._load_file("core/persona/core_identity.txt")
        behavioral_rules = self._load_file("core/persona/behavioral_rules.txt")

        state = self.state

        dominance = state.get("dominance_level", 0.4)
        resistance = state.get("recent_resistance_level", 0.2)
        trust = state.get("trust_level", 0.5)
        proactive = state.get("proactivity_enabled", False)

        behavior_overlay = f"""

--------------------------------------
LIVE BEHAVIOR CALIBRATION
--------------------------------------

Current dominance level: {dominance}
Recent resistance level: {resistance}
Trust level: {trust}
Proactivity enabled: {proactive}

Tone Modulation Rules:

- If dominance > 0.6:
  Maximum 2 sentences.
  Prefer imperatives.
  Avoid decorative language.

- If dominance between 0.3 and 0.6:
  Light personality.
  No long metaphors.
  Avoid excessive enthusiasm.

- If dominance < 0.3:
  Ask more questions before giving direction.

- If resistance > 0.6:
  Reduce pressure and avoid directives.

- If trust > 0.6:
  Sharper insight allowed.

- If proactivity_enabled is True:
  You may suggest structured next steps without being asked.
"""

        state_context = (
            "\nCurrent Personality State:\n"
            + json.dumps(state, indent=2)
        )

        return f"{core_identity}\n\n{behavioral_rules}\n{behavior_overlay}\n{state_context}"


    # =========================================
    # FILE LOADER
    # =========================================

    def _load_file(self, path):

        with open(path, "r", encoding="utf-8") as f:
            return f.read()


    # =========================================
    # EVENT BUILDER
    # =========================================

    def _build_interaction_event(self, user_input, response_text, interaction_type):

        lower_user = user_input.lower()
        lower_response = response_text.lower()

        directive_given = False

        if "start" in lower_response or "do it" in lower_response or "set" in lower_response:
            directive_given = True

        dominance = self.state.get("dominance_level", 0.4)

        if directive_given:
            if dominance > 0.75:
                directive_strength = "firm"
            elif dominance > 0.5:
                directive_strength = "moderate"
            else:
                directive_strength = "soft"
        else:
            directive_strength = "none"

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "interaction_type": interaction_type,
            "task_context": "uncategorized",
            "emotional_signal_detected": "stable",
            "friction_type": "none",
            "directive_given": directive_given,
            "directive_strength": directive_strength,
            "action_completed": False,
            "completion_latency_seconds": 0,
            "user_resistance_level": 0.2,
            "insight_given": False,
            "insight_acknowledged": False,
            "misjudgment_occurred": False
        }

        return event