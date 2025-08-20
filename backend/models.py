from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # ← este campo debe existir
    rol = Column(String)
    is_active = Column(Boolean, default=True)
    pedidos = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")
    interacciones = relationship("Interaccion", back_populates="usuario")

class Producto(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)  # sugerido
    cantidad = Column(Integer, nullable=False, default=0)
    precio = Column(Float, nullable=False)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    producto = Column(String(100), nullable=False)
    cantidad = Column(Integer, nullable=False)
    estado = Column(String(50), nullable=False, default="pendiente")

    usuario = relationship("Usuario", back_populates="pedidos")
    rutas = relationship("Ruta", back_populates="pedido", cascade="all, delete-orphan")

class Ruta(Base):
    __tablename__ = "rutas"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    destino = Column(String(255), nullable=False)
    estado = Column(String(50), nullable=False, default="en_ruta")  # corregido
    tiempo_estimado = Column(String(50))

    pedido = relationship("Pedido", back_populates="rutas")

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

