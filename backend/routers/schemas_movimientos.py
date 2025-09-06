from pydantic import BaseModel
from datetime import datetime

class MovimientoResponse(BaseModel):
    id: int
    producto_id: int
    tipo: str
    cantidad: int
    fecha: datetime
    pedido_id: int | None

    class Config:
        orm_mode = True
