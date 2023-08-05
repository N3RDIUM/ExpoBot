import logging
logging.basicConfig(level=logging.INFO)

logging.log(logging.INFO, "[MAIN] Importing modules...")
from speaker import Speaker
from recognizer import Recognizer
from chatbot import ChatBot

logging.log(logging.INFO, "[MAIN] Initializing modules...")
s = Speaker()
s.initialize()

logging.log(logging.INFO, "[MAIN] Speaker initialized! Running speaker test...")
s.speak_gtts("Hello. Welcome to the CIS science fair!")
s.speak_offline("Testing offline speech synthesis.")
logging.log(logging.INFO, "[MAIN] Speaker test complete!")

logging.log(logging.INFO, "[MAIN] Initializing speech recognition...")
r = Recognizer()
r.initialize()

logging.log(logging.INFO, "[MAIN] Initializing and Training ChatBot...")
chat = ChatBot()

chat.train([[
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

logging.log(logging.INFO, "[MAIN] Training chatbot on exposition data...")
chat.train_expo_data("./project_data.json")

logging.log(logging.INFO, "[MAIN] Training chatbot on chatterbot corpus...")
# chat.train_from_corpus("chatterbot-corpus-data/")

logging.log(logging.INFO, "[MAIN] Training chatbot on fallbacks...")
chat.train_fallbacks([
    "Sorry, I didn't get that.",
    "Can you say that again?",
    "Please speak louder.",
    "Sorry, I didn't understand.",
    "Sorry, I didn't get that.",
])

logging.log(logging.INFO, "[MAIN] Training complete! Loading previous cache...")
chat.load_cache()

logging.log(logging.INFO, f"[MAIN] Training complete! {len(chat.conversation_data)} data points, {len(chat.fallbacks)} fallback points.")
while True:
    try:
        query = r.recognize_from_mic()
        logging.log(logging.INFO, f"[MAIN] Recognized: {query}")
        ans = chat.answer(query)
        logging.log(logging.INFO, f"[MAIN] ExpoBot Answered: {ans}")
        try:
            logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
            s.speak_offline(ans)
        except ValueError: pass # chatbot answered with nothing
    except KeyboardInterrupt:
        logging.log(logging.INFO, "[MAIN] KeyboardInterrupt detected. Saving cache and exiting...")
        chat.save_cache()
        break
