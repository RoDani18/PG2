from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import models
from backend.auth.deps import get_db, require_roles, get_current_user
from backend.routers.schemas_pedidos import PedidoCreate, PedidoUpdate, PedidoResponse
import logging

router = APIRouter()

@router.get("/", response_model=List[PedidoResponse])
def listar_todos(
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    return db.query(models.Pedido).all()

@router.get("/mios", response_model=List[PedidoResponse])
def listar_mios(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Pedido).filter(models.Pedido.usuario_id == user.id).all()

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido_in: PedidoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("cliente", "empleado", "admin"))
):
    # ✅ Validar que el producto exista
    producto = db.query(models.Producto).filter_by(nombre=pedido_in.producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 📝 Crear el pedido si el producto existe
    pedido = models.Pedido(
        usuario_id=user.id,
        producto=pedido_in.producto,
        cantidad=pedido_in.cantidad,
        estado="pendiente"
    )
    db.add(pedido)
    try:
        db.commit()
        db.refresh(pedido)
    except Exception:
        db.rollback()
        raise
    return pedido


@router.put("/{pedido_id}", response_model=PedidoResponse)
def actualizar_pedido(
    pedido_id: int,
    pedido_upd: PedidoUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    for field, value in pedido_upd.dict(exclude_unset=True).items():
        setattr(ped, field, value)

    try:
        db.commit()
        db.refresh(ped)
    except Exception:
        db.rollback()
        raise
    return ped

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("cliente", "empleado", "admin"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if user.rol == "cliente" and ped.usuario_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes eliminar pedidos de otro usuario")

    db.delete(ped)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return None


