import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "offline_sqlite.db"

def init_rutas():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rutas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                destino TEXT,
                estado TEXT,
                tiempo_estimado TEXT,
                lat_actual REAL,
                lng_actual REAL,
                sincronizado INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def agregar_ruta(pedido_id, destino, estado, tiempo_estimado, lat, lng):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rutas (pedido_id, destino, estado, tiempo_estimado, lat_actual, lng_actual, sincronizado)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (pedido_id, destino, estado, tiempo_estimado, lat, lng))
        conn.commit()

def consultar_rutas_por_pedido(pedido_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, destino, estado, tiempo_estimado, lat_actual, lng_actual
            FROM rutas WHERE pedido_id = ?
        """, (pedido_id,))
        return cursor.fetchall()

def actualizar_ruta(ruta_id, estado, lat, lng):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rutas SET estado = ?, lat_actual = ?, lng_actual = ?
            WHERE id = ?
        """, (estado, lat, lng, ruta_id))
        conn.commit()
        return cursor.rowcount > 0

def eliminar_ruta(ruta_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rutas WHERE id = ?", (ruta_id,))
        conn.commit()
        return cursor.rowcount > 0
    
def listar_rutas_no_sincronizadas():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, pedido_id, destino, estado, tiempo_estimado, lat_actual, lng_actual
            FROM rutas WHERE sincronizado = 0
        """)
        return cursor.fetchall()

init_rutas()
