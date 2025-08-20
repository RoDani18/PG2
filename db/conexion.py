# db/conexion.py
import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "asistentePG"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            port=os.getenv("DB_PORT", "5432")
        )
        print("✅ Conexión exitosa a la base de datos.")
        conn.close()
    except Exception as e:
        print("❌ Error de conexión:", e)

if __name__ == "__main__":
    conectar()
