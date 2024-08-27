# app/routes.py
from flask import jsonify, request
from .auth import token_required
from .services.face_detection import detect_blinks
import os
import cv2
import logging

def configure_routes(app):

    @app.route('/life-detection', methods=['POST'])
    @token_required
    def process_video():
        video_file = request.files.get('video')
        if not video_file:
            return jsonify({"error": "No video file provided"}), 400

        video_path = 'temp_video.webm'
        video_file.save(video_path)
        logging.debug("Video saved locally.")

        frame_sequence = []
        frame_count = 0
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % 5 == 0:
                frame_sequence.append(frame)
            frame_count += 1

        cap.release()
        os.remove(video_path)
        is_alive = detect_blinks(frame_sequence)
        logging.debug(f"Is the subject alive? {is_alive}")
        return jsonify({"is_alive": is_alive})

