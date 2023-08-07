# imports
import os
import shutil
import playsound
from TTS.api import TTS
import gtts
import playsound
import _sha256

import logging
logging.basicConfig(level=logging.INFO)

# Mute TTS logs
logging.getLogger('TTS').setLevel(logging.WARNING)

class Speaker():
    def __init__(self):
        self.initialized = False
        self.speaking = False
        
    def initialize(self, model=16):
        self.SAVE_PATH = "speech_tts/"
        self.CACHE_PATH = "tts_cache/"
        logging.log(logging.INFO, "[SPEAKER] Speaker initialize(), model="+str(model))
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
        logging.log(logging.INFO, "[SPEAKER] TTS Models: "+str(TTS.list_models()))
        logging.log(logging.INFO, "[SPEAKER] Loading TTS model...")
        self.tts = TTS(TTS.list_models()[model], progress_bar=True)
        logging.log(logging.INFO, "[SPEAKER] TTS model loaded!")

    def speak_offline(self, text):
        self.cache = os.listdir(self.CACHE_PATH)
        if _sha256.sha256(text.encode()).hexdigest()+".mp3" in self.cache:
            logging.log(logging.INFO, "[SPEAKER] Speaking from cache...")
            playsound.playsound(self.CACHE_PATH+_sha256.sha256(text.encode()).hexdigest()+".mp3")
            return
        filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
        self.tts.tts_to_file(
            text=text,
            file_path=filename,
            gpu=True
        )
        playsound.playsound(filename)
        self.move2cache(filename, text)
        self.spoken += 1
        
    def create_offline_cache(self, text, quiet=False):
        self.cache = os.listdir(self.CACHE_PATH)
        if not _sha256.sha256(text.encode()).hexdigest()+".mp3" in self.cache:
            filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
            self.tts.tts_to_file(
                text=text,
                file_path=filename,
                emotion="neutral",
            )
            self.move2cache(filename, text, quiet=quiet)
            self.spoken += 1
    
    def speak_gtts(self, text):
        filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
        gtts.gTTS(text=text, lang="en").save(filename)
        playsound.playsound(filename)
        os.remove(filename)
        self.spoken += 1
    
    def move2cache(self, filename, text, quiet=False):
        new_filename = self.SAVE_PATH+_sha256.sha256(text.encode()).hexdigest()+".mp3"
        os.rename(filename, new_filename)
        shutil.move(new_filename, self.CACHE_PATH)
        if not quiet:
            logging.log(logging.INFO, "[SPEAKER] Moved file "+filename+" to "+new_filename)