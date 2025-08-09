from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def obtener_inventario(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()

@router.post("/")
def agregar_producto(nombre: str, cantidad: int, db: Session = Depends(get_db)):
    producto = models.Producto(nombre=nombre, cantidad=cantidad)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return {"mensaje": "Producto agregado correctamente", "producto": producto}

@router.get("/{nombre}")
def buscar_producto(nombre: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if producto:
        return {"nombre": producto.nombre, "cantidad": producto.cantidad}
    return {"mensaje": "Producto no encontrado"}

@router.put("/{nombre}")
def actualizar_producto(nombre: str, cantidad: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if producto:
        producto.cantidad = cantidad
        db.commit()
        return {"mensaje": "Producto actualizado"}
    return {"mensaje": "Producto no encontrado"}

@router.delete("/{nombre}")
def eliminar_producto(nombre: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.nombre == nombre).first()
    if producto:
        db.delete(producto)
        db.commit()
        return {"mensaje": "Producto eliminado"}
    return {"mensaje": "Producto no encontrado"}
