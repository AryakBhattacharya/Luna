import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

class WakeWordListener:

    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def listen_for_wake(self):
        print("Listening for 'Luna'...")

        fs = 16000
        duration = 2  # short chunks

        while True:
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()

            audio = np.squeeze(audio).astype(np.float32) / 32768.0

            segments, _ = self.model.transcribe(audio, beam_size=1)

            for segment in segments:
                text = segment.text.lower().strip()
                print(f"HEARD: {text}")

                if "luna" in text:
                    print("Wake word detected!")
                    return