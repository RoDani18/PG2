import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
RUTAS_URL = f"{BASE_URL}/rutas"

# 🔐 Autenticación
def autenticar(email, password):
    try:
        resp = requests.post(LOGIN_URL, json={"email": email, "password": password})
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        print("❌ Error al autenticar:", e)
        return None

# ➕ Asignar ruta
def asignar_ruta(pedido_id, destino, tiempo_estimado, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "pedido_id": pedido_id,
        "destino": destino,
        "tiempo_estimado": tiempo_estimado
    }
    resp = requests.post(RUTAS_URL, json=payload, headers=headers)
    if resp.status_code == 201:
        ruta = resp.json()
        print(f"✅ Ruta asignada: ID {ruta['id']} → {ruta['destino']} ({ruta['tiempo_estimado']})")
        return ruta["id"]
    else:
        print(f"❌ Error al asignar ruta: {resp.status_code} - {resp.text}")
        return None

# 🔄 Actualizar ruta
def actualizar_ruta(ruta_id, estado, tiempo_estimado, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "estado": estado,
        "tiempo_estimado": tiempo_estimado
    }
    resp = requests.put(f"{RUTAS_URL}/{ruta_id}/posicion", json=payload, headers=headers)
    if resp.status_code == 200:
        print(f"🔄 Ruta {ruta_id} actualizada a '{estado}' con tiempo '{tiempo_estimado}'")
    else:
        print(f"❌ Error al actualizar ruta: {resp.status_code} - {resp.text}")

# 👁️ Seguimiento por cliente
def seguimiento_cliente(ruta_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{RUTAS_URL}/{ruta_id}/seguimiento", headers=headers)
    if resp.status_code == 200:
        r = resp.json()
        print(f"🧭 Tu pedido viene por {r['destino']} y llegará en {r['tiempo_estimado']}.")
    else:
        print(f"❌ Error al consultar seguimiento: {resp.status_code} - {resp.text}")

# 🗑️ Cancelar ruta
def cancelar_ruta(ruta_id, token):
    actualizar_ruta(ruta_id, estado="cancelado", tiempo_estimado="0 minutos", token=token)

# 🚀 Flujo completo
def flujo_rutas():
    print("\n🔐 Autenticando empleado...")
    token_empleado = autenticar("empleado@tienda.com", "123456")
    if not token_empleado:
        return

    print("\n➕ Asignando ruta al pedido 205...")
    ruta_id = asignar_ruta(205, "Zona 10", "25 minutos", token_empleado)
    if not ruta_id:
        return

    print("\n🔄 Actualizando ruta a 'en_ruta' con nuevo tiempo...")
    actualizar_ruta(ruta_id, "en_ruta", "20 minutos", token_empleado)

    print("\n🔐 Autenticando cliente...")
    token_cliente = autenticar("cliente@tienda.com", "123456")
    if not token_cliente:
        return

    print("\n👁️ Cliente consulta seguimiento de su pedido...")
    seguimiento_cliente(ruta_id, token_cliente)

    print("\n🗑️ Empleado cancela la ruta...")
    cancelar_ruta(ruta_id, token_empleado)

    print("\n👁️ Cliente consulta seguimiento tras cancelación...")
    seguimiento_cliente(ruta_id, token_cliente)

# 🧪 Ejecutar prueba
if __name__ == "__main__":
    flujo_rutas()
