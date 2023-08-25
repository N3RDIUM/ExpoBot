# TODO: This voice sounds good, so I'm planning to integrate it into the project
from elevenlabs import generate, play, set_api_key
from elevenlabs.api import Voices
# Print all available voices
set_api_key()
voices = Voices.from_api()
for voice in voices:
    print(voice.name)
voice = voices[1]
def speak(text):
    audio = generate(text=text, voice=voice)
    play(audio)
speak("Eleven Labs is a good api for text to speech. I'm planning to use it in my next project!")