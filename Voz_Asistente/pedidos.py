import requests

BASE_URL = "http://localhost:8000"
PEDIDOS_URL = f"{BASE_URL}/pedidos"

# 📝 Crear pedido
def crear_pedido(producto: str, cantidad: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "producto": producto,
            "cantidad": cantidad
        }
        response = requests.post(PEDIDOS_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ Pedido de '{producto}' creado con éxito."
        elif response.status_code == 404:
            return f"⚠️ El producto '{producto}' no existe en el inventario."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al crear pedido:", e)
        return "Error al crear pedido."

# 📋 Consultar pedidos del usuario autenticado
def consultar_mis_pedidos(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{PEDIDOS_URL}/mios", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return "📭 No tienes pedidos registrados."
        respuesta = "📋 Tus pedidos:\n"
        for p in pedidos:
            respuesta += f"- {p['producto']}: {p['cantidad']} unidades ({p['estado']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar pedidos:", e)
        return "No pude consultar tus pedidos."

# 📋 Consultar todos los pedidos (empleado/admin)
def consultar_todos_pedidos(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(PEDIDOS_URL, headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return "📭 No hay pedidos registrados."
        respuesta = "📋 Pedidos registrados:\n"
        for p in pedidos:
            respuesta += f"- {p['producto']}: {p['cantidad']} unidades ({p['estado']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar todos los pedidos:", e)
        return "No pude consultar los pedidos."

# 🔄 Actualizar estado de pedido
def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"estado": nuevo_estado}
        response = requests.put(f"{PEDIDOS_URL}/{pedido_id}", json=payload, headers=headers)
        if response.status_code == 200:
            return f"🔄 Pedido {pedido_id} actualizado a estado '{nuevo_estado}'."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al actualizar pedido:", e)
        return "Error al actualizar pedido."

# 🗑️ Eliminar pedido
def eliminar_pedido(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{PEDIDOS_URL}/{pedido_id}", headers=headers)
        if response.status_code == 204:
            return f"🗑️ Pedido {pedido_id} eliminado correctamente."
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para eliminar este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al eliminar pedido:", e)
        return "Error al eliminar pedido."

def ver_pedido_por_id(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{PEDIDOS_URL}/{pedido_id}", headers=headers)
        if response.status_code == 200:
            p = response.json()
            return f"📦 Pedido {p['id']}:\n- Producto: {p['producto']}\n- Cantidad: {p['cantidad']}\n- Estado: {p['estado']}\n- Usuario ID: {p['usuario_id']}"
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para ver este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al consultar pedido por ID:", e)
        return "Error al consultar pedido."

def modificar_pedido_cliente(pedido_id: int, nueva_cantidad: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"cantidad": nueva_cantidad}
        response = requests.put(f"{PEDIDOS_URL}/cliente/{pedido_id}", json=payload, headers=headers)
        if response.status_code == 200:
            return f"✏️ Pedido {pedido_id} actualizado a {nueva_cantidad} unidades."
        elif response.status_code == 400:
            return "⚠️ Solo puedes modificar pedidos que están pendientes."
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para modificar este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al modificar pedido:", e)
        return "Error al modificar pedido."


def ver_movimientos_inventario(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/movimientos", headers=headers)
        response.raise_for_status()
        movimientos = response.json()
        if not movimientos:
            return "📭 No hay movimientos registrados."
        respuesta = "📊 Movimientos de inventario:\n"
        for m in movimientos:
            respuesta += f"- Producto ID {m['producto_id']}: {m['tipo']} de {m['cantidad']} unidades (Pedido {m['pedido_id']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar movimientos:", e)
        return "No pude consultar los movimientos."
