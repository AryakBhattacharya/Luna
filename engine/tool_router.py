import os
import re
from engine.tools.timer_tool import TimerTool


class ToolRouter:
    """
    Routes tool calls to actual implementations.
    """

    def execute_from_text(self, user_input):

        text = user_input.lower()

        match = re.search(r"(\d+)\s*(sec|second)", text)

        if "timer" in text and match:
            seconds = int(match.group(1))

            # launch Windows clock timer
            os.system("start ms-clock:")

            return seconds

        return None