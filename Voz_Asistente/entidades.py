import requests

def extraer_entidades(texto):
    try:
        response = requests.post("http://localhost:8000/entidades", json={"texto": texto})
        if response.status_code == 200:
            return response.json().get("entidades", {})
        else:
            return {}
    except Exception as e:
        print("❌ Error al extraer entidades:", e)
        return {}
