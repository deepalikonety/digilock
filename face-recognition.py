import threading
import cv2
from deepface import DeepFace
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0

face_match = False
face_match_lock = threading.Lock()

reference_img = cv2.imread("manasa.jpg")

# Extract face embeddings from the reference image
reference_embedding = DeepFace.represent(reference_img)[0]['embedding']

# Parameters for smoothing
SMOOTHING_WINDOW_SIZE = 5
smoothed_results = []

def check_face(frame):
    global face_match
    try:
        # Extract face embeddings from the current frame
        frame_embedding = DeepFace.represent(frame)[0]['embedding']
        
        # Compute cosine similarity
        similarity = np.dot(reference_embedding, frame_embedding) / (np.linalg.norm(reference_embedding) * np.linalg.norm(frame_embedding))
        threshold = 0.6  # Adjust threshold as needed
        verified = similarity > threshold
        
        with face_match_lock:
            smoothed_results.append(verified)
            if len(smoothed_results) > SMOOTHING_WINDOW_SIZE:
                smoothed_results.pop(0)  # Remove oldest result
            face_match = sum(smoothed_results) / len(smoothed_results) > 0.5  # Majority vote
    except ValueError:
        with face_match_lock:
            face_match = False

while True:
    ret, frame = cap.read()

    if ret:
        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()
            except ValueError:
                pass
        counter += 1

        with face_match_lock:
            match_text = "MATCH!" if face_match else "NO MATCH!"
        cv2.putText(frame, match_text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0) if face_match else (0, 0, 255), 3)

        cv2.imshow("video", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
