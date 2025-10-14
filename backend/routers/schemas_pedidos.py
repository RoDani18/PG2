from pydantic import BaseModel, Field, constr
from typing import Optional
from decimal import Decimal
from typing import Annotated
from datetime import datetime
from typing import Optional




# Estados válidos para pedidos
ESTADOS_VALIDOS = ('pendiente', 'enviado', 'entregado', 'cancelado')

class PedidoBase(BaseModel):
    producto: str = Field(..., min_length=1)
    cantidad: int = Field(..., ge=1)
    direccion: str 

class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    producto: Optional[str] = Field(None, min_length=1)
    cantidad: Optional[int] = Field(None, ge=1)
    estado: Optional[Annotated[str, Field(pattern="^(pendiente|enviado|entregado|cancelado)$")]] = None

class PedidoResponse(PedidoBase):
    id: int
    usuario_id: int
    estado: str
    producto_id: int           # ✅ ID del producto en inventario
    fecha: datetime            # ✅ Fecha de creación del pedido
    
class PedidoResumen(BaseModel):
    id: int
    usuario: str
    producto: str
    cantidad: int
    estado: str
    fecha: str
    direccion: str

    class Config:
        orm_mode = True

class MovimientoInventarioResponse(BaseModel):
    id: int
    producto_id: int
    tipo: str
    cantidad: int
    fecha: datetime
    pedido_id: Optional[int]

    class Config:
        orm_mode = True

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

class PedidoConRuta(BaseModel):
    pedido: PedidoResponse
    ruta: RutaResponse
