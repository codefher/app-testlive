# db/queries.py
import psycopg2
from .connection import get_db_connection


def get_multimedia():
    """Obtiene y devuelve todos los registros de multimedia de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM certificacion.multimedia;")
        multimedia = cursor.fetchall()
        return multimedia
    except psycopg2.Error as e:
        print(f"Error fetching multimedia: {e}")
        raise Exception(
            f"Database error: {e}"
        )  # Propaga el error para que pueda ser capturado en el endpoint
    finally:
        cursor.close()
        conn.close()


def insert_multimedia(id_solicitud, tipo, respuesta, ruta):
    """Inserta un nuevo registro en la tabla multimedia."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO certificacion.multimedia
            (id_multimedia, id_solicitud, tipo, respuesta, ruta, fecha_bitacora, usuario_bitacora, registro_bitacora)
            VALUES(nextval('certificacion.multimedia_id_multimedia_seq'::regclass), %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_USER, inet_client_addr())
            """,
            (id_solicitud, tipo, respuesta, ruta),
        )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(
            f"Database error: {e.pgerror}"
        )  # Lanza una excepción con el error de la base de datos
    finally:
        cursor.close()
        conn.close()
