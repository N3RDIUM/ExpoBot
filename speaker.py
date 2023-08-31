# imports
import os
import shutil
import playsound
import gtts
import _sha256
import json
import elevenlabs
from elevenlabs import generate, stream
from filelock import FileLock
OLD_HW = bool(json.load(open("config.json"))["OLD_HARDWARE"])
ELEVEN_API_KEY = json.load(open("config.json"))["ELEVEN_API_KEY"]
if not OLD_HW:
    from TTS.api import TTS
else:
    print("[WARN] OLD_HARDWARE is set to True, TTS will not work offline!")

import logging
logging.basicConfig(level=logging.INFO)

# Mute TTS logs
logging.getLogger('TTS').setLevel(logging.WARNING)

# init elevenlabs
elevenlabs.set_api_key(ELEVEN_API_KEY)
voices = elevenlabs.voices()
print("Available voices:")
for voice in voices:
    print(voice.name)

class Speaker():
    def __init__(self):
        self.initialized = False
        self.speaking = False
        self.old_hw = OLD_HW
        
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
        if not self.old_hw:
            logging.log(logging.INFO, "[SPEAKER] TTS Models: "+str(TTS.list_models()))
            logging.log(logging.INFO, "[SPEAKER] Loading TTS model...")
            print("Available TTS models: "+str(TTS.list_models()))
            self.tts = TTS(TTS.list_models()[model], progress_bar=True)
        else:
            self.tts = None
        logging.log(logging.INFO, "[SPEAKER] TTS model loaded!")

    def speak_offline(self, text):
        with FileLock("expobot.lock"):
            self.cache = os.listdir(self.CACHE_PATH)
            if _sha256.sha256(text.encode()).hexdigest()+".mp3" in self.cache:
                logging.log(logging.INFO, "[SPEAKER] Speaking from cache...")
                playsound.playsound(self.CACHE_PATH+_sha256.sha256(text.encode()).hexdigest()+".mp3")
                return
            filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
            if self.tts:
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav="jarvis.mp3",
                    file_path=filename
                )
            else:
                gtts.gTTS(text=text, lang="en").save(filename)
            playsound.playsound(filename)
            self.move2cache(filename, text)
            self.spoken += 1
        
    def speak_elevenlabs(self, text):
        with FileLock("expobot.lock"):
            audio_stream = generate(
                text,
                stream=True,
                voice=voices[0],
            )
            stream(audio_stream)
        
    def create_offline_cache(self, text, quiet=False):
        self.cache = os.listdir(self.CACHE_PATH)
        if not _sha256.sha256(text.encode()).hexdigest()+".mp3" in self.cache:
            filename = self.SAVE_PATH+str(self.spoken)+"_.mp3"
            if self.tts:
                self.tts.tts_to_file(
                    text=text,
                    file_path=filename,
                    emotion="Confident",
                )
            else:
                gtts.gTTS(text=text, lang="en").save(filename)
            self.move2cache(filename, text, quiet=quiet)
            self.spoken += 1
    
    def speak_gtts(self, text):
        with FileLock("expobot.lock"):
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
            
if __name__ == "__main__":
    s = Speaker()
    s.initialize()
    while True:
        s.speak_gtts(input("Enter text: "))