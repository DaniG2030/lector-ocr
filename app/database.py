import psycopg2
import os

# CONFIGURACIÓN MANUAL (Si esto funciona, el problema era tu .env o lectura de archivos)
DB_HOST = "localhost"
DB_NAME = "redyon_db"  # Verifica que este sea el nombre real de tu base
DB_USER = "postgres"   # Verifica tu usuario
DB_PASS = "Chooper212030" # Verifica tu contraseña

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        # Imprimimos el error real aquí
        print(f"ERROR DE CONEXIÓN DETALLADO: {e}")
        raise e
