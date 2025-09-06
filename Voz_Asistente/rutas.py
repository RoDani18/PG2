import requests

BASE_URL = "http://localhost:8000"
RUTAS_URL = f"{BASE_URL}/rutas"

# 📍 Consultar todas las rutas (empleado/admin)
def consultar_rutas(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(RUTAS_URL, headers=headers)
        response.raise_for_status()
        rutas = response.json()
        if not rutas:
            return "📭 No hay rutas registradas."
        respuesta = "📍 Rutas activas:\n"
        for r in rutas:
            respuesta += f"- Pedido {r['pedido_id']}: {r['destino']} ({r['estado']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar rutas:", e)
        return "No pude consultar las rutas."

# ➕ Asignar ruta a pedido (empleado/admin)
def asignar_ruta(pedido_id: int, destino: str, tiempo_estimado: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "pedido_id": pedido_id,
            "destino": destino,
            "tiempo_estimado": tiempo_estimado
        }
        response = requests.post(RUTAS_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ Ruta asignada al pedido {pedido_id} hacia {destino}."
        elif response.status_code == 404:
            return "⚠️ Pedido no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al asignar ruta:", e)
        return "Error al asignar ruta."

# 🔄 Actualizar ruta (empleado/admin)
def actualizar_ruta(ruta_id: int, destino: str = None, estado: str = None, tiempo_estimado: str = None, token: str = "") -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        if destino: payload["destino"] = destino
        if estado: payload["estado"] = estado
        if tiempo_estimado: payload["tiempo_estimado"] = tiempo_estimado

        response = requests.put(f"{RUTAS_URL}/{ruta_id}/posicion", json=payload, headers=headers)
        if response.status_code == 200:
            return f"🔄 Ruta {ruta_id} actualizada correctamente."
        elif response.status_code == 404:
            return f"⚠️ Ruta {ruta_id} no encontrada."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al actualizar ruta:", e)
        return "Error al actualizar ruta."

# 👁️ Seguimiento de ruta (cliente)
def seguimiento_ruta_cliente(ruta_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{RUTAS_URL}/{ruta_id}/seguimiento", headers=headers)
        if response.status_code == 200:
            r = response.json()
            return f"🧭 Tu pedido viene por {r['destino']} y llegará en {r['tiempo_estimado']}."
        elif response.status_code == 404:
            return "⚠️ Ruta no encontrada."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al consultar seguimiento:", e)
        return "No pude consultar la ruta de tu pedido."

# 📦 Ver rutas por pedido (todos los roles)
def rutas_por_pedido(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{RUTAS_URL}/pedido/{pedido_id}", headers=headers)
        response.raise_for_status()
        rutas = response.json()
        if not rutas:
            return f"📭 No hay rutas asignadas al pedido {pedido_id}."
        respuesta = f"📦 Rutas para el pedido {pedido_id}:\n"
        for r in rutas:
            respuesta += f"- Destino: {r['destino']} | Estado: {r['estado']} | Tiempo estimado: {r['tiempo_estimado']}\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar rutas por pedido:", e)
        return "No pude consultar las rutas de ese pedido."

def cancelar_ruta(ruta_id: int, token: str) -> str:
    return actualizar_ruta(ruta_id, estado="cancelado", token=token)
