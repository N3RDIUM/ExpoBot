import requests
from recognizer import Recognizer
from speaker import Speaker
from time import sleep
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from googletrans import Translator

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
    got_feedback = False
    try_count = 0
    while not got_feedback and try_count < 3:
        feedback = recognizer.recognize_from_mic()
        feedback = toEnglish(feedback)
        elaboration = ""
        if not feedback and not feedback == "":
            # Get the sentiment of the feedback using NLTK
            sentiment = analyzer.polarity_scores(feedback)
            # Sort the sentiment by the most likely emotion
            sentiment = sorted(sentiment.items(), key=lambda x: x[1], reverse=True)
            # Get the most likely emotion
            emotion = sentiment[0][0]
            # Get the score of the most likely emotion
            score = sentiment[0][1]
            if emotion == "pos":
                speaker.speak_offline("Thank you for your feedback. It encourages us to do better.")
                got_feedback = True
            elif emotion in ["neg", "neu", "compound"]:
                speaker.speak_offline("Thank you for your valuable feedback. Would you like to elaborate?")
                elaborate = recognizer.recognize_from_mic()
                elaborate = toEnglish(elaborate)
                sentiment = analyzer.polarity_scores(elaborate)
                sentiment = sorted(sentiment.items(), key=lambda x: x[1], reverse=True)
                emotion = sentiment[0][0]
                score = sentiment[0][1]
                if score > 0.2:
                    if emotion == "pos":
                        speaker.speak_offline("Please tell us more about your experience.")
                        rec = recognizer.recognize_from_mic()
                        elaboration += toEnglish(rec)
                        speaker.speak_offline("Thank you for your feedback.")
                        got_feedback = True
                    elif emotion == "neg":
                        speaker.speak_offline("Thank you for your feedback.")
                        got_feedback = True
                    else:
                        speaker.speak_offline("Thank you for your feedback.")
                got_feedback = True
        else:
            speaker.speak_offline("Sorry, I couldn't hear you. Could you please repeat?")
            try_count += 1
    saveFeedback(feedback + " | " + elaboration, name)
    requests.get("http://localhost:5000/feedback-given/" + name)

def saveFeedback(feedback, name):
    csvpath = "feedbacks.csv"
    with open(csvpath, "a") as f:
        f.write(name + "," + feedback + "\n")

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