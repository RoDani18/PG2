from db.conexion import conectar

def crear_pedido(cliente, producto, cantidad):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pedidos (cliente, producto, cantidad, estado)
            VALUES (%s, %s, %s, 'pendiente')
        """, (cliente, producto, cantidad))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al crear pedido:", e)
        return False

def obtener_pedidos():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, cliente, producto, cantidad, estado FROM pedidos")
        pedidos = cur.fetchall()
        cur.close()
        conn.close()
        return pedidos
    except Exception as e:
        print("❌ Error al obtener pedidos:", e)
        return []

def actualizar_estado_pedido(pedido_id, nuevo_estado):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al actualizar pedido:", e)
        return False

def eliminar_pedido(pedido_id):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar pedido:", e)
        return False
