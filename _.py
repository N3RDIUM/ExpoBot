from elevenlabs import set_api_key
set_api_key("<YOUR_API_KEY>")

from elevenlabs import generate, stream, save
from elevenlabs.api import Voices

voices = Voices.from_api()
voice = voices[-1]

print("Starting to generate the voice...")
audio_stream = generate(
  text="This is a streaming voice, and I am speaking as the waves are being generated. That's why it's so fast. By the way, I'm JARVIS, and I'm a voice assistant.",
  voice=voice,
  stream=True
)

stream(audio_stream)