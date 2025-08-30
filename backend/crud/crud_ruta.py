from sqlalchemy.orm import Session
from backend.models import Ruta
from typing import List, Optional

def get_ruta_by_id(db: Session, ruta_id: int) -> Optional[Ruta]:
    return db.query(Ruta).filter(Ruta.id == ruta_id).first()

def get_rutas_por_pedido(db: Session, pedido_id: int) -> List[Ruta]:
    return db.query(Ruta).filter(Ruta.pedido_id == pedido_id).all()

def get_all_rutas(db: Session) -> List[Ruta]:
    return db.query(Ruta).all()

def crear_ruta(db: Session, pedido_id: int, destino: str, estado: str, tiempo_estimado: str, lat: float, lng: float) -> Ruta:
    ruta = Ruta(
        pedido_id=pedido_id,
        destino=destino,
        estado=estado,
        tiempo_estimado=tiempo_estimado,
        lat_actual=lat,
        lng_actual=lng
    )
    db.add(ruta)
    db.commit()
    db.refresh(ruta)
    return ruta

def actualizar_ruta(db: Session, ruta_id: int, estado: str, lat: float, lng: float) -> bool:
    ruta = get_ruta_by_id(db, ruta_id)
    if ruta:
        ruta.estado = estado
        ruta.lat_actual = lat
        ruta.lng_actual = lng
        db.commit()
        return True
    return False

def update_ruta(db: Session, ruta_id: int, update_data) -> Optional[Ruta]:
    ruta = get_ruta_by_id(db, ruta_id)
    if not ruta:
        return None
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(ruta, field, value)
    db.commit()
    db.refresh(ruta)
    return ruta

def eliminar_ruta(db: Session, ruta_id: int) -> Optional[Ruta]:
    ruta = get_ruta_by_id(db, ruta_id)
    if not ruta:
        return None
    db.delete(ruta)
    db.commit()
    return ruta
