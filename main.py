from engine.conversation_manager import ConversationManager
from utils.state_manager import StateManager
import json
import ctypes
import sys

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

        mode = input("Press Enter for voice or type command: ")

        # TEXT MODE
        if mode.strip():
            user_input = mode

        # VOICE MODE
        else:
            print("Listening for 'Luna'...")
            wake.listen_for_wake()
            print("Wake word detected.")
            user_input = stt.listen()

        if not user_input.strip():
            continue

        print(f"You: {user_input}")

        if "exit" in user_input.lower():
            print("Exiting Luna.")
            break

        if "state" in user_input.lower():
            print_state_snapshot()
            continue

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