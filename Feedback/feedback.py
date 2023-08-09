import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import requests
from recognizer import Recognizer
from speaker import Speaker
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from googletrans import Translator
from time import sleep

nltk.download('vader_lexicon')

speaker = Speaker()
speaker.initialize()
speaker.speak_gtts("Hello, I am your feedback assistant")

recognizer = Recognizer()
recognizer.initialize()

analyzer = SentimentIntensityAnalyzer()

def toEnglish(text):
    translator = Translator()
    return translator.translate(text, dest="en").text

def askForFeedback(name):
    speaker.speak_offline("Hello, Please give your valuable feedback")
    recognizer.record_and_save("feedback_recordings/" + name + ".wav")
    requests.get("http://localhost:5000/feedback-given/" + name)

while True:
    sleep(1/12)
    try:
        faces = requests.get("http://localhost:5000/faces").json()
        print(faces)
        for face in faces:
            if len(faces[face]["seen"]) >= 2:
                print(face + ", Please give your valuable feedback")
                askForFeedback(face)
    except KeyboardInterrupt:
        break