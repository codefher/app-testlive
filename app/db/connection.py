# db/connection.py
import psycopg2
from ..config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_db_connection():
    """Establece y devuelve una conexión a la base de datos PostgreSQL"""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    return conn
