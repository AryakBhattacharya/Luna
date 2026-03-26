from engine.conversation_manager import ConversationManager
from utils.state_manager import StateManager
import json
import ctypes
import sys
import time

from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from audio.wake_word import WakeWordListener


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# Auto-elevate
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        " ".join(sys.argv),
        None,
        1
    )
    sys.exit()


def print_state_snapshot():
    state = StateManager.load_state()
    print("\n--- Personality State Snapshot ---")
    print(json.dumps(state, indent=2))
    print("----------------------------------\n")


def main():
    print("Luna CLI Initialized.")
    print("Type 'exit' to quit.")
    print("Type 'state' to view personality state.\n")

    luna = ConversationManager()

    stt = SpeechToText()
    tts = TextToSpeech()
    wake = WakeWordListener()

    while True:

        print("Listening for 'Luna'...")
        wake.listen_for_wake()

        print("Wake word detected.")

        silence_count = 0

        while True:

            time.sleep(0.5)
            user_input = stt.listen(duration=4)

            if not user_input.strip():
                silence_count += 1

                if silence_count >= 2:
                    print("Exiting voice mode.\n")
                    break

                continue

            silence_count = 0

            print(f"You: {user_input}")

            if "exit" in user_input.lower():
                print("Exiting Luna.")
                return

            if "state" in user_input.lower():
                print_state_snapshot()
                continue

            # interrupt speech
            tts.stop()

            response = luna.handle_user_input(user_input)

            if isinstance(response, list):
                for r in response:
                    print(f"Luna: {r}")
                    tts.speak(r)
            else:
                print(f"Luna: {response}")
                tts.speak(response)

if __name__ == "__main__":
    main()