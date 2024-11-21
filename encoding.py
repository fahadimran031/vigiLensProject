import face_recognition
import os
import pickle

# Directory containing images of known faces
known_faces_dir = "known_faces/"
encoding_file = "face_encodings.pkl"

known_encodings = []
known_names = []

for filename in os.listdir(known_faces_dir):
    filepath = os.path.join(known_faces_dir, filename)
    image = face_recognition.load_image_file(filepath)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        known_encodings.append(encodings[0])  # Save the first face encoding
        known_names.append(os.path.splitext(filename)[0])  # Save the name

# Save encodings and names
with open(encoding_file, "wb") as file:
    pickle.dump((known_encodings, known_names), file)

print(f"Processed {len(known_encodings)} faces and saved to {encoding_file}.")
