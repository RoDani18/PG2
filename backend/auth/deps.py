from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Generator

from backend.database.connection import SessionLocal
from backend.crud import crud_usuario  # ✅ nuevo import
from backend.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud_usuario.get_usuario_by_email(db, email=email)  # ✅ uso de CRUD
    if not user or not user.is_active:
        raise credentials_exception
    return user

def require_roles(*roles: str):
    def checker(current_user = Depends(get_current_user)):
        if roles and current_user.rol not in roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user
    return checker
