from datetime import datetime, timedelta
from typing import Optional, List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

from backend.database.connection import get_db
from backend import models

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

SECRET_KEY = os.getenv("SECRET_KEY", "change_me_in_env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject, "iat": int(datetime.utcnow().timestamp())}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

RoleType = Annotated[str, Field(pattern="^(admin|empleado|cliente)$")]
PasswordType = Annotated[str, Field(min_length=8, max_length=128)]

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(alias="rol")
    is_active: bool

    model_config = {
    "from_attributes": True,
    "populate_by_name": True
}


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: EmailStr
    full_name: Optional[Annotated[str, Field(max_length=100)]] = None
    role: RoleType = "cliente"
    password: PasswordType

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[Annotated[str, Field(max_length=100)]] = None
    role: Optional[RoleType] = None
    password: Optional[PasswordType] = None
    is_active: Optional[bool] = None

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(UserOut):
    pass

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Usuario).filter(models.Usuario.email == subject).first()
    if not user or not user.is_active:
        raise credentials_exception
    
    return user

def require_roles(*roles: str):
    def checker(current_user: models.Usuario = Depends(get_current_user)):
        if roles and current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user
    return checker

@router.get("/", response_model=List[UserOut], summary="Listar usuarios (admin)")
def listar_usuarios(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin")),
    q: Optional[str] = Query(None, description="Buscar por username, nombre o correo"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    query = db.query(models.Usuario)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Usuario.username.ilike(like)) |
            (models.Usuario.full_name.ilike(like)) |
            (models.Usuario.email.ilike(like))
        )
    usuarios = query.order_by(models.Usuario.id.desc()).offset(offset).limit(limit).all()
    return usuarios

@router.get("/me", response_model=MeOut, summary="Perfil del usuario autenticado")
def obtener_perfil(current_user: models.Usuario = Depends(get_current_user)):
    return current_user

@router.get("/{usuario_id}", response_model=UserOut, summary="Detalle de usuario (admin o dueño)")
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    user = db.query(models.Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    if current_user.role != "admin" and current_user.id != user.id:
        raise HTTPException(403, "Permisos insuficientes")
    return user

@router.post("/", response_model=UserOut, status_code=201, summary="Crear usuario (admin)")
def crear_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin")),
):
    if db.query(models.Usuario).filter(
        (models.Usuario.username == payload.username) | (models.Usuario.email == payload.email)
    ).first():
        raise HTTPException(400, "Username o email ya en uso")

    user = models.Usuario(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Conflicto de unicidad")
    db.refresh(user)
    return user

@router.patch("/{usuario_id}", response_model=UserOut, summary="Actualizar usuario (admin o dueño)")
def actualizar_usuario(
    usuario_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    user = db.query(models.Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    if current_user.role != "admin" and current_user.id != user.id:
        raise HTTPException(403, "Permisos insuficientes")

    if payload.email and payload.email != user.email:
        if db.query(models.Usuario).filter(models.Usuario.email == payload.email).first():
            raise HTTPException(400, "Email ya en uso")
        user.email = payload.email

    if payload.full_name is not None:
        user.full_name = payload.full_name

    if payload.password:
        user.hashed_password = get_password_hash(payload.password)

    if payload.role:
        if current_user.role != "admin":
            raise HTTPException(403, "Solo admin puede cambiar rol")
        user.role = payload.role

    if payload.is_active is not None:
        if current_user.role != "admin":
            raise HTTPException(403, "Solo admin puede activar/desactivar usuarios")
        user.is_active = payload.is_active

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{usuario_id}", status_code=204, summary="Eliminar usuario (admin)")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin")),
):
    user = db.query(models.Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    db.delete(user)
    db.commit()
    return

@router.patch("/{usuario_id}/activar", response_model=UserOut, summary="Activar usuario (admin)")
def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin")),
):
    user = db.query(models.Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{usuario_id}/desactivar", response_model=UserOut, summary="Desactivar usuario (admin)")
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin")),
):
    user = db.query(models.Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
