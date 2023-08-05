import spacy
import random
import json
import inflect
import fuzzywuzzy.fuzz as fuzz
p = inflect.engine()        
nlp = spacy.load('en_core_web_md')

THRESHOLD = 0.6 # Similarity threshold
def similarity(a, b):
    a = nlp(a)
    b = nlp(b)
    return a.similarity(b)

class ChatBot:
    def __init__(self):
        self.conversation_data = []
        self.fallbacks = []
        
    def train(self, conversation_data):
        self.conversation_data += conversation_data
    
    def train_fallbacks(self, fallbacks):
        self.fallbacks += fallbacks
    
    def answer(self, query):
        if query == "": return ""
        similarities = []
        for i in range(len(self.conversation_data)):
            similarity_scores = []
            for j in range(len(self.conversation_data[i])):
                similarity_scores.append(
                    similarity(query, self.conversation_data[i][j]) +\
                    self.fuzz_ratio(query, self.conversation_data[i][j])
                )
            similarities.append(similarity_scores)
            
        linear_similarities = []
        for i in range(len(similarities)):
            for j in range(len(similarities[i])):
                linear_similarities.append((similarities[i][j], (i, j))) if similarities[i][j] > THRESHOLD else None
        try:
            max_similarity = max([i[0] for i in linear_similarities])
            max_similarity_index = [i[1] for i in linear_similarities if i[0] == max_similarity][0]
            return self.conversation_data[max_similarity_index[0]][max_similarity_index[1]+1]
        except:
            return self.random_fallback()
        
    def random_fallback(self):
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
        ]
        for category in categories:
            _ = [[
                qs[i].format(category), 
                "{}".format(expo_data["categories"][self.get_category_index(expo_data, category)]["description"]),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
        
        # "What are the projects in category X?"
        qs = [
            "What are the projects in category {}?",
            "What are the projects in the {} category?",
            "What are the projects in the {} topic?",
            "What are the projects in the {} topics?",
            "What are the projects in {}",
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
                "The projects in the {} floor are: ".format(floor) + ", ".join(floors[floor.lower().strip()][:-1]) + " and " + floors[floor.lower().strip()][-1] + ".",
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
                
        # What are the projects in room X?
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
                print(_)
                for i in range(len(_)):
                    data.append(_[i])
            except IndexError: pass
        
        # Where is project X?
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