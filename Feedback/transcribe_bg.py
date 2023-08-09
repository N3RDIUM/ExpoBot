import speech_recognition as sr
import os
import json

def update_feedbacks(data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedbacks.json")) as f:
        current = json.load(f)
        current.update(data)
        json.dump(current, f)

r = sr.Recognizer()
langs = [
    "en-US",
    "hi-IN",
    "bn-IN",
    "gu-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "pa-IN",
    "ta-IN",
]
while True:
    # Remember, any language can be used here
    files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedback_recordings"))
    for file in files:
        data = dict(
            r.recognize_google(
                sr.AudioData(
                    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedback_recordings", file), "rb").read(),
                    sample_rate=16000,
                    sample_width=4
                )
        ))
        print(data)