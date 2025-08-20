from pydantic import BaseModel, Field, confloat
from typing import Optional, Annotated

# Validación para estado con regex (Pydantic v2)
EstadoRutaType = Annotated[str, Field(pattern="^(en_ruta|retrasado|entregado)$")]

# Validación para coordenadas
LatType = Annotated[float, Field(ge=-90, le=90)]
LngType = Annotated[float, Field(ge=-180, le=180)]

class RutaBase(BaseModel):
    pedido_id: int
    destino: str = Field(..., min_length=1)

class RutaCreate(RutaBase):
    lat_actual: Optional[LatType] = None
    lng_actual: Optional[LngType] = None
    tiempo_estimado: Optional[str] = None

class RutaUpdate(BaseModel):
    lat_actual: Optional[LatType] = None
    lng_actual: Optional[LngType] = None
    estado: Optional[EstadoRutaType] = None
    tiempo_estimado: Optional[str] = None

class RutaResponse(RutaBase):
    id: int
    lat_actual: Optional[float]
    lng_actual: Optional[float]
    estado: str
    tiempo_estimado: Optional[str]

    model_config = {"from_attributes": True}
