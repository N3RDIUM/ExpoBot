import spacy
import random
import json
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
        similarities = []
        for i in range(len(self.conversation_data)):
            similarity_scores = []
            for j in range(len(self.conversation_data[i])):
                similarity_scores.append(similarity(query, self.conversation_data[i][j]))
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
                "The projects in the {} category are: ".format(category) + ", ".join(projects[category.lower().strip()][:-1]) + " and " + projects[category.lower().strip()][-1] + ".",
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
        
        # Where is project X?
        qs = [
            "Where is project {}?",
            "Where is the {} project?",
            "Where is the {}?",
            "Where is {}?",
            "Where can I find {}?",
            "Where can I find the {} project?",
            "Where can I find the {}?",
            "Where can I find project {}?",
            "Where can I find the project {}?",
            "Where can I find the {}?",
            "Where can I find {}?",
        ]
        for project in expo_data["projects"]:
            _ = [[
                qs[i].format(project["title"]),
                "The {} project is in the {} floor, room {}.".format(project["title"], self.numerify(project["floor"]), project["roomNumber"]),
            ] for i in range(len(qs))]
            for i in range(len(_)):
                data.append(_[i])
        
        # TODO: Work in progress
        self.train(data)
        
    def numerify(self, number):
        # if number is 1, return 1st
        # if number is 2, return 2nd
        # if number is 3, return 3rd
        if number == str(1):
            return "1st"
        elif number == str(2):
            return "2nd"
        elif number == str(3):
            return "3rd"