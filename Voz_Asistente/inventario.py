import requests

BASE_URL = "http://localhost:8000"
INVENTARIO_URL = f"{BASE_URL}/inventarios"
LOGIN_URL = f"{BASE_URL}/auth/login"

# 🔐 Autenticación
def autenticar_usuario(email: str, password: str) -> str:
    try:
        response = requests.post(LOGIN_URL, json={
            "email": email,
            "password": password
        })
        response.raise_for_status()
        token = response.json().get("access_token")
        return token
    except Exception as e:
        print("❌ Error al autenticar:", e)
        return None

# 📦 Consultar inventario
def consultar_inventario(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(INVENTARIO_URL, headers=headers)
        response.raise_for_status()
        inventario = response.json()
        respuesta = "📦 Inventario actual:\n"
        for item in inventario:
            respuesta += f"- {item['nombre']}: {item['cantidad']} unidades\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar inventario:", e)
        return "No pude consultar el inventario."

# ➕ Agregar producto
def agregar_producto(nombre: str, cantidad: int, precio: float, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }
        response = requests.post(INVENTARIO_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ Producto '{nombre}' agregado con éxito."
        elif response.status_code == 409:
            return f"⚠️ El producto '{nombre}' ya existe."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al agregar producto:", e)
        return "Error al agregar producto."

# 🔄 Actualizar producto
def actualizar_producto(nombre: str, nueva_cantidad: int, nuevo_precio: float, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "cantidad": nueva_cantidad,
            "precio": nuevo_precio
        }
        response = requests.put(f"{INVENTARIO_URL}/{nombre}", json=payload, headers=headers)
        if response.status_code == 200:
            return f"🔄 Producto '{nombre}' actualizado correctamente."
        elif response.status_code == 404:
            return f"⚠️ Producto '{nombre}' no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al actualizar producto:", e)
        return "Error al actualizar producto."

# 🗑️ Eliminar producto
def eliminar_producto(nombre: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{INVENTARIO_URL}/{nombre}", headers=headers)
        if response.status_code == 204:
            return f"🗑️ Producto '{nombre}' eliminado correctamente."
        elif response.status_code == 404:
            return f"⚠️ Producto '{nombre}' no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al eliminar producto:", e)
        return "Error al eliminar producto."
