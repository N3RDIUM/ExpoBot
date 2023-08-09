import socket
import threading
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import json
PORT = int(json.load(open("config.json"))["PORT"])

class Server:
    def __init__(self):
        self.initialized = False  
        self.connected = False      
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
        self.data = {
            "listening": 0,
            "amplitude": 0,
            "speaking": "no-one", # no-one, user, or bot
            "speaking-text": "", # the text that is being spoken
            "user-text": "" # the text that the user said
        }
        
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("localhost", PORT))
        self.initialized = True
        self.socket.listen(1)
        self.client, self.address = self.socket.accept()
        self.connected = True
        while True:
            data = self.client.recv(1024)
            if not data:
                continue
            data = data.decode("utf-8").split("\n")
            for line in data:
                try:
                    line = json.loads(line)
                    self.data["amplitude"] = line["amplitude"]
                    self.data["speaking"] = line["speaking"]
                    self.data["speaking-text"] = line["speaking-text"]
                    self.data["user-text"] = line["user-text"]
                    self.data["listening"] = line["listening"]
                except: pass