from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.auth.schemas import LoginRequest, TokenResponse
from backend.auth.security import verify_password, create_access_token
from backend.auth.deps import get_db
from backend import models

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == credentials.email).first()
    if not usuario or not verify_password(credentials.password, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(data={"sub": usuario.email})
    return TokenResponse(access_token=token, rol=usuario.rol)

