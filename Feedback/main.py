import cv2
import face_recognition as fr
import uuid
import flask
import threading
import time
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
CAMERA = int(json.load(open("config.json"))["CAMERA"])

# Live face recognition
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Face data: Last seen
face_data = {}
special_greet = []
greeted = []
def update_facedata(data):
    global face_data
    face_data.update(data)
def update_specialgreet(data):
    global special_greet
    special_greet.append(data)

# Load known faces
import os
faces = {}
for file in os.listdir("faces"):
    if file.endswith(".jpg"):
        try:
            faces[file[:-4]] = fr.face_encodings(fr.load_image_file("faces/" + file), model="small")[0]
            face_data[file[:-4]] = {"seen":[0], "feedback": False}
            print("Loaded face: " + file)
        except:
            print("Error loading face: " + file)
print("Loaded " + str(len(faces)) + " faces")

def start_server():
    app = flask.Flask(__name__)
    @app.route("/faces")
    def get_faces():
        return flask.jsonify(face_data)
    @app.route("/feedback-given/<name>")
    def feedback_given(name):
        if name in face_data:
            face_data[name]["seen"] = []
            face_data[name]["feedback"] = True
            return flask.jsonify({"success": True})
        else:
            return flask.jsonify({"success": False})
    @app.route("/sgget/")
    def special_greet_get():
        greets = special_greet.copy()
        special_greet.clear()
        greeted.extend(greets)
        return flask.jsonify({"data": greets})
    app.run(port=5000)
    

thread = threading.Thread(target=start_server)
thread.start()

import subprocess
import sys
import os

subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "feedback.py")])
subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "transcribe_bg.py")])
    
while True:
    ret, frame = cap.read()
    downscale_factor = 2
    downscaled_frame = cv2.resize(frame, (0, 0), fx=1/downscale_factor, fy=1/downscale_factor)
    if ret:        
        face_locations = fr.face_locations(downscaled_frame, model="hog")
        face_encodings = fr.face_encodings(downscaled_frame, face_locations, model="small")
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = fr.compare_faces(list(faces.values()), face_encoding)
            if True not in matches:
                fname = str(uuid.uuid4())
                fname = fname[:fname.find("-")]
                factor = 32 // downscale_factor
                _top = max(0, top - factor)
                _bottom = min(frame.shape[0], bottom + factor)
                _left = max(0, left - factor)
                _right = min(frame.shape[1], right + factor)
                cv2.imwrite(f"faces/{fname}.jpg", frame[_top*downscale_factor : _bottom*downscale_factor, _left*downscale_factor : _right*downscale_factor])
                try:
                    faces[fname] = fr.face_encodings(fr.load_image_file(f"faces/{fname}.jpg"), model="small")[0]
                    print("Loaded face: " + fname)
                    update_facedata({fname: {"seen":[time.time()], "feedback": False}})
                except:
                    print("Error loading face: " + fname)
            else:
                # Find the name of the face
                name = list(faces.keys())[matches.index(True)]
                # Special greetings
                for special in ["Creator", "Creator2", "Creator3", "Mentor"]:
                    if name == special and name not in greeted:
                        update_specialgreet(name)
                        greeted.append(name)
                # Mark left eye
                face_landmarks_list = fr.face_landmarks(downscaled_frame[top:bottom, left:right], model="small")
                for face_landmarks in face_landmarks_list:
                    eye = face_landmarks["left_eye"]
                    avg_x = sum([x[0] for x in eye]) / len(eye)
                    avg_y = sum([x[1] for x in eye]) / len(eye)
                    avg_x += left
                    avg_y += top
                    size = max([x[0] for x in eye]) - min([x[0] for x in eye])
                    cv2.rectangle(frame, (int(avg_x - size / 2)*downscale_factor, int(avg_y - size / 2)*downscale_factor), (int(avg_x + size / 2)*downscale_factor, int(avg_y + size / 2)*downscale_factor), (0, 255, 0), 1)
                    cv2.putText(frame, name, (int(avg_x - size / 2)*downscale_factor, int(avg_y - size)*downscale_factor), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.circle(frame, (int(avg_x)*downscale_factor, int(avg_y)*downscale_factor), 1, (0, 255, 0), 3)
                # Update last seen
                if name in face_data:
                    if not face_data[name]["feedback"]:
                        # If it's been more than 2 minutes since the last time we saw this face, update
                        if face_data[name]["seen"][-1] < time.time() - 20:
                            if face_data[name]["seen"][-1] == 0:
                                face_data[name]["seen"] = []
                            face_data[name]["seen"].append(time.time())
                        else:
                            face_data[name]["seen"][-1] = time.time()

        # Show the frame
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            thread.join()
            break
    else:
        print("Error reading frame from camera")
        continue