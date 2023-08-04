from speaker import Speaker
from recognizer import Recognizer

s = Speaker()
s.initialize()
s.speak_gtts("Hello World! This is ExpoBot.")

r = Recognizer()
r.initialize()
print("Speak something!")
print("You said:", r.recognize_from_mic())