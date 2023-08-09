import speech_recognition as sr
import os
import json

def update_feedbacks(data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedbacks.json")) as f:
        current = json.load(f)
        current.update(data)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedbacks.json"), "w") as f:
        json.dump(current, f, indent=4)

r = sr.Recognizer()
languages = [
    "en-US",
    "hi-IN",
    "mr-IN",
    "kn-IN",
]
def transcribe_all_languages(path):
    result = {}
    for language in languages:
        with sr.AudioFile(path) as source:
            audio = r.record(source)
        try:
            result[language] = r.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            result[language] = ""
        except sr.RequestError:
            result[language] = ""
    return result

while True:
    # Remember, any language can be used here
    files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedback_recordings"))
    for file in files:
        lng = transcribe_all_languages(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedback_recordings", file))
        update_feedbacks({file.split(".")[0]: lng})
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "feedback_recordings", file))