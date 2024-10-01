import os

# Token key
SECRET_KEY = "SJDFSKJDFBSDJKFBSDFBJSFKSDFNSDFSDFLKNSDFJKSDFKHSBDFKJSDFBSJKDF"

# Bandera regisro MinIO 
FLAG_MINIO = os.getenv('FLAG_MINIO', 'False').lower() == 'true'

# Configuración de MinIO
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', "10.0.50.19:9040")
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', "user.certificacion")
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', "Segip2024dsadsadsadsa")
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', "video-bucket")
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() == 'true'  # Convierte el valor a booleano

# Configuración DB
DB_NAME = os.getenv("DB_NAME", "certificacion_digital")
DB_USER = os.getenv("DB_USER", "user_ed12")
DB_PASSWORD = os.getenv("DB_PASSWORD", "user_ed12")
# DB_USER = os.getenv("DB_USER", "user_multimedia_ed12")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "user_multimedia_ed12")
DB_HOST = os.getenv("DB_HOST", "10.0.50.24")
DB_PORT = os.getenv("DB_PORT", "5432")
