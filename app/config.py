import os

# Token key
SECRET_KEY = "SJDFSKJDFBSDJKFBSDFBJSFKSDFNSDFSDFLKNSDFJKSDFKHSBDFKJSDFBSJKDF"

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
