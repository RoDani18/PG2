from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import models
from backend.auth.deps import get_db, require_roles
from backend.routers.schemas_rutas import RutaCreate, RutaUpdate, RutaResponse

router = APIRouter()

@router.get("/", response_model=List[RutaResponse])
def listar_rutas(
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    return db.query(models.Ruta).all()

@router.get("/pedido/{pedido_id}", response_model=List[RutaResponse])
def rutas_por_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin", "cliente"))
):
    # ✅ Validar que el pedido exista
    pedido = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # 📦 Consultar rutas asociadas
    return db.query(models.Ruta).filter(models.Ruta.pedido_id == pedido_id).all()

@router.post("/", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
def crear_ruta(
    data: RutaCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    if not db.query(models.Pedido).filter_by(id=data.pedido_id).first():
        raise HTTPException(404, "Pedido no encontrado")
    ruta = models.Ruta(**data.dict(), estado="en_ruta")
    db.add(ruta)
    db.commit()
    db.refresh(ruta)
    return ruta

@router.put("/{ruta_id}/posicion", response_model=RutaResponse)
def actualizar_posicion(
    ruta_id: int,
    data: RutaUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ruta = db.query(models.Ruta).filter_by(id=ruta_id).first()
    if not ruta:
        raise HTTPException(404, "Ruta no encontrada")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(ruta, k, v)

    db.commit()
    db.refresh(ruta)
    return ruta

@router.get("/{ruta_id}/seguimiento", response_model=RutaResponse)
def seguimiento(
    ruta_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin", "cliente"))
):
    ruta = db.query(models.Ruta).filter_by(id=ruta_id).first()
    if not ruta:
        raise HTTPException(404, "Ruta no encontrada")
    return ruta
