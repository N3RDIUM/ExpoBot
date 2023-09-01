import logging
import time
import subprocess
logging.basicConfig(level=logging.INFO)
DEV = False
# for older hardware, set this to True
# TODO: Also cache fallbacks

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import json
PORT = int(json.load(open("config.json"))["PORT"])

logging.log(logging.INFO, "[MAIN] Importing modules...")
if not DEV:
    from speaker import Speaker
    from recognizer import Recognizer
    from servercomms import ServerComms
    import socket
from chatbot import ChatBot
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# if not DEV:
#     # Start a new browser session in Firefox
#     logging.log(logging.INFO, "[MAIN] Starting browser session...")
#     driver = webdriver.Chrome()
#     wait = WebDriverWait(driver, 3)
#     presence = EC.presence_of_element_located
#     visible = EC.visibility_of_element_located
#     logging.log(logging.INFO, "[MAIN] Browser session started!")
#     logging.log(logging.INFO, "[MAIN] installing UBlock Origin from chrome web store...")
#     driver.get("https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm")
#     # Get the install button (aria-label="Add to Chrome")
#     wait.until(visible((By.CLASS_NAME, "webstore-test-button-label")))
#     # Click on the install button
#     driver.find_element(By.CLASS_NAME, "webstore-test-button-label").click()
#     time.sleep(2)
#     logging.log(logging.INFO, "[MAIN] UBlock Origin installed!")
#     driver.get("https://n3rdium.dev")
#     logging.log(logging.INFO, "[MAIN] Navigated to https://n3rdium.dev")

logging.log(logging.INFO, "[MAIN] Initializing modules...")
if not DEV:
    s = Speaker()
    s.initialize()

    logging.log(logging.INFO, "[MAIN] Speaker initialized! Running speaker test...")
    s.speak_gtts("Hello. Welcome to Anveshan, the quest within! I am ExpoBot!")
    logging.log(logging.INFO, "[MAIN] Speaker test complete!")

    logging.log(logging.INFO, "[MAIN] Initializing speech recognition...")
    r = Recognizer()
    r.initialize()
    
    logging.log(logging.INFO, "[MAIN] Connecting to UI...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", PORT))
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
chat.create_offline_cache()

