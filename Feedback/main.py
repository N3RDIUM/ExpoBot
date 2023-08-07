import requests

while True:
    faces = requests.get("http://localhost:5000/faces").json()
    for face in faces:
        if len(faces[face]["seen"]) >= 2:
            print(face + ", Please give your valuable feedback")