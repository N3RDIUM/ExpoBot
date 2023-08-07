import json
import threading
import pyaudio
import time

class ServerComms:
    def __init__(self, sock):
        self.socket = sock
        self.data = {
            "amplitude": 0,
            "speaking": "no-one", # no-one, user, or bot
            "speaking-text": "", # the text that is being spoken
            "user-text": "" # the text that the user said
        }
        self.start_amp_thread()
        
    def update(self, dct):
        self.data.update(dct)
        self.socket.send(str(json.dumps(self.data) + "\n").encode("utf-8"))
            
    def start_amp_thread(self):
        self.lock = threading.Lock()
        self.lock.acquire()
        self.amp_thread = threading.Thread(target=self.amp_thread_run)
        self.amp_thread.start()
    
    def amp_thread_run(self):
        time.sleep(1)
        pyaudio_instance = pyaudio.PyAudio()
        time.sleep(1)
        self.lock.release()
        stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        while True:
            self.data["amplitude"] = self.get_amplitude(stream)
            self.update(self.data)
            
    def get_amplitude(self, stream):
        # Get the loudness of the mic
        data = stream.read(1024)
        return sum([abs(x) for x in data]) / len(data)
    