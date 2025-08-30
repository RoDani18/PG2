# test_backend.py
import pytest
import requests

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/auth/login"
EMAIL = "dani@correo.com"
PASSWORD = "123456"

@pytest.fixture(scope="session")
def token():
    print("🔐 Iniciando sesión...")
    response = requests.post(f"{BASE_URL}{LOGIN_ENDPOINT}", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    assert response.status_code == 200, f"❌ Error en login: {response.text}"
    print("✅ Login exitoso.")
    return response.json()["access_token"]

@pytest.mark.parametrize("endpoint", [
    "/usuarios/me",
    "/inventarios/",
    "/pedidos/mios",
    "/rutas/",
    "/offline/inventario"
])
def test_endpoint(token, endpoint):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    print(f"\n📡 Probando endpoint: {url}")
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"❌ Error {response.status_code}: {response.text}"
    try:
        data = response.json()
        print("📦 Contenido:", data if data else "Sin datos")
    except Exception as e:
        pytest.fail(f"⚠️ Error al parsear JSON: {e}")
