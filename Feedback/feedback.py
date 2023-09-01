import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import requests
from recognizer import Recognizer
from speaker import Speaker
from googletrans import Translator
from time import sleep

speaker = Speaker()
speaker.initialize()
speaker.speak_gtts("Hello World. Welcome to Anveshan!")

recognizer = Recognizer()
recognizer.initialize()

def askForFeedback(name):
    speaker.speak_gtts("Hello, Please give your valuable feedback")
    recognizer.record_and_save("feedback_recordings/" + name + ".wav")
    requests.get("http://localhost:5000/feedback-given/" + name)
    speaker.speak_gtts("Thank you for your feedback!")

while True:
    sleep(1/12)
    try:
        faces = requests.get("http://localhost:5000/faces").json()
        for face in faces:
            if len(faces[face]["seen"]) >= 2:
                print("Asking for feedback from " + face)
                askForFeedback(face)
        specialgreet = requests.get("http://localhost:5000/sgget").json()
        for greet in specialgreet["data"]:
            if "Principal" in greet:
                speaker.speak_gtts("Good Morning principal mam. Welcome to Anveshan 2023. We are greatful for your presence, mam.")
            if "AbhasSir" in greet:
                speaker.speak_gtts("Good Morning Abhas sir. Welcome to Anveshan 2023. We are greatful for your presence, sir.")
            if "PritiMaam" in greet:
                speaker.speak_gtts("Good Morning Priti mam. Welcome to Anveshan 2023. We are greatful for your presence, mam.")
            if "ShreyasSir" in greet:
                speaker.speak_gtts("Good Morning Shreyas sir. Welcome to Anveshan 2023. We are greatful for your presence, sir.")
            if "MthSir" in greet:
                speaker.speak_gtts("Good Morning Mth sir. Welcome to Anveshan 2023. We are greatful for your presence, sir.")
    except KeyboardInterrupt:
        break