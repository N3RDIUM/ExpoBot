import cv2
import face_recognition as fr
import uuid
import flask
import threading
import time

# Live face recognition
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Face data: Last seen
face_data = {}
def update_facedata(data):
    global face_data
    face_data.update(data)

# Load known faces
import os
faces = {}
for file in os.listdir("faces"):
    if file.endswith(".jpg"):
        try:
            faces[file[:-4]] = fr.face_encodings(fr.load_image_file("faces/" + file))[0]
            face_data[file[:-4]] = {"seen":[0]}
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
            return flask.jsonify({"success": True})
        else:
            return flask.jsonify({"success": False})
    app.run(port=5000)

thread = threading.Thread(target=start_server)
thread.start()
    
while True:
    ret, frame = cap.read()
    downscale_factor = 1
    downscaled_frame = cv2.resize(frame, (0, 0), fx=1/downscale_factor, fy=1/downscale_factor)
    if ret:        
        face_locations = fr.face_locations(downscaled_frame)
        face_encodings = fr.face_encodings(downscaled_frame, face_locations)
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
                    faces[fname] = fr.face_encodings(fr.load_image_file(f"faces/{fname}.jpg"))[0]
                    print("Loaded face: " + fname)
                    update_facedata({fname: {"seen":[time.time()]}})
                except:
                    print("Error loading face: " + fname)
            else:
                # Find the name of the face
                name = list(faces.keys())[matches.index(True)]
                # Mark left eye
                face_landmarks_list = fr.face_landmarks(downscaled_frame[top:bottom, left:right])
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
                    # If it's been more than 2 minutes since the last time we saw this face, update
                    if face_data[name]["seen"][-1] < time.time() - 20:
                        if face_data[name]["seen"][-1] == 0:
                            face_data[name]["seen"] = []
                        face_data[name]["seen"].append(time.time())
                    else:
                        face_data[name]["seen"][-1] = time.time()
        print(face_data)                
        # Show the frame
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            thread.join()
            break
    else:
        print("Error reading frame from camera")
        continue