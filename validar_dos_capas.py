import requests

# Frases de prueba
frases = [
    "Quiero saber el clima",
    "Muéstrame mi agenda",
    "¿Puedes encender las luces?",
    "Hola",
    "No entiendo nada"
]

# Usuario de prueba
usuario = "dani"

# Endpoints
URL_IA_DIRECTA = "http://localhost:8000/intencion"
URL_BACKEND = "http://localhost:9000/ia/probar-ia"

# Función para enviar frase
def enviar_frase(url, frase, usuario):
    payload = {"texto": frase, "usuario": usuario}
    try:
        response = requests.post(url, json=payload)
        print(f"🔗 {url}: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"❌ Error al conectar con {url}: {e}")
        return {}

# Validación por frase
for frase in frases:
    print(f"\n🧪 Frase: \"{frase}\"")

    data_ia = enviar_frase(URL_IA_DIRECTA, frase, usuario)
    data_backend = enviar_frase(URL_BACKEND, frase, usuario)

    intencion_ia = data_ia.get("intencion", "❌ No encontrada")
    intencion_backend = data_backend.get("intencion", "❌ No encontrada")

    print(f"🧠 IA directa: {intencion_ia}")
    print(f"🔗 Backend: {intencion_backend}")

    if intencion_ia == intencion_backend:
        print("✅ Coinciden")
    else:
        print("⚠️ Diferencia detectada")

print("\n📋 Validación completada.")
