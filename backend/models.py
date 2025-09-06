from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, Text
from backend.database.connection import Base
from typing import List
import datetime


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    rol: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")
    interacciones: Mapped[List["Interaccion"]] = relationship("Interaccion", back_populates="usuario")

class Producto(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)  # sugerido
    cantidad = Column(Integer, nullable=False, default=0)
    precio = Column(Float, nullable=False)

class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    producto: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    estado: Mapped[str] = mapped_column(String(50), default="pendiente")
    producto_id: Mapped[int] = mapped_column(ForeignKey("inventario.id"), nullable=False)
    fecha: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="pedidos")
    rutas: Mapped[List["Ruta"]] = relationship("Ruta", back_populates="pedido", cascade="all, delete-orphan")

class Ruta(Base):
    __tablename__ = "rutas"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    destino: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), default="en_ruta")
    tiempo_estimado: Mapped[str] = mapped_column(String(50))
    lat_actual: Mapped[float] = mapped_column(nullable=True)
    lng_actual: Mapped[float] = mapped_column(nullable=True)

    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="rutas")

class Interaccion(Base):
    __tablename__ = "interacciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    texto = Column(String(500), nullable=False)
    intent_predicha = Column(String(100), nullable=True)
    confianza = Column(Float, nullable=True)
    intent_final = Column(String(100), nullable=True)
    estado = Column(String(20), nullable=False, default="pendiente")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("Usuario", back_populates="interacciones")

class FraseEntrenamiento(Base):
    __tablename__ = "frases_entrenamiento"

    id = Column(Integer, primary_key=True, index=True)
    frase = Column(Text)
    intencion = Column(Text)
    fuente = Column(Text)
    
class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("inventario.id"))
    tipo = Column(String)  # "entrada" o "salida"
    cantidad = Column(Integer)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
