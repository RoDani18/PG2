from fastapi import APIRouter, HTTPException
from backend.database import SessionLocal
from backend import models
from backend.auth.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    db = SessionLocal()
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario or not verify_password(password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(data={"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}
