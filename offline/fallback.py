import sqlite3

conn = sqlite3.connect("offline_sqlite.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad INTEGER)")
conn.commit()

def guardar_producto(nombre, cantidad):
    cursor.execute("INSERT INTO productos (nombre, cantidad) VALUES (?, ?)", (nombre, cantidad))
    conn.commit()
