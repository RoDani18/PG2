import httpx

BACKEND_URL = "http://localhost:8000"
IA_URL = "http://localhost:9000"

def login():
    print("🔐 Iniciando sesión...")
    r = httpx.post(f"{BACKEND_URL}/auth/login", json={
        "email": "dani@correo.com",
        "password": "123456"
    })
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("✅ Login exitoso")
        return {"Authorization": f"Bearer {token}"}
    else:
        print("❌ Login fallido:", r.text)
        return {}

def probar_backend(headers):
    print("📡 Probando backend...")

    r1 = httpx.get(f"{BACKEND_URL}/usuarios/me", headers=headers)
    print(f"✅ /usuarios/me: {r1.status_code}")

    r2 = httpx.get(f"{BACKEND_URL}/inventarios/", headers=headers)
    print(f"✅ /inventarios/: {r2.status_code}")

    r3 = httpx.get(f"{BACKEND_URL}/pedidos/mios", headers=headers)
    print(f"✅ /pedidos/mios: {r3.status_code}")

def probar_ia_directa():
    print("\n🧠 Probando IA directamente...")
    texto = "Quiero 3 unidades del producto 3 para el cliente Juan"
    r = httpx.post(f"{IA_URL}/intencion", json={"texto": texto})
    print(f"✅ /intencion: {r.status_code}")
    print("🧠 Respuesta IA:", r.json())

def probar_ia_desde_backend(headers):
    print("\n🔗 Probando IA desde el backend...")
    texto = "Quiero 3 unidades del producto 3 para el cliente Juan"
    r = httpx.post(f"{BACKEND_URL}/ia/probar-ia", json={"texto": texto}, headers=headers)
    print(f"✅ /ia/probar-ia: {r.status_code}")
    print("🔗 Respuesta desde backend:", r.json())

if __name__ == "__main__":
    headers = login()
    probar_backend(headers)
    probar_ia_directa()
    probar_ia_desde_backend(headers)
