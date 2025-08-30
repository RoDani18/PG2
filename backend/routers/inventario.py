from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import models
from backend.auth.deps import get_db, require_roles
from backend.routers.schemas_inventario import (
    ProductoCreate, ProductoUpdate, ProductoResponse
)
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    db: Session = Depends(get_db),
    #user=Depends(require_roles("empleado", "admin", "cliente"))
):
    return db.query(models.Producto).all()

@router.get("/{nombre}", response_model=ProductoResponse)
def obtener_producto(
    nombre: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin", "cliente"))
):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def agregar_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    if db.query(models.Producto).filter(models.Producto.nombre == data.nombre).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Producto ya existe")

    producto = models.Producto(**data.dict())
    db.add(producto)
    try:
        db.commit()
        db.refresh(producto)
    except Exception:
        db.rollback()
        raise
    return producto

@router.put("/{nombre}", response_model=ProductoResponse)
def actualizar_producto(
    nombre: str,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(producto, k, v)

    try:
        db.commit()
        db.refresh(producto)
    except Exception:
        db.rollback()
        raise
    return producto

@router.delete("/{nombre}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    nombre: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    db.delete(producto)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return None
    

