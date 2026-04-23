import ssl
import cv2
import base64
import numpy as np
import json
import os
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import tensorflow as tf

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

# Load model and class names
print("Loading model...")
model = tf.keras.models.load_model('models/MobileNetV2_best.keras')

with open('class_names.json') as f:
    class_names = json.load(f)

print(f"Model loaded successfully.")
print(f"Classes: {class_names}")


def preprocess_frame(frame): #for the model
    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('video_frame')
def handle_video_frame(data):
    img_data = base64.b64decode(data.split(',')[1])
    np_img   = np.frombuffer(img_data, dtype=np.uint8)
    frame    = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return

    # Face Detection
    gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        emit('no_face', {})
        return

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face = frame[y:y+h, x:x+w]

    processed = preprocess_frame(face)
    preds     = model.predict(processed, verbose=0)
    pred_idx  = np.argmax(preds[0])
    label     = class_names[pred_idx]
    confidence = float(preds[0][pred_idx]) * 100

    top3_idx = np.argsort(preds[0])[::-1][:3]
    top3 = [
        {
            'label':      class_names[i],
            'confidence': round(float(preds[0][i]) * 100, 2)
        }
        for i in top3_idx
    ]

    emit('prediction', {
        'label':      label,
        'confidence': round(confidence, 2),
        'top3':       top3
    })

    print(f"Predicted: {label} ({confidence:.1f}%)")

if __name__ == '__main__':
    cert_file = 'certificates/certificate.crt'
    key_file  = 'certificates/private.key'

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        ssl_context=ssl_context,
        allow_unsafe_werkzeug=True,
    )




"""import ssl
import cv2
import base64
import numpy as np
import os
from flask import Flask, render_template
from flask_socketio import SocketIO

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('video_frame')
def handle_video_frame(data):
    # Decode base64 image
    img_data = base64.b64decode(data.split(',')[1])
    np_img = np.frombuffer(img_data, dtype=np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Save the received image to a file
    filename = "received_frame.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved frame as {filename}")

if __name__ == '__main__':
    cert_file = 'certificates/certificate.crt'
    key_file = 'certificates/private.key'

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        ssl_context=ssl_context,
        allow_unsafe_werkzeug=True,
    )
"""