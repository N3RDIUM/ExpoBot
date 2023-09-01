from speaker import Speaker
s = Speaker()
s.initialize()
while True:
    s.speak_gtts(input("> "))