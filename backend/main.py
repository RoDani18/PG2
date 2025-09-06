import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.connection import Base, engine
from backend.routers import inventario, pedidos, rutas, usuarios, offline_routes, ia as ia_router
from backend.auth import routers as auth_routers
from backend.background import sync_loop
from backend.config import settings
from fastapi import FastAPI
from backend.routers import analisis
from backend.routers.router_usuario import router as usuario_router
from backend.routers import ia as ia_router
from backend.routers import intencion
from backend.routers import movimientos


app = FastAPI(title="Asistente Logístico API")

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas solo en desarrollo
import os
if os.getenv("ENV") == "dev":
    Base.metadata.create_all(bind=engine)

# Lanzar sincronizador en segundo plano
stop_event = threading.Event()
threading.Thread(target=sync_loop, args=(stop_event,), daemon=True).start()

# Incluir rutas
app.include_router(auth_routers.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router)
app.include_router(inventario.router, prefix="/inventarios", tags=["Inventario"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(rutas.router, prefix="/rutas", tags=["Rutas"])
app.include_router(offline_routes.router)
app.include_router(analisis.router, prefix="/ia", tags=["IA"])
app.include_router(usuario_router)
app.include_router(ia_router.router, prefix="/ia", tags=["IA"])
app.include_router(intencion.router, prefix="/intencion", tags=["Intención"])
app.include_router(movimientos.router, prefix="/movimientos", tags=["Movimientos"])


