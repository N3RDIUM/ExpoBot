import socket
import threading
import json

class Server:
    def __init__(self):
        self.initialized = False  
        self.connected = False      
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
        self.data = {
            "amplitude": 0,
            "speaking": "no-one", # no-one, user, or bot
            "speaking-text": "", # the text that is being spoken
            "user-text": "" # the text that the user said
        }
        
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("localhost", 3030))
        self.initialized = True
        self.socket.listen(1)
        self.client, self.address = self.socket.accept()
        self.connected = True
        while True:
            data = self.client.recv(1024)
            if not data:
                continue
            data = json.loads(data.decode("utf-8"))
            self.data["amplitude"] = data["amplitude"]
            self.data["speaking"] = data["speaking"]
            self.data["speaking-text"] = data["speaking-text"]
            self.data["user-text"] = data["user-text"]