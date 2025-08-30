from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.auth.schemas import LoginRequest, TokenResponse
from backend.auth.security import verify_password, create_access_token
from backend.auth.deps import get_db
from backend.crud import crud_usuario  
import logging

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    usuario = crud_usuario.get_usuario_by_email(db, email=credentials.email)  
    if not usuario or not verify_password(credentials.password, usuario.hashed_password):
        logging.warning(f"Intento fallido de login para: {credentials.email}")  
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(data={"sub": usuario.email})
    logging.info(f"Login exitoso: {usuario.email} con rol {usuario.rol}")  
    return TokenResponse(access_token=token, rol=usuario.rol)
