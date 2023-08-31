import random
import json
import inflect
import fuzzywuzzy.fuzz as fuzz
import spacy
import _sha256 as sha256
import tqdm
import yaml
import os

p = inflect.engine()
import logging
logging.basicConfig(level=logging.INFO)

THRESHOLD = 0.8 # Similarity threshold

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import openai
import json
if not "USELOCAL" in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.json"))):
    logging.log(logging.INFO, "[CHAT] Using OpenAI API")
    OPENAI_API_KEY = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.json")))["OPENAI_API_KEY"]
    openai.api_key = OPENAI_API_KEY
    engine = "ada"
else:
    logging.log(logging.INFO, "[CHAT] FAILED to use OpenAI API, Using local OpenAI API")
    openai.api_key = None
    openai.api_base = "http://localhost:5000/v1"
    engine = "ggml-gpt4all-j"

messages = [ 
    {"role": "system", "content": "You are a intelligent assistant. Speak in English only. Give short responses, enough to be spoken in 5 to 8 senconds. you are a chatbot at a science fair."},
    {"role": "system", "content": "You must be able to answer questions about the science fair from the json data given below:"},
    {"role": "system", "content": json.dumps(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "expo_data.json"))), indent=4)}
]
def get_response(message):
    # check for moderation issues with openai
    message = message.lower()
    mod = openai.Moderation.create(message, 'text-moderation-stable')
    if mod["results"][0]["flagged"]:
        return "I'm sorry, I cannot answer that."
    global messages
    messages.append(
        {"role": "user", "content": message},
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    return str(response.choices[0].message.content)

class ChatBot:
    def __init__(self, speaker=None):
        logging.log(logging.INFO, "[CHAT] ChatBot __init__")
        self.conversation_data = []
        self.fallbacks = []
        self.cache = {}
        self.nlp_cache = {}
        if not os.path.exists("./cache.json"):
            with open("./cache.json", "w") as f:
                f.write("{}")
        self.loader = yaml.SafeLoader
        self.speaker = speaker
        self.nlp = spacy.load("en_core_web_lg")
        
    def train(self, conversation_data):
        logging.log(logging.INFO, f"[CHAT] Training chatbot on {len(conversation_data)} conversation data points...")
        self.conversation_data += conversation_data
        self.save_hash = sha256.sha256(str(conversation_data).encode()).hexdigest()
        
    def create_speech_cache(self):
        logging.log(logging.INFO, "[CHAT] Creating text to speech cache...")
        for data in tqdm.tqdm(self.conversation_data, desc="Creating tts cache for train"):
            for utterance in data:
                if self.speaker and not self.is_question(utterance):
                    self.speaker.create_offline_cache(utterance, quiet=True)
        for utterance in tqdm.tqdm(self.fallbacks, desc="Creating tts cache for fallbacks"):
            if self.speaker and not self.is_question(utterance):
                self.speaker.create_offline_cache(utterance, quiet=True)
    
    def is_question(self, utterance):
        return "?" in utterance
    
    def train_fallbacks(self, fallbacks):
        logging.log(logging.INFO, f"[CHAT] Training chatbot on {len(fallbacks)} fallback data points...")
        self.fallbacks += fallbacks
    
    def calculate_similarity_dirty(self, a, b):
        return self.fuzz_ratio(a, b) / 100
    
    def calculate_similarity_better(self, a, b):
        if not a in self.nlp_cache:
            self.nlp_cache[a] = self.nlp(' '.join([str(token) for token in self.nlp(a.lower()) if not token.is_stop]))
        if not b in self.nlp_cache:
            self.nlp_cache[b] = self.nlp(' '.join([str(token) for token in self.nlp(b.lower()) if not token.is_stop]))
        return self.nlp_cache[a].similarity(self.nlp_cache[b])
    
    def calculate_similarity(self, query, conversation_entry):
        similarity_scores = []
        for utterance in conversation_entry:
            similarity_score = self.calculate_similarity_better(query, utterance)
            # TODO: Make nlp similarity better
            similarity_scores.append(similarity_score)
        return similarity_scores
    
    def answer(self, query):
        if query == "":
            return ""
        logging.log(logging.INFO, f"[CHAT] Answering query: {query}")
        if not query in self.cache:
            logging.log(logging.INFO, "[CHAT] Query not in cache. Calculating similarities...")
            similarities = []
            for conversation_entry in tqdm.tqdm(self.conversation_data, desc="Calculating similarities"):
                similarities.append(self.calculate_similarity(query, conversation_entry))
            logging.log(logging.INFO, "[CHAT] Similarities calculated. Linearizing...")
            
            linear_similarities = []
            for i, similarity_scores in enumerate(similarities):
                for j, score in enumerate(similarity_scores):
                    if score > THRESHOLD:
                        linear_similarities.append((score, (i, j)))
            logging.log(logging.INFO, "[CHAT] Linearized. Sorting...")
            self.cache[query] = linear_similarities
        else:
            linear_similarities = self.cache[query]

        self.save_cache()

        try:
            logging.log(logging.INFO, "[CHAT] Sorted matches. Finding max...")
            max_similarity = max(i[0] for i in linear_similarities)
            max_similarity_index = next(i[1] for i in linear_similarities if i[0] == max_similarity)
            logging.log(logging.INFO, f"[CHAT] Max found to be {max_similarity} at index {max_similarity_index}")
            return self.conversation_data[max_similarity_index[0]][max_similarity_index[1] + 1]
        except:
            try:
                logging.log(logging.INFO, "[CHAT] No matches found. Trying ChatGPT...")
                return get_response(query)
            except Exception as e:
                logging.log(logging.INFO, f"[CHAT] ChatGPT failed with {e}. Using random fallback...")
                return self.random_fallback()
        
    def random_fallback(self):
        logging.log(logging.INFO, "[CHAT] Random fallback!")
        return random.choice(self.fallbacks)
    
    def train_expo_data(self, expo_data):
        with open(expo_data, "r") as f:
            expo_data = json.load(f)
        data = []
        # Expo data:
        # {
        #    "categories": [ similarly for floors and room numbers
        #       "category1",
        #     ],
        #      "projects": [
        #           {title:asdf, description:asdf, category:asdf, floor:asdf, roomNumber: asdf},
        #   ]}
        # The chatbot should know everything about the data, and be able to inter-relate it

        # let's start with the categories:
        # "What are the categories?"
        # etc.
        logging.log(logging.INFO, "[CHAT] Training chatbot on categories...")
        qs = [
            "What are the categories?", 
            "What are the categories of projects?", 
            "What are the categories of projects in the fair?",
            "What are the categories of projects in the expo?",
            "What are the categories of projects in the exhibition?",
            "What are the topics of projects in the fair?",
            "What are the topics?"
        ]
        categories = list(expo_data["categories"])
        for i in range(len(categories)):
            categories[i] = categories[i]["title"]
        _ = [[
            qs[i], 
            "The topics are: " + ", ".join(categories[:-1]) + " and " + categories[-1] + ".",
        ] for i in range(len(qs))]
        for i in range(len(_)):
            data.append(_[i])
            
        # Explain a topic
        logging.log(logging.INFO, "[CHAT] Training chatbot on category explanations...")
        qs = [
            "What is the {} category?",
            "What is the {} topic?",
            "What is the {}?",
            "What is {}?",
            "What is the {} category about?",
            "What is the {} topic about?",
            "What is the {} about?",
            "What is {} about?",
            "Explain the {} category.",
            "Explain the {} topic.",
            "Explain the {}.",
            "Explain {}.",
            "Tell me about the {} category.",
            "Tell me about the {} topic.",
            "Tell me about the {}.",
            "Tell me about {}.",
        ]
        for category in categories:
            _ = [[
                qs[i].format(category), 
                "{}".format(expo_data["categories"][self.get_category_index(expo_data, category)]["description"]),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
        
        # "What are the projects in category X?"
        logging.log(logging.INFO, "[CHAT] Training chatbot on projects in categories...")
        qs = [
            "What are the projects in category {}?",
            "What are the projects in the {} category?",
            "What are the projects in the {} topic?",
            "What are the projects in the {} topics?",
            "What are the projects in {}",
            "What is in the {} category?",
            "What is in the {} topic?",
            "What is in the {} topics?",
            "What is in {}",
        ]
        projects = {}
        for category in categories:
            projects[category.lower().strip()] = []
        for project in expo_data["projects"]:
            projects[project["category"].lower().strip()].append(project["title"])
        for category in categories:
            _ = [[
                qs[i].format(category), 
                "The projects in the {} topic are: ".format(category) + ", ".join(projects[category.lower().strip()][:-1]) + " and " + projects[category.lower().strip()][-1] + ".",
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                
        # What are the projects in floor X?
        logging.log(logging.INFO, "[CHAT] Training chatbot on projects in floors...")
        qs = [
            "What are the projects in floor {}?",
            "What are the projects in the {} floor?",
        ]
        floors = {}
        for floor in expo_data["floors"]:
            floors[floor.lower().strip()] = []
        for project in expo_data["projects"]:
            floors[project["floor"].lower().strip()].append(project["title"])
        for floor in floors:
            _ = [[
                qs[i].format(floor), 
                "The projects in the {} floor are: ".format(self.numerify(floor)) + ", ".join(floors[floor.lower().strip()][:-1]) + " and " + floors[floor.lower().strip()][-1] + ".",
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                
        # What are the projects in room X?
        logging.log(logging.INFO, "[CHAT] Training chatbot on projects in rooms...")
        qs = [
            "What are the projects in room {}?",
            "What are the projects in the {} room?",
        ]
        rooms = {}
        for room in expo_data["rooms"]:
            rooms[room.lower().strip()] = []
        for project in expo_data["projects"]:
            rooms[project["roomNumber"].lower().strip()].append(project["title"])
        for room in rooms:
            try:
                _ = [[
                    qs[i].format(room), 
                    "The projects in room {} are: ".format(self.number_to_speech(room)) + ", ".join(rooms[room.lower().strip()][:-1]) + " and " + rooms[room.lower().strip()][-1] + ".",
                ] for i in range(len(qs))]
                for i in range(len(_)):
                    data.append(_[i])
            except IndexError: pass
        
        # Where is project X?
        logging.log(logging.INFO, "[CHAT] Training chatbot on project locations...")
        qs = [
            "Where is project {}?",
            "Where is the {} project?",
            "Where is the {}?",
            "Where is {}?",
            "Where can I find {}?",
            "Where can I find the {} project?",
            "Where can I find the {}?",
            "Where can I find project {}?"
        ]
        for project in expo_data["projects"]:
            _ = [[
                qs[i].format(project["title"]),
                "The {} project is in the {} floor, room {}.".format(
                    project["title"], 
                    self.numerify(project["floor"]), 
                    self.number_to_speech(project["roomNumber"])
                ),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                
        # Who made project X?
        logging.log(logging.INFO, "[CHAT] Training chatbot on project creators...")
        qs = [
            "Who made {}?",
            "Who made the {} project?",
            "Who made the {}?",
            "Who made project {}?",
            "Who created {}?",
            "Who created the {} project?",
            "Who created the {}?",
            "Who created project {}?",
        ]
        for project in expo_data["projects"]:
            # Create members string
            mmbrs = project["members"]
            _ = ""
            for i in range(len(mmbrs)):
                if i == len(mmbrs) - 1:
                    _ += " and "
                elif i != 0:
                    _ += ", "
                _ += mmbrs[i]
            _ = [[
                qs[i].format(project["title"]),
                "The {} project was made by {}.".format(
                    project["title"], 
                    _
                ),
            ] for i in range(len(qs))]
            print(_)
            for i in range(len(_)):
                data.append(_[i])
                
        # Train on project descriptions
        logging.log(logging.INFO, "[CHAT] Training chatbot on project descriptions...")
        qs = [
            "What is {}?",
            "What is the {} project?",
            "What is the {}?",
            "What is project {}?",
            "Explain {}.",
            "Explain the {} project.",
            "Explain the {}.",
            "Explain project {}.",
            "Tell me about {}.",
            "Tell me about the {} project.",
            "Tell me about the {}.",
            "Tell me about project {}.",
        ]
        for project in expo_data["projects"]:
            _ = [[
                qs[i].format(project["title"]),
                "{}".format(project["description"]),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                    
        # Train on student names and corresponding projects
        logging.log(logging.INFO, "[CHAT] Training chatbot on student names and corresponding projects...")
        qs = [
            "Who made {}?",
            "Who made the {} project?",
            "Who made the {}?",
            "Who made project {}?",
            "Who created {}?",
            "Who created the {} project?",
            "Who created the {}?",
            "Who created project {}?",
        ]
        for project in expo_data["projects"]:
            # Create members string
            mmbrs = project["members"]
            _names = ""
            for i in range(len(mmbrs)):
                if i == len(mmbrs) - 1:
                    _names += " and "
                elif i != 0:
                    _names += ", "
                _names += mmbrs[i]
            _ = [[
                qs[i].format(project["title"]),
                "The {} project was made by {}.".format(project["title"], _names),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                
        # Train on student places
        logging.log(logging.INFO, "[CHAT] Training chatbot on student places...")
        qs = [
            "Where is {}?",
            "Where is my friend {}?",
            "Where is my friend {}'s project?",
            "Where is {}'s project?",
        ]
        for project in expo_data["projects"]:
            for member in project["members"]:
                _ = [[
                    qs[i].format(member),
                    "The {} project is in the {} floor, room {}.".format(
                        project["title"], 
                        self.numerify(project["floor"]), 
                        self.number_to_speech(project["roomNumber"])
                    ),
                ] for i in range(len(qs))]
                for i in range(len(_)):
                    data.append(_[i])
                
        # When there are more that 2 projects with the same name
        found = {}
        for project in expo_data["projects"]:
            try:
                found[project["title"]] += 1
            except KeyError:
                found[project["title"]] = 1
        found_exceptions = [i for i in found if found[i] > 1]
        for exception in found_exceptions:
            print(exception)
        
        # TODO: Work in progress
        self.train(data)
        
    def numerify(self, number):
        if number == str(1):
            return "first"
        elif number == str(2):
            return "second"
        elif number == str(3):
            return "third"
        
    def number_to_speech(self, number):
        """
        Convert 16 into sixteen, etc.
        """
        number = str(number)
        number = list(number)
        for i in range(len(number)):
            number[i] = p.number_to_words(number[i])
        return " ".join(number)

    def get_category_index(self, expo_data, category):
        for i in range(len(expo_data["categories"])):
            if expo_data["categories"][i]["title"] == category:
                return i
        return None
    
    def fuzz_ratio(self, a, b):
        return fuzz.ratio(a, b)
    
    def load_cache(self):
        logging.log(logging.INFO, "[CHAT] Loading cache...")
        try:
            with open("cache.json", "r") as f:
                self.cache = json.load(f)
                try:
                    if self.cache["train_data_hash"] != self.save_hash:
                        self.cache = {
                            "train_data_hash": self.save_hash,
                        }
                        self.save_cache()
                except KeyError:
                    self.cache = {
                        "train_data_hash": self.save_hash,
                    }
                    self.save_cache()
        except FileNotFoundError:
            self.cache["train_data_hash"] = ""
            self.save_cache()
    
    def save_cache(self):
        logging.log(logging.INFO, "[CHAT] Saving cache...")
        try:
            with open("cache.json", "w") as f:
                if not "train_data_hash" in self.cache:
                    self.cache["train_data_hash"] = self.save_hash
                json.dump(self.cache, f)
        except FileNotFoundError:
            self.cache = {}
            
    def train_from_yaml(self, yaml_file):
        with open(yaml_file, "r") as f:
            data = yaml.load(f, Loader=self.loader)["conversations"]
        logging.log(logging.INFO, "Training chatbot on yaml file: {}".format(yaml_file))
        self.train(data)
    
    def train_from_corpus(self, corpus_dir, include=["*"]):
        logging.log(logging.INFO, "[CHAT] Training chatbot on corpus directory: {}".format(corpus_dir))
        for filename in os.listdir(corpus_dir):
            if include[0] == "*":
                if filename.endswith(".yml"):
                    self.train_from_yaml(os.path.join(corpus_dir, filename))
            else:
                if filename.split(".")[0] in include:
                    self.train_from_yaml(os.path.join(corpus_dir, filename))