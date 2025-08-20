from fastapi import APIRouter, Depends, HTTPException
from auth.utils import require_roles
from backend.offline import fallback
from pydantic import BaseModel

router = APIRouter(prefix="/offline/inventario", tags=["Inventario Offline"])

class ProductoOffline(BaseModel):
    nombre: str
    cantidad: int

# Agregar producto
@router.post("/agregar", dependencies=[Depends(require_roles("empleado"))])
def agregar_producto(producto: ProductoOffline):
    fallback.guardar_producto(producto.nombre, producto.cantidad)
    return {"mensaje": f"Producto '{producto.nombre}' agregado con cantidad {producto.cantidad}"}

# Consultar inventario
@router.get("/consultar", dependencies=[Depends(require_roles("empleado"))])
def consultar_inventario():
    return fallback.consultar_inventario()

# Actualizar producto
@router.put("/actualizar", dependencies=[Depends(require_roles("empleado"))])
def actualizar_producto(producto: ProductoOffline):
    actualizado = fallback.actualizar_producto(producto.nombre, producto.cantidad)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": f"Producto '{producto.nombre}' actualizado a cantidad {producto.cantidad}"}

# Eliminar producto
@router.delete("/eliminar/{nombre}", dependencies=[Depends(require_roles("empleado"))])
def eliminar_producto(nombre: str):
    eliminado = fallback.eliminar_producto(nombre)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": f"Producto '{nombre}' eliminado"}
