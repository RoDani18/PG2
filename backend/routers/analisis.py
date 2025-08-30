# backend/routers/analisis.py
from fastapi import APIRouter, HTTPException
from backend.ia_client import detectar_intencion

router = APIRouter()

@router.post("/analizar")
def analizar_texto(payload: dict):
    resultado = detectar_intencion(payload["texto"])
    if "error" in resultado:
        raise HTTPException(status_code=502, detail=resultado["error"])
    return resultado
