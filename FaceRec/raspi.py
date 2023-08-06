import cv2
import face_recognition as fr

# Live face recognition
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if ret:
        face_locations = fr.face_locations(frame)
        for top, right, bottom, left in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        print("Error reading frame from camera")
        break