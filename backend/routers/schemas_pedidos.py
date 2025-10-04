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
