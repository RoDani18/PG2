from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from Voz_Asistente.rutas import asignar_ruta, actualizar_ruta, seguimiento_ruta_cliente, rutas_por_pedido, calcular_ruta_gps,obtener_coordenadas
from backend import models
import openrouteservice
from backend.auth.deps import get_db, require_roles
from backend.routers.schemas_rutas import RutaCreate, RutaUpdate, RutaResponse
import requests
router = APIRouter()

@router.get("/", response_model=List[RutaResponse])
def listar_rutas(
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    return db.query(models.Ruta).all()

@router.get("/pedido/{pedido_id}", response_model=List[RutaResponse])
def rutas_por_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin", "cliente"))
):
    # ✅ Validar que el pedido exista
    pedido = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # 📦 Consultar rutas asociadas
    return db.query(models.Ruta).filter(models.Ruta.pedido_id == pedido_id).all()

@router.post("/", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
def crear_ruta(
    data: RutaCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    if not db.query(models.Pedido).filter_by(id=data.pedido_id).first():
        raise HTTPException(404, "Pedido no encontrado")
    ruta = models.Ruta(**data.dict(), estado="en_ruta")
    db.add(ruta)
    db.commit()
    db.refresh(ruta)
    return ruta

@router.put("/{ruta_id}/posicion", response_model=RutaResponse)
def actualizar_posicion(
    ruta_id: int,
    data: RutaUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ruta = db.query(models.Ruta).filter_by(id=ruta_id).first()
    if not ruta:
        raise HTTPException(404, "Ruta no encontrada")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(ruta, k, v)

    db.commit()
    db.refresh(ruta)
    return ruta

@router.get("/{ruta_id}/seguimiento", response_model=RutaResponse)
def seguimiento(
    ruta_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin", "cliente"))
):
    ruta = db.query(models.Ruta).filter_by(id=ruta_id).first()
    if not ruta:
        raise HTTPException(404, "Ruta no encontrada")
    return ruta


def obtener_direccion_desde_gps(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}"
        response = requests.get(url)
        data = response.json()
        direccion = data.get("display_name", "ubicación desconocida")
        return direccion
    except Exception as e:
        print("❌ Error al obtener dirección:", e)
        return "ubicación desconocida"
    
from backend.routers.schemas_rutas import RutaReprogramar

@router.put("/{ruta_id}/reprogramar")
def reprogramar_ruta(
    ruta_id: int,
    datos: RutaReprogramar,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ruta = db.query(models.Ruta).filter(models.Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if ruta.estado == "cancelada":
        raise HTTPException(status_code=400, detail="No se puede reprogramar una ruta cancelada")

    ruta.destino = datos.nuevo_destino
    ruta.tiempo_estimado = datos.nuevo_tiempo
    ruta.estado = "reprogramada"
    db.commit()
    return {"mensaje": f"Ruta {ruta_id} reprogramada correctamente"}

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM0YWVkNWE2MmY3MDQ3NzI5OGZlYWE4ZWU2ZTVkNGQ2IiwiaCI6Im11cm11cjY0In0="

class RutaGPS(BaseModel):
    pedido_id: int
    direccion: str
    origen: list[float] | None = None  # [lng, lat]

def obtener_coordenadas(direccion: str):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={direccion}, Guatemala"
    headers = {"User-Agent": "RutaAsistente/1.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return [lon, lat]
    return None

def calcular_ruta_gps(origen, destino):
    client = openrouteservice.Client(key=ORS_API_KEY)
    coords = [origen, destino]
    ruta = client.directions(coords, profile='driving-car', format='geojson')
    resumen = ruta['features'][0]['properties']['summary']
    distancia = resumen['distance'] / 1000
    duracion = resumen['duration'] / 60
    pasos = ruta['features'][0]['geometry']['coordinates']
    ruta_formateada = [[p[1], p[0]] for p in pasos]
    return distancia, duracion, ruta_formateada

@router.post("/gps")
def asignar_ruta_gps(data: RutaGPS):
    origen = data.origen or [-90.5133, 14.6099]  # Default: San Miguel Petapa
    destino_coords = obtener_coordenadas(data.direccion)
    if not destino_coords:
        return {"error": "No se pudo obtener coordenadas del destino."}

    distancia, duracion, ruta_formateada = calcular_ruta_gps(origen, destino_coords)

    return {
        "pedido_id": data.pedido_id,
        "direccion": data.direccion,
        "distancia_km": round(distancia, 1),
        "tiempo_min": round(duracion, 1),
        "lat": destino_coords[1],
        "lng": destino_coords[0],
        "ruta": ruta_formateada
    }