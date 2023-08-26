# imports
import logging
logging.basicConfig(level=logging.INFO)
import speech_recognition as sr

class Recognizer():
    def __init__(self):
        logging.log(logging.INFO, "[RECOGNIZER] Recognizer __init__")
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        # self.r.pause_threshold = 2
        logging.log(logging.INFO, "[RECOGNIZER] Recognizer and microphone initialized!")
        self.initialize()
        logging.log(logging.INFO, "[RECOGNIZER] Recognizer initialized!")

    def initialize(self):
        logging.log(logging.INFO, "[RECOGNIZER] Recognizer is adjusting for ambient noise...")
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
        
    def recognize_from_mic(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
            logging.log(logging.INFO, "[RECOGNIZER] Listening...")
            audio = self.r.listen(source)
        try:
            logging.log(logging.INFO, "[RECOGNIZER] Recognizing with Google Speech Recognition...")
            return self.r.recognize_google(audio, language="en-IN")
        except sr.UnknownValueError:
            logging.log(logging.INFO, "[RECOGNIZER] Google Speech Recognition could not understand audio!")
            return self.recognize_from_mic()
    
    def record_and_save(self, filename):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
            logging.log(logging.INFO, "[RECOGNIZER] Listening...")
            audio = self.r.listen(source)
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())
        return filename