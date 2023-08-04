print("Initializing...")
from speaker import Speaker
from recognizer import Recognizer
from chatbot import ChatBot

s = Speaker()
s.initialize()
print("Speaker initialized! Running speaker test...")
s.speak_gtts("Hello, I am ExpoBot.")

r = Recognizer()
r.initialize()
print("Recognizer initialized!")

chat = ChatBot()

print("Training ChatBot...")
chat.train([[ # TODO: Add more data, train based on stall positions
        "Hello",
        "Hi",
        "Hi there",
        "Howdy",
        "Hello",
        "Hi",
        "Hey",
        "Nice to see you",
        "Long time no see",
        "Hello"
    ],
    [
        "What is your name?",
        "My name is ExpoBot.",
    ]
])

misc_questions = [
    "How are you?",
    "How is it going?",
    "How are you doing?",
]

chat.train([[
    misc_questions[i], 
    "I'm doing great!", 
    "That's nice to hear!"
] for i in range(len(misc_questions))])

print("Training fallbacks...")
chat.train_fallbacks([
    "Sorry, I didn't get that.",
    "Can you say that again?",
    "Please speak louder.",
    "Sorry, I didn't understand.",
    "Sorry, I didn't get that.",
])

print("Done! Starting up...")
while True:
    try:
        print("Listening!")
        query = r.recognize_from_mic()
        print("You:", query)
        ans = chat.answer(query)
        print("ExpoBot:", ans)
        s.speak_gtts(ans)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        break