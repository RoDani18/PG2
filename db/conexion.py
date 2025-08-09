import psycopg2

def conectar():
    return psycopg2.connect(
        host="localhost",
        database="asistentePG",
        user="postgres",
        password="admin123"  # o el que tú tengas
    )

try:
    conn = conectar()
    print("✅ Conexión exitosa a la base de datos.")
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)
