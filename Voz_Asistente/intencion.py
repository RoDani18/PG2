import requests

def detectar_intencion(frase):
    try:
        response = requests.post("http://localhost:8000/intencion", json={"frase": frase}, timeout=3)

        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code} al detectar intención.")
            return "intención_desconocida", 0.0

        data = response.json()

        intencion = data.get("intencion", "intención_desconocida")
        confianza = data.get("confianza", 0.0)

        if not isinstance(confianza, (float, int)):
            print("⚠️ Confianza no es numérica. Usando 0.0")
            confianza = 0.0

        return intencion, float(confianza)

    except (requests.exceptions.RequestException, Exception) as e:
        print("❌ Error de conexión al servidor de intención:", e)
        return "intención_desconocida", 0.0


    except (requests.exceptions.RequestException, ValueError, Exception) as e:
        print("❌ Error al detectar intención:", e)
        return "intención_desconocida", 0.0

