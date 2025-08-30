from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    
class UsuarioBase(BaseModel):
    email: EmailStr
    rol: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=6)

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr]
    rol: Optional[str]
    is_active: Optional[bool]

class UsuarioOut(UsuarioBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class ProductoBase(BaseModel):
    nombre: str
    cantidad: int
    precio: float

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str]
    cantidad: Optional[int]
    precio: Optional[float]

class ProductoOut(ProductoBase):
    id: int

    class Config:
        orm_mode = True
        
class PedidoBase(BaseModel):
    producto: str
    cantidad: int
    estado: str
    producto_id: int

class PedidoCreate(PedidoBase):
    usuario_id: int

class PedidoUpdate(BaseModel):
    producto: Optional[str]
    cantidad: Optional[int]
    estado: Optional[str]
    producto_id: Optional[int]

class PedidoOut(PedidoBase):
    id: int
    usuario_id: int
    fecha: datetime  

    class Config:
        orm_mode = True
        
class RutaBase(BaseModel):
    destino: str
    estado: str
    tiempo_estimado: str
    lat_actual: float
    lng_actual: float

class RutaCreate(RutaBase):
    pedido_id: int

class RutaUpdate(BaseModel):
    destino: Optional[str]
    estado: Optional[str]
    tiempo_estimado: Optional[str]
    lat_actual: Optional[float]
    lng_actual: Optional[float]

class RutaOut(RutaBase):
    id: int
    pedido_id: int

    class Config:
        orm_mode = True



