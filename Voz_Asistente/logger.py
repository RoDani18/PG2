import requests
from datetime import datetime

def guardar_log(frase, intencion, respuesta, confianza):
    try:
        payload = {
            "frase": frase,
            "fecha": datetime.now().isoformat(),
            "confianza": confianza,
            "interaccion_sugerida": respuesta
        }
        response = requests.post("http://localhost:8000/interacciones", json=payload)
        if response.status_code == 200:
            print("📝 Interacción registrada en la base.")
        else:
            print("⚠️ No se pudo registrar la interacción.")
    except Exception as e:
        print("❌ Error al registrar interacción:", e)
