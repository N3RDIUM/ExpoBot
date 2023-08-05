# imports
import speech_recognition as sr

class Recognizer():
    def __init__(self):
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        self.initialized = False
        self.stopped = False
        self.wake = False

    def initialize(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
        self.initialized = True
        
    def recognize_from_mic(self):
        if self.initialized:
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
                audio = self.r.listen(source)
            try:
                return self.r.recognize_google(audio, language="en-IN")
            except sr.UnknownValueError:
                return ""
        else:
            print("Please initialize the recognizer first.")