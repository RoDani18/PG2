# tests/test_api_ia.py
import pytest
from fastapi.testclient import TestClient
from ia.main import app  # Asegúrate que esta ruta sea correcta

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "mensaje" in r.json()

def test_intencion_simple():
    payload = {"texto": "quiero una coca", "usuario": "tester"}
    r = client.post("/intencion", json=payload)
    assert r.status_code == 200
    data = r.json()
    print("🔍 Respuesta IA:", data)

    assert "intencion" in data
    assert "confianza" in data
    assert "entidades" in data
    assert isinstance(data["entidades"], dict)
    assert "nombre" in data["entidades"]

    # Validación flexible para evitar fallo si el modelo aún no reconoce bien
    nombre_detectado = data["entidades"].get("nombre")
    assert nombre_detectado is not None, "⚠️ No se detectó la entidad 'nombre'"
    assert "coca" in nombre_detectado.lower(), f"⚠️ Se esperaba 'coca', pero se obtuvo: {nombre_detectado}"

def test_reentrenar():
    r = client.post("/reentrenar")
    assert r.status_code == 200
    assert "mensaje" in r.json()
