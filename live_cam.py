import cv2
import os
from datetime import datetime
import face_recognition
import pickle
import numpy as np

# Replace with the URL of your mobile IP camera
ipcam_url = "http://192.168.137.82:8080/video"  # Ensure this URL is correct

# Directory to save screenshots
output_folder = "./frames"

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load known face encodings
with open("face_encodings.pkl", "rb") as file:
    known_encodings, known_names = pickle.load(file)

# Open video stream from the mobile camera
video_capture = cv2.VideoCapture(ipcam_url)

if not video_capture.isOpened():
    print("Error: Unable to access video stream.")
    exit()

print("Press 'spacebar' to capture a screenshot and run face recognition. Press 'q' to quit.")

# Function to run face recognition
def recognize_faces(image_path):
    # Load the input image
    image = face_recognition.load_image_file(image_path)

    # Detect faces
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    if not face_locations:
        print("No faces detected.")
        return

    for face_location, face_encoding in zip(face_locations, face_encodings):
        # Compare with known faces
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        min_distance = np.min(distances)

        if min_distance < 0.5:  # Match threshold
            match_index = np.argmin(distances)
            name = known_names[match_index]
            print(f"Recognized: {name}")
        else:
            print("ALERT: Intruder detected!")

# Display the live feed
while True:
    ret, frame = video_capture.read()

    if not ret:
        print("Failed to retrieve frame.")
        break

    # Show the frame in a window
    cv2.imshow("Live Feed", frame)

    # Check for key presses
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):  # Quit the program
        break
    elif key == ord(' '):  # Spacebar to capture a screenshot and run face recognition
        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(output_folder, f"screenshot_{timestamp}.jpg")

        # Save the frame
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved: {filename}")

        # Run face recognition on the saved screenshot
        recognize_faces(filename)

# Release video capture and close OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