BLACKLISTED_SONGS = [
    "bts",
    "2 Cool 4 Skool"
    "O!RUL8,2?"
    "Skool Luv Affair"
    "Skool Luv Affair: Special Addition"
    "No More Dream"
    "BOY IN LUV"
    "Dark & Wild"
    "Danger"
    "Wake Up"
    "The Most Beautiful Moment In Life Pt.1"
    "FOR YOU"
    "The Most Beautiful Moment In Life Pt.2"
    "I NEED U"
    "RUN"
    "The Most Beautiful Moment In Life: Young Forever"
    "Youth"
    "WINGS"
    "You Never Walk Alone"
    "Blood Sweat & Tears"
    "Love Yourself: Her"
    "MIC DROP / DNA / CRYSTAL SNOW"
    "Face Yourself"
    "Love Yourself: Tear"
    "Love Yourself: Answer"
    "FAKE LOVE/Airplane Pt.2"
    "Map of the Soul: Persona"
    "BTS World Original Soundtrack"
    "Lights/Boy With Luv"
    "Map of the Soul: 7"
    "Map of the Soul 7: The Journey"
    "Dynamite"
    "BE"
    "Film Out"
    "Butter"
    "Permission To Dance",
    "No More Dream",
    "We Are Bulletproof Pt.2",
    "N.O",
    "Boy In Luv",
    "Just One Day",
    "Danger",
    "War of Hormone",
    "I Need U",
    "Dope",
    "Run",
    "Epilogue: Young Forever",
    "Fire",
    "Save Me",
    "Blood Sweat & Tears",
    "Spring Day",
    "Not Today",
    "DNA",
    "Mic Drop",
    "Fake Love",
    "IDOL",
    "Boy With Luv",
    "Make It Right",
    "Black Swan",
    "ON",
    "Dynamite",
    "Life Goes On",
    "Butter",
    "Permission to Dance",
    "Butter (Hotter Remix)",
    "Butter (Sweeter Remix)",
    "Stay",
    "My Universe (with Coldplay)",
    "Film Out",
    "Peaches and Cream",
    "Blue & Grey",
    "Dis-ease",
    "Stay Gold",
    "Your Eyes Tell",
    "Stay",
    "Film Out",
    "Film Out",
    "Life Goes On (Dinner Party Remix)",
    "Film Out",
]
# Process the blacklisted songs
# Make all characters lowercase
BLACKLISTED_SONGS += [song.lower() for song in BLACKLISTED_SONGS]
# And without the special characters
BLACKLISTED_SONGS += [song.replace(" ", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace("!", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace(".", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace(",", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace(":", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace("/", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace("&", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace("(", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace(")", "") for song in BLACKLISTED_SONGS]
BLACKLISTED_SONGS += [song.replace("-", "") for song in BLACKLISTED_SONGS]

# Find all instances of
# def find_blacklisted_content(query):
#     # Search the entire page for any mention of the blacklisted songs
#     for song in BLACKLISTED_SONGS:
#         if song.lower() == query.lower():
#             logging.log(logging.WARNING, "[MAIN] found blacklisted content: "+song)
#             return True
#     return False

def process(response):
    global s
    # if response.startswith("play"):
    #     if not "bts" in response.lower():
    #         logging.log(logging.INFO, "[MAIN] Playing song...")
    #         if not DEV:
    #             try:
    #                 if comms:
    #                     comms.update({"speaking": "bot", "speaking-text": "Sorry, you are not authorised to play that song."})
    #                 logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
    #                 s.speak_gtts("Okay, playing "+response[5:]+".")
    #                 if comms:
    #                     comms.update({"speaking": "no-one", "speaking-text": ""})
    #             except ValueError:
    #                 if comms:
    #                     comms.update({"speaking": "no-one", "speaking-text": ""})
    #         # Close all tabs wiht youtuve.com in the URL
    #         driver.get("https://www.youtube.com/results?search_query=" + response[5:])
    #         if not find_blacklisted_content(response[5:]):
    #             # Click on the first video
    #             # play the video
    #             wait.until(visible((By.ID, "video-title")))
    #             driver.find_element(By.ID, "video-title").click()
    #             return True
    #         else:
    #             # If the video is blacklisted, don't play it
    #             logging.log(logging.WARNING, "[MAIN] Sorry, you are not authorised to play that song.")
    #             if not DEV:
    #                 try:
    #                     if comms:
    #                         comms.update({"speaking": "bot", "speaking-text": "Sorry, you are not authorised to play that song."})
    #                     logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
    #                     s.speak_gtts("You are not authorised to play BTS songs in this fair.")
    #                     if comms:
    #                         comms.update({"speaking": "no-one", "speaking-text": ""})
    #                 except ValueError:
    #                     if comms:
    #                         comms.update({"speaking": "no-one", "speaking-text": ""})
    #             # Go back to the home page
    #             driver.get("https://n3rdium.dev")
    #             return True
    #     else:
    #         logging.log(logging.WARNING, "[MAIN] Sorry, you are not authorised to play that song.")
    #         if not DEV:
    #             try:
    #                 if comms:
    #                     comms.update({"speaking": "bot", "speaking-text": "You are not authorised to play BTS songs in this fair."})
    #                 logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
    #                 s.speak_gtts("You are not authorised to play BTS songs in this fair.")
    #                 if comms:
    #                     comms.update({"speaking": "no-one", "speaking-text": ""})
    #             except ValueError:
    #                 if comms:
    #                     comms.update({"speaking": "no-one", "speaking-text": ""})
    #         # Go back to the home page
    #         driver.get("https://n3rdium.dev")
    #         return True
    # if "pause" in response:
    #     pause()
    #     return True
    # if "play" in response:
    #     play()
    #     return True
    # if "countdown" in response.lower():
    #     subprocess.Popen(["python3", "countdown.py"])
    return False

# def pause():
#     if not DEV:
#         try:
#             driver.execute_script("document.getElementsByTagName('video')[0].pause()")
#         except:
#             pass
    
# def play():
#     if not DEV:
#         try:
#             driver.execute_script("document.getElementsByTagName('video')[0].play()")
#         except:
#             pass

logging.log(logging.INFO, f"[MAIN] Training complete! {len(chat.conversation_data)} data points, {len(chat.fallbacks)} fallback points.")
while True:
    time.sleep(0.5) # Wait for the feedback process to get the lockfile too
    try:
        if not DEV:
            if comms:
                comms.update({"listening": 1})
            # pause()
            query = r.recognize_from_mic()
            # play()
            if comms:
                comms.update({"listening": 0})
        else:
            query = input("Enter query: ")
        if comms:
            comms.update({"user-text": query})
        logging.log(logging.INFO, f"[MAIN] Recognized: {query}")
        if not process(query):
            ans = chat.answer(query)
            logging.log(logging.INFO, f"[MAIN] ExpoBot Answered: \n\t{ans}")
            if not DEV:
                try:
                    if comms:
                        comms.update({"speaking": "bot", "speaking-text": ans})
                    logging.log(logging.INFO, "[MAIN] Speaking using TTS...")
                    # pause()
                    s.speak_gtts(ans)
                    # play()
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
