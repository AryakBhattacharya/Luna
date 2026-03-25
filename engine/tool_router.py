import os
import re
import subprocess

from engine.tools.system_control import SystemControl


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
        # SYSTEM CONTROL
        # ------------------------------

        # Volume
        if "volume up" in text or "increase volume" in text:
            return ("system", SystemControl.volume_up())

        if "volume down" in text or "decrease volume" in text:
            return ("system", SystemControl.volume_down())

        if "mute" in text:
            return ("system", SystemControl.volume_mute())


        # WiFi
        if "wifi" in text:
            if "on" in text:
                return ("system", SystemControl.wifi_on())
            elif "off" in text:
                return ("system", SystemControl.wifi_off())
            else:
                return ("system", SystemControl.wifi_settings())


        # Bluetooth
        if "bluetooth" in text:
            if "on" in text:
                return ("system", SystemControl.bluetooth_on())
            elif "off" in text:
                return ("system", SystemControl.bluetooth_off())
            else:
                return ("system", SystemControl.bluetooth_settings())


        # Airplane mode
        if "airplane" in text:
            if "on" in text:
                return ("system", SystemControl.airplane_on())
            elif "off" in text:
                return ("system", SystemControl.airplane_off())
            else:
                return ("system", SystemControl.airplane_mode())

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