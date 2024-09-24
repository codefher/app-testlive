import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargando el detector de rostros y el predictor de puntos de referencia faciales
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

# Umbral y contador para detectar parpadeo
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def preprocess_image(gray_frame):
    # Aplicar suavizado Gaussian para reducir ruido
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    # Aumentar el contraste de la imagen
    gray_frame = cv2.equalizeHist(gray_frame)
    return gray_frame


def adjust_gamma(image, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")
    return cv2.LUT(image, table)


def is_frame_too_dark(frame, threshold=50):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    return mean_brightness < threshold


def detect_blinks(frame_sequence):
    blink_count = 0
    consecutive_frames = 0
    ear_history = []

    try:
        for frame in frame_sequence:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = preprocess_image(gray)  # Preprocesamiento de la imagen

            faces = detector(gray, 0)

            for face in faces:
                shape = predictor(gray, face)
                shape = np.array([[p.x, p.y] for p in shape.parts()])
                leftEye = shape[42:48]
                rightEye = shape[36:42]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                ear_history.append(ear)

                # Mantener solo el historial de los últimos 5 cuadros
                if len(ear_history) > 5:
                    avg_ear = np.mean(ear_history[-5:])

                    if avg_ear < EYE_AR_THRESH:
                        consecutive_frames += 1
                    else:
                        if consecutive_frames >= EYE_AR_CONSEC_FRAMES:
                            blink_count += 1
                            logging.debug(
                                f"Blink detected. Total blinks: {blink_count}"
                            )
                        consecutive_frames = 0
                else:
                    # Si aún no hay suficiente historial, usar el EAR actual
                    if ear < EYE_AR_THRESH:
                        consecutive_frames += 1
                    else:
                        if consecutive_frames >= EYE_AR_CONSEC_FRAMES:
                            blink_count += 1
                            logging.debug(
                                f"Blink detected. Total blinks: {blink_count}"
                            )
                        consecutive_frames = 0

        logging.debug(f"Total blinks counted: {blink_count}")
        return blink_count > 0

    except Exception as e:
        logging.error(f"Error during blink detection: {e}")
        return False
