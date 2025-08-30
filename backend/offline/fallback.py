import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "offline_sqlite.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                sincronizado INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def guardar_producto(nombre, cantidad, precio):
    # Ejemplo con SQLite local
    conn = sqlite3.connect("offline.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventario (nombre, cantidad, precio)
        VALUES (?, ?, ?)
        ON CONFLICT(nombre) DO UPDATE SET
            cantidad = cantidad + ?,
            precio = ?
    """, (nombre, cantidad, precio, cantidad, precio))
    conn.commit()
    cur.close()
    conn.close()
    print("💾 Guardado offline en SQLite.")


def buscar_producto(nombre: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cantidad FROM productos WHERE nombre = ? ORDER BY id DESC LIMIT 1", (nombre,))
        row = cursor.fetchone()
        return row[0] if row else None

def actualizar_producto(nombre: str, cantidad: int, precio: float):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET cantidad = ?, precio = ? WHERE nombre = ?", (cantidad, precio, nombre))
        conn.commit()
        return cursor.rowcount > 0

def eliminar_producto(nombre: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
        conn.commit()
        return cursor.rowcount > 0

def consultar_inventario():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, SUM(cantidad) FROM productos GROUP BY nombre")
        rows = cursor.fetchall()
        return {nombre: cantidad for nombre, cantidad in rows}

def listar_productos_no_sincronizados():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, cantidad FROM productos WHERE sincronizado = 0")
        return cursor.fetchall()

def marcar_como_sincronizado(ids):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany("UPDATE productos SET sincronizado = 1 WHERE id = ?", [(i,) for i in ids])
        conn.commit()

# Inicializar la base al importar
init_db()
