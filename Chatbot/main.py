import logging
logging.basicConfig(level=logging.INFO)
DEV = False
OLD_HW = False 
# for older hardware, set this to True
# TODO: Also cache fallbacks

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

logging.log(logging.INFO, "[MAIN] Importing modules...")
if not DEV:
    from speaker import Speaker
    from recognizer import Recognizer
    from servercomms import ServerComms
    import socket
from chatbot import ChatBot

logging.log(logging.INFO, "[MAIN] Initializing modules...")
if not DEV:
    s = Speaker(OLD_HW)
    s.initialize()

    logging.log(logging.INFO, "[MAIN] Speaker initialized! Running speaker test...")
    s.speak_gtts("Hello. Welcome to the CIS science fair!")
    s.speak_offline("Testing offline speech synthesis.")
    logging.log(logging.INFO, "[MAIN] Speaker test complete!")

    logging.log(logging.INFO, "[MAIN] Initializing speech recognition...")
    r = Recognizer()
    r.initialize()
    
    logging.log(logging.INFO, "[MAIN] Connecting to UI...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 3030))
    comms = ServerComms(sock)
    logging.log(logging.INFO, "[MAIN] Connected to UI!")

    logging.log(logging.INFO, "[MAIN] Initializing and Training ChatBot...")
    chat = ChatBot(speaker = s)
else:
    logging.log(logging.INFO, "[MAIN] Initializing and Training ChatBot...")
    chat = ChatBot()
    comms = None

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
chat.train_expo_data(os.path.join(os.path.dirname(os.path.abspath(__file__)), "expo_data.json"))

# logging.log(logging.INFO, "[MAIN] Training chatbot on chatterbot corpus...")
# chat.train_from_corpus(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus/"), include=[
#     "main"
# ])
# Not required, as we are going to do gpt integration

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

logging.log(logging.INFO, "[MAIN] Saving speech cache...")
chat.create_speech_cache()

logging.log(logging.INFO, f"[MAIN] Training complete! {len(chat.conversation_data)} data points, {len(chat.fallbacks)} fallback points.")
while True:
    try:
        if not DEV:
            if comms:
                comms.update({"listening": 1})
            query = r.recognize_from_mic()
            if comms:
                comms.update({"listening": 0})
        else:
            query = input("Enter query: ")
        if comms:
            comms.update({"user-text": query})
        logging.log(logging.INFO, f"[MAIN] Recognized: {query}")
        ans = chat.answer(query)
        logging.log(logging.INFO, f"[MAIN] ExpoBot Answered: \n\t{ans}")
        if not DEV:
            try:
                if comms:
                    comms.update({"speaking": "bot", "speaking-text": ans})
                logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
                s.speak_offline(ans)
                if comms:
                    comms.update({"speaking": "no-one", "speaking-text": ""})
            except ValueError: # chatbot answered with nothing
                if comms:
                    comms.update({"speaking": "no-one", "speaking-text": ""})
    except KeyboardInterrupt:
        logging.log(logging.INFO, "[MAIN] KeyboardInterrupt detected. Saving cache and exiting...")
        chat.save_cache()
        break
    except Exception as e:
        logging.log(logging.WARNING, f"[MAIN] Exception occured: {e}")
        chat.save_cache()
    finally:
        if comms:
            comms.update({"user-text": ""})
        if comms:
            comms.update({"listening": 0})
