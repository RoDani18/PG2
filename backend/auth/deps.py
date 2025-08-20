from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Generator

from backend.database.connection import SessionLocal
from backend import models
from backend.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

def require_roles(*roles):
    def wrapper(user: models.Usuario = Depends(get_current_user)):
        if user.rol not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user
    return wrapper
