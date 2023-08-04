# imports
import os
import shutil
import playsound
from gtts import gTTS

class Speaker():
    def __init__(self):
        self.initialized = False
        self.speaking = False

    def initialize(self):
        self.SAVE_PATH = "speech_tts/"

        try:
            # check if the folder exists and delete it
            shutil.rmdir(self.SAVE_PATH)
            # create the folder again
            os.mkdir(self.SAVE_PATH)
        except:
            try:
                # first time initialization
                os.mkdir(self.SAVE_PATH)
            except:
                pass
        
        # get the pytorch model
        self.initialized = True
        self.SPOKEN = 0

    def speak_gtts(self, text):
        speech = gTTS(text)
        speech.save(self.SAVE_PATH+"_.mp3")
        playsound.playsound(self.SAVE_PATH+"_.mp3")
        os.remove(self.SAVE_PATH+"_.mp3")