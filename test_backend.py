import requests

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/auth/login"
EMAIL = "dani@correo.com"  # según tu base de datos
PASSWORD = "123456"  # debe ir como string

def login():
    print("🔐 Iniciando sesión...")
    response = requests.post(f"{BASE_URL}{LOGIN_ENDPOINT}", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login exitoso.")
        return token
    else:
        print("❌ Error en login:", response.text)
        return None

def test_endpoint(endpoint, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    print(f"📡 GET {endpoint} → {response.status_code}")
    if response.status_code == 200:
        print("✅ OK:", response.json())
    else:
        print("❌ Error:", response.text)

if __name__ == "__main__":
    token = login()
    if token:
        endpoints = [
            "/usuarios/me",
            "/inventarios/",
            "/pedidos/mios",
            "/rutas/",
            "/offline/inventario"
        ]
        for ep in endpoints:
            test_endpoint(ep, token)
