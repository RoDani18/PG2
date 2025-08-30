from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models import FraseEntrenamiento

router = APIRouter()

@router.get("/")
def test_intencion():
    return {"mensaje": "Endpoint de intención activo"}

@router.post("/")
async def detectar_intencion(request: Request, db: Session = Depends(get_db)):
    datos = await request.json()
    texto = datos.get("texto", "").lower()

    # Buscar coincidencia exacta o parcial
    frase = db.query(FraseEntrenamiento).filter(
        FraseEntrenamiento.frase.ilike(f"%{texto}%")
    ).first()

    if frase:
        return {"intencion": frase.intencion}
    else:
        return {"intencion": "desconocida"}
