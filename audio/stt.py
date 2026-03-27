import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import tempfile
import time

class SpeechToText:

    def __init__(self):
        self.model = whisper.load_model("small")

    def listen(self, duration=5):

        fs = 44100
        sd.stop()

        print("Listening...")

        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype='int16',
            device=7   # ADD THIS
        )
        sd.wait()
        time.sleep(0.3)

        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        write(temp_file.name, fs, recording)

        result = self.model.transcribe(temp_file.name)

        text = result["text"].strip()

        print(f"DEBUG STT: {text}")  # <-- important

        return text