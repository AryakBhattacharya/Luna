from engine.conversation_manager import ConversationManager
#from audio.stt import listen
#from audio.tts import speak

class UIController:
    def __init__(self):
        self.manager = ConversationManager()

    def process_voice(self):
        return None, None

    def process_text(self, text):
        response = self.manager.handle_user_input(text)
        #print("DEBUG:", response)
        return response

    def process_voice(self):
        text = listen()
        if not text:
            return None, None

        response = self.manager.handle_user_input(text)
        speak(response)

        return text, response