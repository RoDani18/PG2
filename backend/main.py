from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import inventario, pedidos, rutas, usuarios
from backend.auth import auth

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asistente Logístico API")

# Incluir rutas
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(inventario.router, prefix="/inventario", tags=["Inventario"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(rutas.router, prefix="/rutas", tags=["Rutas"])
