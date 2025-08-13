import os

# Token key
SECRET_KEY = "SJDFSKJDFBSDJKFBSDFBJSFKSDFNSDFSDFLKNSDFJKSDFKHSBDFKJSDFBSJKDF"

# Bandera regisro MinIO 
FLAG_MINIO = os.getenv('FLAG_MINIO', 'False').lower() == 'true'

# Configuración de MinIO
MINIO_ENDPOINT = "10.0.50.19:9040"
MINIO_ACCESS_KEY = "user.certificacion"
MINIO_SECRET_KEY = "Segip2024"
MINIO_BUCKET_NAME = "video-bucket"
MINIO_SECURE = False  # Cambia a True si estás usando HTTPS

# Configuración DB
DB_NAME = os.getenv("DB_NAME", "certificacion_digital")
DB_USER = os.getenv("DB_USER", "user_ed12")
DB_PASSWORD = os.getenv("DB_PASSWORD", "user_ed12")
# DB_USER = os.getenv("DB_USER", "user_multimedia_ed12")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "user_multimedia_ed12")
DB_HOST = os.getenv("DB_HOST", "10.0.50.24")
DB_PORT = os.getenv("DB_PORT", "5432")

# Intervalo de tiempo para la detección de parpadeos
# 0.0 = muy flexible ←→ 1.0 = muy estricto
BLINK_SENS = float(os.getenv("BLINK_SENS", "0.60"))
BLINK_SENS = max(0.0, min(1.0, BLINK_SENS))  # limitar 0..1

# Rango base
_T_MIN, _T_MAX = 0.20, 0.29      # EAR threshold: flexible → estricto
_F_MIN, _F_MAX = 2, 5            # frames consecutivos: flexible → estricto

# Invertimos el sentido:
EYE_AR_THRESH = _T_MAX - BLINK_SENS * (_T_MAX - _T_MIN)
EYE_AR_CONSEC_FRAMES = int(round(_F_MIN + BLINK_SENS * (_F_MAX - _F_MIN)))