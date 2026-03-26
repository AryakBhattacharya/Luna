import asyncio
import edge_tts
import threading
import uuid
import os

from playsound import playsound

class TextToSpeech:

    def __init__(self):
        self.voice = "en-US-JennyNeural"
        self.current_process = None

    def speak(self, text):

        def run():
            filename = f"temp_{uuid.uuid4().hex}.mp3"

            async def generate():
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(filename)

            asyncio.run(generate())

            playsound(filename)

            os.remove(filename)

        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        os.system("taskkill /im wmplayer.exe /f >nul 2>&1")