import os
import re
import subprocess


class ToolRouter:
    """
    Routes tool calls to actual implementations.
    """

    def execute_from_text(self, user_input):

        text = user_input.lower().strip()

        # ------------------------------
        # TIMER TOOL
        # ------------------------------
        timer_match = re.search(r"(\d+)\s*(sec|second|seconds)", text)

        if "timer" in text and timer_match:

            seconds = timer_match.group(1)

            os.system(f'start ms-clock:timer')
            return ("timer", seconds)

        # ------------------------------
        # OPEN APPLICATION
        # ------------------------------

        open_match = re.search(r"(open|launch|start|run)\s+(.+)", text)

        if open_match:

            app_name = open_match.group(2).strip()

            # 1️⃣ Try Start Menu / Windows resolver
            try:
                os.startfile(app_name)
                return ("open_app", app_name)
            except:
                pass


            # 2️⃣ Try executable
            try:
                subprocess.Popen(app_name)
                return ("open_app", app_name)
            except:
                pass

            try:
                subprocess.Popen(app_name + ".exe")
                return ("open_app", app_name)
            except:
                pass


            # 3️⃣ Final fallback: Windows start command
            try:
                os.system(f'start "" "{app_name}"')
                return ("open_app", app_name)
            except:
                return ("app_not_found", app_name)