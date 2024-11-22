from flask import Flask, render_template, jsonify ,request
from flask_socketio import SocketIO, send, emit
import json
import base64
import time


app = Flask(__name__)
socketio = SocketIO(app)
clients=set()

def worker(img_path,sid):
    time.sleep(10)
    with open(img_path, "rb") as image_file:
        image_binary = image_file.read()
    img = base64.b64encode(image_binary).decode("utf-8")
    socketio.emit("Alert",{img:img},sid)
    
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
    socketio.start_background_task(worker,f"./images/{msg['user_id']}.{msg['time_stamp']}.png",request.sid)
    send(f"Echo: {msg}") 

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
