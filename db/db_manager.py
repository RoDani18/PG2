# db_manager.py
import psycopg2
from psycopg2 import OperationalError
from backend.offline import fallback
from backend.offline import sync_to_postgres


PG_CONN = {
    "host": "localhost",
    "database": "asistentePG",
    "user": "postgres",
    "password": "admin123",
    "port": 5432
}

def guardar_producto(nombre, cantidad):
    try:
        conn_pg = psycopg2.connect(**PG_CONN)
        cur_pg = conn_pg.cursor()
        cur_pg.execute("""
            INSERT INTO inventario (nombre, cantidad, precio)
            VALUES (%s, %s, 0)
            ON CONFLICT (nombre) DO UPDATE 
                SET cantidad = inventario.cantidad + EXCLUDED.cantidad
        """, (nombre, cantidad))
        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()
        print("💾 Guardado directamente en PostgreSQL.")
    except OperationalError:
        print("⚠️ Sin conexión. Guardando offline...")
        fallback.guardar_producto(nombre, cantidad)

