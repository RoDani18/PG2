from sqlalchemy.orm import Session
from backend import models
from backend.auth.security import get_password_hash

# Obtener usuario por email
def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

# Obtener usuario por ID
def get_usuario_by_id(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

# Crear nuevo usuario
def create_usuario(db: Session, usuario_data):
    hashed_password = get_password_hash(usuario_data.password)
    nuevo_usuario = models.Usuario(
        email=usuario_data.email,
        hashed_password=hashed_password,
        rol=usuario_data.rol,
        is_active=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# Actualizar usuario
def update_usuario(db: Session, usuario_id: int, update_data):
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        return None
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return usuario

# Eliminar usuario
def delete_usuario(db: Session, usuario_id: int):
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        return None
    db.delete(usuario)
    db.commit()
    return usuario
