from pydantic import BaseModel
from typing import Optional

# 🆕 Crear ruta
class RutaCreate(BaseModel):
    pedido_id: int
    destino: str
    tiempo_estimado: str

# 🔄 Actualizar posición GPS o estado
class RutaUpdate(BaseModel):
    lat_actual: Optional[float] = None
    lng_actual: Optional[float] = None
    estado: Optional[str] = None
    tiempo_estimado: Optional[str] = None
    destino: Optional[str] = None

# 📦 Respuesta completa
class RutaResponse(BaseModel):
    id: int
    pedido_id: int
    destino: str
    estado: str
    tiempo_estimado: str
    lat_actual: Optional[float]
    lng_actual: Optional[float]

    class Config:
        orm_mode = True

# 🔁 Reprogramar ruta
class RutaReprogramar(BaseModel):
    nuevo_destino: str
    nuevo_tiempo: str
