from sqlalchemy.orm import Session
from backend.models import Producto
from typing import Optional, List

def get_producto_by_id(db: Session, producto_id: int) -> Optional[Producto]:
    return db.query(Producto).filter(Producto.id == producto_id).first()

def get_producto_by_nombre(db: Session, nombre: str) -> Optional[Producto]:
    return db.query(Producto).filter(Producto.nombre == nombre).first()

def get_all_productos(db: Session) -> List[Producto]:
    return db.query(Producto).all()

def crear_producto(db: Session, nombre: str, cantidad: int, precio: float) -> Producto:
    producto = Producto(nombre=nombre, cantidad=cantidad, precio=precio)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto

def actualizar_producto(db: Session, producto_id: int, update_data) -> Optional[Producto]:
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        return None
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(producto, field, value)
    db.commit()
    db.refresh(producto)
    return producto

def actualizar_stock(db: Session, nombre: str, cantidad: int) -> bool:
    producto = get_producto_by_nombre(db, nombre)
    if producto:
        producto.cantidad = cantidad
        db.commit()
        return True
    return False

def eliminar_producto(db: Session, producto_id: int) -> Optional[Producto]:
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        return None
    db.delete(producto)
    db.commit()
    return producto
