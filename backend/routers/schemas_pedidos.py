from pydantic import BaseModel, Field, constr
from typing import Optional
from decimal import Decimal
from typing import Annotated

# Estados válidos para pedidos
ESTADOS_VALIDOS = ('pendiente', 'enviado', 'entregado', 'cancelado')

class PedidoBase(BaseModel):
    producto: str = Field(..., min_length=1)
    cantidad: int = Field(..., ge=1)

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

    class Config:
        orm_mode = True
