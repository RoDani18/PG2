from db.conexion import conectar

def agregar_producto(nombre, cantidad):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO inventario (nombre, cantidad) VALUES (%s, %s)",
            (nombre, cantidad)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al guardar en base de datos:", e)
        return False
