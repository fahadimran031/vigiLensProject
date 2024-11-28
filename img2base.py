import base64
import socketio


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
        return encoded_image.decode('utf-8')

image_path = "./245322733097.jpeg"
encoded_image = image_to_base64(image_path)

sio = socketio.Client()
@sio.event
def connect():
    print("Connected to the server")
    sio.emit("message", {
"user_id":245322733097,
"time_stamp":1234,
"img":encoded_image
})

@sio.event
def Alert(data):
    print(f"Received message: {data}")

@sio.event
def disconnect():
    print("Disconnected from the server")

sio.connect("http://localhost:5000")
sio.wait()
