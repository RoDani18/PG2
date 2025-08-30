from sqlalchemy.orm import Session
from backend.models import Pedido
from typing import List, Optional
import datetime

def get_pedido_by_id(db: Session, pedido_id: int) -> Optional[Pedido]:
    return db.query(Pedido).filter(Pedido.id == pedido_id).first()

def get_all_pedidos(db: Session) -> List[Pedido]:
    return db.query(Pedido).all()

def get_pedidos_por_usuario(db: Session, usuario_id: int) -> List[Pedido]:
    return db.query(Pedido).filter(Pedido.usuario_id == usuario_id).all()

def crear_pedido(db: Session, usuario_id: int, producto: str, cantidad: int, estado: str, producto_id: int) -> Pedido:
    pedido = Pedido(
        usuario_id=usuario_id,
        producto=producto,
        cantidad=cantidad,
        estado=estado,
        producto_id=producto_id,
        fecha=datetime.datetime.utcnow()
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido

def actualizar_estado_pedido(db: Session, pedido_id: int, nuevo_estado: str) -> bool:
    pedido = get_pedido_by_id(db, pedido_id)
    if pedido:
        pedido.estado = nuevo_estado
        db.commit()
        return True
    return False

def actualizar_pedido(db: Session, pedido_id: int, update_data) -> Optional[Pedido]:
    pedido = get_pedido_by_id(db, pedido_id)
    if not pedido:
        return None
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(pedido, field, value)
    db.commit()
    db.refresh(pedido)
    return pedido

def eliminar_pedido(db: Session, pedido_id: int) -> Optional[Pedido]:
    pedido = get_pedido_by_id(db, pedido_id)
    if not pedido:
        return None
    db.delete(pedido)
    db.commit()
    return pedido
