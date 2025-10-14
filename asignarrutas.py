import requests

# 📍 Configuración
BASE_URL = "http://localhost:8000"
RUTA_ID = 5  # Reemplazá con el ID real de la ruta
TOKEN = "tu_token_aqui"  # Reemplazá con tu token real

# 🧭 Nueva posición GPS
payload = {
    "lat_actual": 14.6123,
    "lng_actual": -90.5382
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 🚀 Actualizar posición
try:
    response = requests.put(f"{BASE_URL}/rutas/{RUTA_ID}/posicion", json=payload, headers=headers)
    if response.status_code == 200:
        print("✅ Posición actualizada correctamente.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print("❌ Error al actualizar posición:", e)
