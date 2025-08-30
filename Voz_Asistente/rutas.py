from db.conexion import conectar

def asignar_ruta(pedido_id, direccion_entrega):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rutas (pedido_id, direccion, estado)
            VALUES (%s, %s, 'asignada')
        """, (pedido_id, direccion_entrega))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al asignar ruta:", e)
        return False

def obtener_rutas():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, pedido_id, direccion, estado FROM rutas")
        rutas = cur.fetchall()
        cur.close()
        conn.close()
        return rutas
    except Exception as e:
        print("❌ Error al obtener rutas:", e)
        return []

def actualizar_estado_ruta(ruta_id, nuevo_estado):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("UPDATE rutas SET estado = %s WHERE id = %s", (nuevo_estado, ruta_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al actualizar ruta:", e)
        return False

def eliminar_ruta(ruta_id):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM rutas WHERE id = %s", (ruta_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar ruta:", e)
        return False
