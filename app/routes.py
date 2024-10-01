# app/routes.py
from flask import jsonify, request
from .auth import token_required
from .services.face_detection import detect_blinks
from .services.face_detection import adjust_gamma
from .services.face_detection import is_frame_too_dark
from .db.queries import (
    get_multimedia,
    insert_video_details,
)  # Asegúrate de que esta ruta de importación es correcta
import dlib
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
    FLAG_MINIO
)

# Cargando el detector de rostros y el predictor de puntos de referencia faciales
detector = dlib.get_frontal_face_detector()

def configure_routes(app, url_prefix=""):
    # Inicializar cliente MinIO usando las configuraciones de config.py
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )

        # Crear el bucket en MinIO si no existe
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)

    except S3Error as err:
        logging.error(f"Error connecting to MinIO: {err}")
        minio_client = None  # Deshabilitar el uso de MinIO si falla la configuración
    except Exception as e:
        logging.error(f"Unexpected error configuring MinIO: {e}")
        minio_client = None  # Deshabilitar el uso de MinIO si falla la configuración

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
    # @token_required  # Descomenta esto si quieres activar la autenticación vía token
    def process_video():
        video_file = request.files.get("video")
        if not video_file:
            return jsonify({"error": "No se proporcionó un archivo de video"}), 400

        if not video_file.mimetype.startswith("video"):
            return (
                jsonify(
                    {"error": "Tipo de archivo inválido. Por favor, sube un video."}
                ),
                400,
            )

        video_path = "temp_video.webm"
        video_file.save(video_path)
        logging.debug("Video guardado localmente.")

        cap = cv2.VideoCapture(video_path)
        frame_sequence = []
        frame_count = 0

        # Inicializar el rastreador de objetos (MOSSE en este caso)
        tracker_initialized = False
        tracker = cv2.TrackerKCF_create()

        bbox = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Si el rastreador aún no está inicializado, seleccionar una ROI y crear el rastreador
            if not tracker_initialized:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray, 0)
                if faces:
                    face = faces[0]  # Usar la primera cara detectada
                    (x, y, w, h) = (
                        face.left(),
                        face.top(),
                        face.width(),
                        face.height(),
                    )
                    bbox = (x, y, w, h)
                    tracker.init(frame, bbox)
                    tracker_initialized = True

            # Actualizar la posición de la cara con el rastreador
            if tracker_initialized:
                ok, bbox = tracker.update(frame)
                if ok:
                    x, y, w, h = [int(v) for v in bbox]
                    roi = frame[y : y + h, x : x + w]
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                    # Muestrear cada 5 cuadros
                    if frame_count % 5 == 0:
                        frame_sequence.append(roi)

            frame_count += 1

        cap.release()
        logging.debug("Video processing finished.")

        # Eliminar el archivo temporal después de su uso
        os.remove(video_path)
        logging.debug("Temporary video removed.")

        is_alive = detect_blinks(frame_sequence)
        logging.debug(f"Is the subject alive? {is_alive}")

        if FLAG_MINIO and minio_client:
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
                video_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{video_name}"

                # Usar split para obtener el id_solicitud
                pId_solicitud = int(
                    video_name.split("_")[0]
                )  # Esto dividirá el nombre y tomará el primer elemento

                # Insertar detalles del video en la base de datos
                insert_video_details(
                    id_solicitud=pId_solicitud,
                    tipo="VIDEO",
                    is_alive=is_alive,
                    ruta=video_url,
                )

            except S3Error as err:
                logging.error(f"Failed to upload video to MinIO: {err}")
                return jsonify({"error": "Failed to upload video to MinIO"}), 500
            except Exception as e:
                logging.error(f"Error inserting video details: {e}")
                return jsonify({"error": str(e)}), 500

        # Retornar el resultado de la detección de vida
        return jsonify({"is_alive": is_alive})
