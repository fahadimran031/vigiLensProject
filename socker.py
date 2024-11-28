from flask import Flask, render_template, jsonify ,request
from flask_socketio import SocketIO, send, emit
import json
import base64
import time
from datetime import datetime
import face_recognition
import pickle
import numpy as np
from mail import mailing

app = Flask(__name__)
socketio = SocketIO(app)
clients=set()
mail=mailing()

def recognize_faces(image_path):
    with open("face_encodings.pkl", "rb") as file:
        known_encodings, known_names = pickle.load(file)
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    if not face_locations:
        print("No faces detected.")
        return 0
    for face_location, face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        min_distance = np.min(distances)

        if min_distance < 0.5:
            match_index = np.argmin(distances)
            name = known_names[match_index]
            print(f"Recognized: {name}")
            return True
        else:
            print("ALERT: Intruder detected!")
            return False


def worker(img_path,tst,sid):
    res=recognize_faces(img_path)
    if not (res):
        socketio.emit("Alert",{"alert":"intruder detected"},to=sid)
        alert=mail.compose_alert("BossBattlar","bossbattlar@gmail.com",img_path=img_path)
        mail.send(alert)
            

@app.route('/')
def index():
    return jsonify({"error":False})

@socketio.on('message')
def handle_message(msg):
    if type(msg) is not dict:
        msg=json.loads(msg)
    image_data = base64.b64decode(msg['img'])
    with open(f"./images/{msg['user_id']}.{msg['time_stamp']}.png", 'wb') as image_file:
        image_file.write(image_data)
    socketio.start_background_task(worker,f"./images/{msg['user_id']}.{msg['time_stamp']}.png",msg['time_stamp'],request.sid)

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    clients.add(request.sid)
    send("Welcome to the WebSocket server!") 

@socketio.on('disconnect')
def handle_disconnect():
    clients.remove(request.sid)
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app,debug=True, host='127.0.0.1', port=5000)
