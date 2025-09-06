import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
PEDIDOS_URL = f"{BASE_URL}/pedidos"

# 🔐 Autenticación
def autenticar(email, password):
    try:
        resp = requests.post(LOGIN_URL, json={"email": email, "password": password})
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        print("❌ Error al autenticar:", e)
        return None

# 📝 Crear pedido como cliente
def crear_pedido(token, producto, cantidad):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"producto": producto, "cantidad": cantidad}
    resp = requests.post(PEDIDOS_URL, json=payload, headers=headers)
    if resp.status_code == 201:
        pedido = resp.json()
        print(f"✅ Pedido creado: {pedido['id']} - {pedido['producto']} ({pedido['cantidad']})")
        return pedido["id"]
    else:
        print(f"❌ Error al crear pedido: {resp.status_code} - {resp.text}")
        return None

# 📋 Ver pedidos del cliente
def ver_mis_pedidos(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{PEDIDOS_URL}/mios", headers=headers)
    if resp.status_code == 200:
        pedidos = resp.json()
        print("📋 Pedidos del cliente:")
        for p in pedidos:
            print(f"- ID {p['id']}: {p['producto']} ({p['cantidad']}) → Estado: {p['estado']}")
        return pedidos
    else:
        print("❌ Error al consultar pedidos:", resp.text)
        return []

# 🔄 Actualizar estado como empleado
def actualizar_estado(token, pedido_id, nuevo_estado):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"estado": nuevo_estado}
    resp = requests.put(f"{PEDIDOS_URL}/{pedido_id}", json=payload, headers=headers)
    if resp.status_code == 200:
        print(f"🔄 Pedido {pedido_id} actualizado a '{nuevo_estado}'")
    else:
        print(f"❌ Error al actualizar estado: {resp.status_code} - {resp.text}")

# 🧪 Simulación completa
def flujo_completo():
    print("\n🔐 Autenticando cliente...")
    token_cliente = autenticar("cliente1@vox.com", "123456")
    if not token_cliente:
        return

    print("\n📝 Cliente crea pedido...")
    pedido_id = crear_pedido(token_cliente, "ricitos", 3)
    if not pedido_id:
        return

    print("\n📋 Cliente consulta sus pedidos...")
    ver_mis_pedidos(token_cliente)

    print("\n🔐 Autenticando empleado...")
    token_empleado = autenticar("empleado1@vox.com", "123456")
    if not token_empleado:
        return

    print("\n🔄 Empleado actualiza estado del pedido a 'en camino'...")
    actualizar_estado(token_empleado, pedido_id, "en camino")

    print("\n📋 Cliente vuelve a consultar sus pedidos...")
    ver_mis_pedidos(token_cliente)

# 🚀 Ejecutar prueba
if __name__ == "__main__":
    flujo_completo()
