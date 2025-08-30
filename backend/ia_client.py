import httpx
import logging

IA_API_URL = "http://localhost:9000"  # Puerto donde corre la API de IA

logger = logging.getLogger(__name__)

def detectar_intencion(texto: str) -> dict:
    try:
        response = httpx.post(f"{IA_API_URL}/intencion", json={"texto": texto}, timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error de conexión con la IA: {e}")
        return {"error": "No se pudo conectar con el servicio de IA"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP desde la IA: {e.response.status_code} - {e.response.text}")
        return {"error": "La IA respondió con un error"}
