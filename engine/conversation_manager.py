import json
import re

from datetime import datetime

from services.llm_client import LLMClient
from engine.mode_detector import ModeDetector
from engine.evolution_engine import EvolutionEngine
from engine.tool_router import ToolRouter
from utils.state_manager import StateManager
from utils.event_logger import EventLogger
from utils.pattern_memory import PatternMemory
from engine.pattern_interpreter import PatternInterpreter


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
        self.pattern_memory = PatternMemory.load()
        self.event_logger = EventLogger()
        self.history = []

        self.last_event = None
        self.last_response = None


    # =========================================
    # Pattern Memory
    # =========================================

    def _update_pattern_memory(self, event):

        memory = self.pattern_memory

        memory["conversation_count"] = memory.get("conversation_count", 0) + 1

        if event.get("friction_type") == "avoidance":
            memory["avoidance_patterns"] = memory.get("avoidance_patterns", 0) + 1

        if event.get("directive_given") and event.get("action_completed"):
            memory["directive_follow_through"] = memory.get("directive_follow_through", 0) + 1

        if event.get("insight_given") and event.get("insight_acknowledged"):
            memory["insight_acceptance"] = memory.get("insight_acceptance", 0) + 1

        PatternMemory.save(memory)
        self.pattern_memory = memory


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

        messages = [{"role": "system", "content": system_prompt}]

        messages.extend(self.history[-6:])

        messages.append({"role": "user", "content": user_input})

        response_text = self.llm.generate_response(
            messages,
            user_input=user_input,
            tool_mode=False
        )

        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response_text})

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=response_text,
            interaction_type="conversation"
        )

        self.event_logger.log_event(event)

        self.evolution_engine.process_event(event, self.state)
        self._update_pattern_memory(event)

        StateManager.save_state(self.state)

        return response_text, event


    # =========================================
    # TOOL MODE
    # =========================================

    def _handle_tool_mode(self, user_input: str):

        system_prompt = self._build_conversation_prompt()

        tool_seconds = self.tool_router.execute_from_text(user_input)

        if tool_seconds:

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"User asked for a timer of {tool_seconds} seconds. Confirm that the timer is starting."
                }
            ]

            response_text = self.llm.generate_response(
                messages,
                user_input=user_input,
                tool_mode=False
            )

        else:
            response_text = "I couldn't detect a tool request."

        event = self._build_interaction_event(
            user_input=user_input,
            response_text=response_text,
            interaction_type="tool_execution"
        )

        self.event_logger.log_event(event)
        self.evolution_engine.process_event(event, self.state)
        self._update_pattern_memory(event)

        StateManager.save_state(self.state)

        return response_text, event


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

        insights = PatternInterpreter.interpret(self.pattern_memory)

        insight_context = "\nBehavioral Insights:\n" + "\n".join(
            f"- {insight}" for insight in insights
        )

        pattern_context = f"""

--------------------------------------
KNOWN USER BEHAVIOR PATTERNS
--------------------------------------

{json.dumps(self.pattern_memory, indent=2)}

Interpretation Guidelines:
- Higher avoidance_patterns → user tends to hesitate starting tasks.
- Higher directive_follow_through → user responds well to clear direction.
- Higher insight_acceptance → user accepts behavioral observations.
- conversation_count shows familiarity level.
"""
        pattern_insights = PatternInterpreter.interpret(self.pattern_memory)
        pattern_interpretation = "\nObserved Behavioral Insights:\n"

        for insight in pattern_insights:
            pattern_interpretation += f"- {insight}\n"

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

        return f"""
{core_identity}

{behavioral_rules}

{behavior_overlay}

{state_context}

{pattern_context}

{insight_context}
"""


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

        directive_patterns = [
            r"^(start|go|try|do|take)\b",
            r"\bnow\b",
            r"\bspend \d+ minutes\b",
            r"\bfocus on\b"
        ]

        directive_given = False

        sentences = re.split(r"[.!?]\s*", lower_response.strip())

        for sentence in sentences:
            sentence = sentence.strip()
            for pattern in directive_patterns:
                if re.search(pattern, sentence):
                    directive_given = True
                    break
            if directive_given:
                break

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

        completion_phrases = [
            "done",
            "finished",
            "completed",
            "i did it",
            "it's done"
        ]

        action_completed = False

        if self.last_event and self.last_event.get("directive_given"):
            for phrase in completion_phrases:
                if phrase in lower_user:
                    action_completed = True
                    break

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "interaction_type": interaction_type,
            "task_context": "uncategorized",
            "emotional_signal_detected": "stable",
            "friction_type": "none",
            "directive_given": directive_given,
            "directive_strength": directive_strength,
            "action_completed": action_completed,
            "completion_latency_seconds": 0,
            "user_resistance_level": 0.2,
            "insight_given": False,
            "insight_acknowledged": False,
            "misjudgment_occurred": False
        }

        return event