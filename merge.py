import json
j1 = json.loads(open('Chatbot/expo_data.json').read())
j2 = json.loads(open('edata.json').read())
j1.update(j2)
with open('Chatbot/merged_data.json', 'w') as f:
    json.dump(j1, f, indent=4)