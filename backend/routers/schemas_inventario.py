from pydantic import BaseModel, Field, condecimal
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    cantidad: int = Field(..., ge=0)
    precio: condecimal(max_digits=10, decimal_places=2) = Field(..., ge=0)

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, ge=0)
    precio: Optional[condecimal(max_digits=10, decimal_places=2)] = Field(None, ge=0)

class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True  # ✅ compatible con Pydantic v2

