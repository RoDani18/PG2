# backend/routers/ia.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.connection import SessionLocal
from backend.config import settings
from backend import models
from ia.modelos.utils import predecir_intencion, recargar_modelo
from ia.modelos.reentrenar_desde_bd import reentrenar
from backend.routers.usuarios import require_roles, get_current_user  

router = APIRouter(prefix="/ia", tags=["IA"])

TAU_LOW = settings.TAU_LOW
TAU_HIGH = settings.TAU_HIGH

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TextoIn(BaseModel):
    texto: str = Field(..., min_length=1, max_length=500)

class PrediccionOut(BaseModel):
    intencion: str
    confianza: float
    interaccion_id: int
    pedir_confirmacion: bool

class FeedbackIn(BaseModel):
    interaccion_id: int
    intent_final: Optional[str] = None
    accion: str = Field(..., pattern="^(confirmar|corregir|descartar)$")

@router.post("/predecir", response_model=PrediccionOut)
def predecir(texto_in: TextoIn, 
            db: Session = Depends(get_db),
            user: models.Usuario = Depends(get_current_user)):
    intent, conf = predecir_intencion(texto_in.texto)

    if conf >= TAU_HIGH:
        estado = "auto"
        intent_final = intent
        pedir_confirm = False
    else:
        estado = "pendiente"
        intent_final = None
        pedir_confirm = True if conf >= TAU_LOW else True  # pide confirmación

    inter = models.Interaccion(
        user_id=user.id if user else None,
        texto=texto_in.texto,
        intent_predicha=intent,
        confianza=conf,
        intent_final=intent_final,
        estado=estado
    )
    db.add(inter)
    db.commit()
    db.refresh(inter)

    return PrediccionOut(
        intencion=intent, confianza=conf, interaccion_id=inter.id,
        pedir_confirmacion=pedir_confirm
    )

@router.post("/feedback", status_code=204)
def feedback(data: FeedbackIn,
            db: Session = Depends(get_db),
            _: models.Usuario = Depends(require_roles("admin","empleado","cliente"))):
    inter = db.query(models.Interaccion).filter_by(id=data.interaccion_id).first()
    if not inter:
        raise HTTPException(404, "Interacción no encontrada")

    if data.accion == "confirmar":
        inter.estado = "confirmada"
        if not inter.intent_final:
            inter.intent_final = inter.intent_predicha
    elif data.accion == "corregir":
        if not data.intent_final:
            raise HTTPException(400, "Falta intent_final para corrección")
        inter.intent_final = data.intent_final
        inter.estado = "corregida"
    elif data.accion == "descartar":
        inter.estado = "descartada"

    db.commit()
    return

@router.post("/reentrenar", status_code=202)
def reentrenar_modelo(_: models.Usuario = Depends(require_roles("admin"))):
    # Entrena y recarga en caliente (bloqueante en esta versión simple)
    reentrenar()
    recargar_modelo()
    return {"mensaje": "Modelo reentrenado y recargado"}
