import queue
import sounddevice as sd
import vosk
import json


class WakeWordListener:

    def __init__(self):
        self.q = queue.Queue()
        self.model = vosk.Model(lang="en-us")

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_for_wake(self):

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self.callback
        ):
            rec = vosk.KaldiRecognizer(self.model, 16000)

            while True:
                data = self.q.get()

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")

                    if text.strip() in ["luna", "hey luna"]:
                        return