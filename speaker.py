# imports
import os
import shutil
import playsound
from TTS.api import TTS
import gtts
import playsound

class Speaker():
    def __init__(self):
        self.initialized = False
        self.speaking = False
        
    def initialize(self, model=16):
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
        
        self.spoken = 0
        self.tts = TTS(TTS.list_models()[model])

    def speak_offline(self, text):
        filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
        self.tts.tts_to_file(
            text=text,
            file_path=filename,
            gpu=True
        )
        playsound.playsound(filename)
        os.remove(filename)
        self.spoken += 1
    
    def speak_gtts(self, text):
        filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
        gtts.gTTS(text=text, lang="en").save(filename)
        playsound.playsound(filename)
        os.remove(filename)
        self.spoken += 1
