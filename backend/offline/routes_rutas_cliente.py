from fastapi import APIRouter, Depends, HTTPException
from backend.auth.deps import require_roles
from backend.offline import rutas_fallback
from pydantic import BaseModel

router = APIRouter(prefix="/offline/rutas", tags=["Rutas Offline"])

class RutaCreate(BaseModel):
    pedido_id: int
    destino: str
    estado: str
    tiempo_estimado: str
    lat_actual: float
    lng_actual: float

class RutaUpdate(BaseModel):
    ruta_id: int
    estado: str
    lat_actual: float
    lng_actual: float

# Agregar ruta
@router.post("/agregar", dependencies=[Depends(require_roles("cliente"))])
def agregar_ruta(ruta: RutaCreate):
    rutas_fallback.agregar_ruta(
        ruta.pedido_id, ruta.destino, ruta.estado,
        ruta.tiempo_estimado, ruta.lat_actual, ruta.lng_actual
    )
    return {"mensaje": "Ruta agregada correctamente"}

# Consultar rutas por pedido
@router.get("/consultar/{pedido_id}", dependencies=[Depends(require_roles("cliente"))])
def consultar_rutas(pedido_id: int):
    rutas = rutas_fallback.consultar_rutas_por_pedido(pedido_id)
    return [{"id": r[0], "destino": r[1], "estado": r[2], "tiempo_estimado": r[3], "lat": r[4], "lng": r[5]} for r in rutas]

# Actualizar ruta
@router.put("/actualizar", dependencies=[Depends(require_roles("cliente"))])
def actualizar_ruta(data: RutaUpdate):
    actualizado = rutas_fallback.actualizar_ruta(data.ruta_id, data.estado, data.lat_actual, data.lng_actual)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"mensaje": "Ruta actualizada"}

# Eliminar ruta
@router.delete("/eliminar/{ruta_id}", dependencies=[Depends(require_roles("cliente"))])
def eliminar_ruta(ruta_id: int):
    eliminado = rutas_fallback.eliminar_ruta(ruta_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"mensaje": "Ruta eliminada"}
