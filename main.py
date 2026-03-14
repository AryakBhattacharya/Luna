from engine.conversation_manager import ConversationManager
from utils.state_manager import StateManager
import json


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

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Exiting Luna.")
            break

        if user_input.lower() == "state":
            print_state_snapshot()
            continue

        response = luna.handle_user_input(user_input)

        if isinstance(response, list):
            for r in response:
                print(f"Luna: {r}")
        else:
            print(f"Luna: {response}")


if __name__ == "__main__":
    main()