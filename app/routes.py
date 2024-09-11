# app/routes.py
from flask import jsonify, request
from .auth import token_required
from .services.face_detection import detect_blinks
from .db.queries import (
    get_multimedia,
    insert_video_details,
)  # Asegúrate de que esta ruta de importación es correcta
import os
import cv2
import logging
import io
from minio import Minio
from minio.error import S3Error
from .config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME,
    MINIO_SECURE,
)


def configure_routes(app, url_prefix=""):
    # Inicializar cliente MinIO usando las configuraciones de config.py
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )

    # Crear el bucket en MinIO si no existe
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)

    @app.route(url_prefix + "/multimedias", methods=["POST"])
    @token_required  # Descomenta esto si quieres activar la autenticación vía token
    def create_multimedia():
        data = request.json
        id_solicitud = data.get("id_solicitud", 0)
        tipo = data.get("tipo", "")
        respuesta = data.get("respuesta", False)
        ruta = data.get("ruta", "")

        try:
            insert_video_details(id_solicitud, tipo, respuesta, ruta)
            return (
                jsonify({"success": True, "message": "Multimedia added successfully"}),
                201,
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route(url_prefix + "/multimedias", methods=["GET"])
    @token_required
    def list_multimedias():
        try:
            multimedias = get_multimedia()
            if multimedias is not None:
                return jsonify(multimedias), 200
            else:
                return jsonify({"error": "Error fetching multimedia data"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route(url_prefix + "/life-detection", methods=["POST"])
    @token_required  # Descomenta esto si quieres activar la autenticación vía token
    def process_video():
        # Obtener el archivo de video de la solicitud
        video_file = request.files.get("video")
        if not video_file:
            return jsonify({"error": "No video file provided"}), 400

        # Guardar el video temporalmente en el servidor local
        video_path = "temp_video.webm"
        video_file.save(video_path)
        logging.debug("Video saved locally.")

        # Procesar el video con OpenCV, por ejemplo, detectar blinks
        frame_sequence = []
        frame_count = 0
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % 5 == 0:  # Tomar un frame cada 5
                frame_sequence.append(frame)
            frame_count += 1

        cap.release()
        os.remove(video_path)  # Borrar el archivo local una vez procesado
        is_alive = detect_blinks(frame_sequence)
        logging.debug(f"Is the subject alive? {is_alive}")

        # Guardar el video en MinIO y obtener la URL de MinIO
        try:
            video_file.seek(0)
            video_data = video_file.read()
            video_stream = io.BytesIO(video_data)
            video_name = video_file.filename

            minio_client.put_object(
                MINIO_BUCKET_NAME,
                video_name,
                video_stream,
                length=len(video_data),
                content_type="video/webm",
            )
            logging.debug(f"Video uploaded to MinIO: {video_name}")

            # Construir la ruta completa donde el video está guardado
            video_url = f"htrrtp://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{video_name}"

            # Insertar detalles del video en la base de datos
            insert_video_details(
                id_solicitud=12, tipo="VIDEO", is_alive=is_alive, ruta=video_url
            )  # Asumiendo que tienes id_solicitud disponible

        except S3Error as err:
            logging.error(f"Failed to upload video to MinIO: {err}")
            return jsonify({"error": "Failed to upload video"}), 500
        except Exception as e:
            logging.error(f"Error inserting video details: {e}")
            return jsonify({"error": str(e)}), 500

        # Retornar el resultado de la detección de vida
        return jsonify({"is_alive": is_alive})
