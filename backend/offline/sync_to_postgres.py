# offline/sync_to_postgres.py
import os
import psycopg2
from dotenv import load_dotenv
from backend.offline import fallback

load_dotenv()

PG_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "asistentePG"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "port": os.getenv("DB_PORT", 5432)
}

def sync():
    try:
        productos = fallback.listar_productos_no_sincronizados()
        if not productos:
            print("✅ No hay productos pendientes de sincronizar.")
            return

        conn_pg = psycopg2.connect(**PG_CONN)
        cur_pg = conn_pg.cursor()

        for pid, nombre, cantidad in productos:
            cur_pg.execute("""
                INSERT INTO inventario (nombre, cantidad, precio)
                VALUES (%s, %s, 0)
                ON CONFLICT (nombre) DO UPDATE SET cantidad = inventario.cantidad + EXCLUDED.cantidad
            """, (nombre, cantidad))

        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()

        fallback.marcar_como_sincronizado([p[0] for p in productos])
        print(f"✅ Sincronizados {len(productos)} productos a PostgreSQL.")

    except Exception as e:
        print(f"❌ Error sincronizando: {e}")

if __name__ == "__main__":
    sync()
