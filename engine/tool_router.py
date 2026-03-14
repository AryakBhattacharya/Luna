import os
import re
import subprocess


class ToolRouter:
    """
    Routes tool calls to actual implementations.
    """

    def __init__(self, app_index):
        self.app_index = app_index

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

            app_name = open_match.group(2).strip().lower()

            # 1️⃣ App index lookup
            for name, path in self.app_index.items():

                if app_name in name:

                    os.startfile(path)
                    return ("open_app", name)


            # 2️⃣ System executable fallback
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


            # 3️⃣ Windows URI fallback
            windows_uri = {
                "settings": "ms-settings:",
                "camera": "microsoft.windows.camera:",
                "clock": "ms-clock:",
            }

            if app_name in windows_uri:
                os.system(f'start {windows_uri[app_name]}')
                return ("open_app", app_name)


            return ("app_not_found", app_name)