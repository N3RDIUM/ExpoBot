# imports
import os
import shutil
import playsound
from TTS.api import TTS
import playsound

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
        self.spoken = 0
        self.tts = TTS(TTS.list_models()[0])

    def speak(self, text):
        filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
        self.tts.tts_to_file(
            text=text, 
            speaker=self.tts.speakers[4],
            language=self.tts.languages[0], 
            file_path=filename,
            speaker_wav="SampleVoice.mp3",
            progress_bar=True,
            gpu=True
        )
        playsound.playsound(filename)
        os.remove(filename)
        self.spoken += 1
