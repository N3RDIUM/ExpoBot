import json
import threading
import pyaudio

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
        self.socket.send(json.dumps(self.data).encode("utf-8"))
            
    def start_amp_thread(self):
        self.amp_thread = threading.Thread(target=self.amp_thread_run)
        # self.amp_thread.start()
    
    def amp_thread_run(self):
        pyaudio_instance = pyaudio.PyAudio()
        stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        while True:
            self.update(amplitude=self.get_amplitude(stream))
            
    def get_amplitude(self, stream):
        return int.from_bytes(stream.read(1024), byteorder="little", signed=True)