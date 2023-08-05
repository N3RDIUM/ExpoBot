print("Initializing...")
from speaker import Speaker
from recognizer import Recognizer
from chatbot import ChatBot

s = Speaker()
s.initialize()
print("Speaker initialized! Running speaker test...")
s.speak("Hello. I am the see eye ess- science fair robot.")

r = Recognizer()
r.initialize()
print("Recognizer initialized!")

chat = ChatBot()

print("Training ChatBot...")
chat.train([[ # TODO: Add more data, train based on stall positions
        "Hello",
        "Hi there",
        "Howdy",
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

thanks = [
    "Thank you",
    "Thanks",
    "Thanks a lot",
    "Thank you very much",
    "Thank you so much",
]
chat.train([[
    thanks[i],
    "You're welcome!",
] for i in range(len(thanks))])

chat.train_expo_data("./project_data.json")

print("Training fallbacks...")
chat.train_fallbacks([
    "Sorry, I didn't get that.",
    "Can you say that again?",
    "Please speak louder.",
    "Sorry, I didn't understand.",
    "Sorry, I didn't get that.",
])

print("Loading conversation cache...")
chat.load_cache()

print("Done! Starting up...")
while True:
    try:
        print("Listening!")
        query = r.recognize_from_mic()
        print("You:", query)
        ans = chat.answer(query)
        print("ExpoBot:", ans)
        try:
            s.speak(ans)
        except ValueError: pass # chatbot answered with nothing
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        break
