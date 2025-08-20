from fastapi import APIRouter
from backend.offline import fallback

router = APIRouter()

@router.get("/offline/inventario")
def obtener_inventario_local():
    """
    Devuelve el inventario guardado en SQLite (modo offline).
    """
    inventario = fallback.consultar_inventario()
    return {"inventario": inventario}
