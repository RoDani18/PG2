from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from database.connection import SessionLocal
from backend.config import SECRET_KEY, ALGORITHM
from backend.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Extraer usuario desde token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.email == email).first()
    db.close()
    if user is None:
        raise credentials_exception
    return user

# Validar roles
def require_roles(*roles):
    def role_checker(user: Usuario = Depends(get_current_user)):
        if user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado para rol '{user.rol}'"
            )
    return Depends(role_checker)
