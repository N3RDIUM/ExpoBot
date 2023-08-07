import requests
from recognizer import Recognizer
from speaker import Speaker
from time import sleep
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import os
nltk.download('vader_lexicon')

speaker = Speaker()
speaker.initialize()
speaker.speak_gtts("Hello, I am your feedback assistant")

recognizer = Recognizer()
recognizer.initialize()

analyzer = SentimentIntensityAnalyzer()

def askForFeedback(name):
    speaker.speak_offline("Hello, Please give your valuable feedback")
    got_feedback = False
    while not got_feedback:
        feedback = recognizer.recognize_from_mic()
        # Get the sentiment of the feedback using NLTK
        sentiment = analyzer.polarity_scores(feedback)
        # Remove the compound score
        del sentiment["compound"]
        # Sort the sentiment by the most likely emotion
        sentiment = sorted(sentiment.items(), key=lambda x: x[1], reverse=True)
        # Get the most likely emotion
        emotion = sentiment[0][0]
        # Get the score of the most likely emotion
        score = sentiment[0][1]
        # If the score is greater than 0.5, then the emotion is probably correct
        if score > 0.5:
            if emotion == "pos":
                speaker.speak_offline("Thank you for your feedback. It encourages us to do better.")
                saveFeedback(feedback, name)
                got_feedback = True
            elif emotion == "neg":
                speaker.speak_offline("Thank you for your valuable feedback. Would you like to elaborate?")
                elaborate = recognizer.recognize_from_mic()
                sentiment = analyzer.polarity_scores(elaborate)
                sentiment = sorted(sentiment.items(), key=lambda x: x[1], reverse=True)
                emotion = sentiment[0][0]
                score = sentiment[0][1]
                if score > 0.5:
                    if emotion == "pos":
                        speaker.speak_offline("Please tell us more about your experience.")
                        elaboration = recognizer.recognize_from_mic()
                        speaker.speak_offline("Thank you for your feedback.")
                        saveFeedback(feedback + elaboration, name)
                        got_feedback = True
                    elif emotion == "neg":
                        speaker.speak_offline("Thank you for your feedback.")
                        saveFeedback(feedback, name)
                        got_feedback = True
                    else:
                        speaker.speak_offline("Thank you for your feedback.")
                        saveFeedback(feedback, name)
                got_feedback = True
            else:
                speaker.speak_offline("Thank you for your feedback.")
        else:
            speaker.speak_offline("Sorry, I didn't get that. Please repeat your feedback.")
    requests.get("http://localhost:5000/feedback/" + name)

def saveFeedback(feedback, name):
    csvpath = os.path.join(os.path.dirname(__file__), "feedbacks.csv")
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