import face_recognition
import cv2
import pickle
import numpy as np

# Load known face encodings
with open("face_encodings.pkl", "rb") as file:
    known_encodings, known_names = pickle.load(file)

# Read input image
input_image_path = "245322733097.jpeg"  # Replace with actual image
image = face_recognition.load_image_file(input_image_path)

# Detect faces
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

for face_location, face_encoding in zip(face_locations, face_encodings):
    # Compare with known faces
    distances = face_recognition.face_distance(known_encodings, face_encoding)
    min_distance = np.min(distances)

    if min_distance < 0.6:  # Match threshold
        match_index = np.argmin(distances)
        name = known_names[match_index]
        print(f"Recognized: {name}")
    else:
        print("ALERT: Intruder detected!")
