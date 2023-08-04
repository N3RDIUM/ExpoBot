import spacy
import random
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