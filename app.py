from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Cargar el clasificador pre-entrenado para rostros (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/process-video', methods=['POST'])
def process_video():
    video_file = request.files.get('video')
    if not video_file:
        return jsonify({"error": "No video file provided"}), 400

    video_path = 'temp_video.webm'
    video_file.save(video_path)

    is_alive = detect_liveness(video_path)

    os.remove(video_path)
    return jsonify({"is_alive": is_alive})

def detect_liveness(video_path):
    cap = cv2.VideoCapture(video_path)
    face_detected = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        
        if len(faces) > 0:
            face_detected = True
            break

    cap.release()
    return face_detected

if __name__ == '__main__':
    app.run(debug=True)
