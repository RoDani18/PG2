import requests
import openrouteservice

BASE_URL = "http://localhost:8000"
RUTAS_URL = f"{BASE_URL}/rutas"

# 📍 Consultar todas las rutas (empleado/admin)
def consultar_rutas(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(RUTAS_URL, headers=headers)
        response.raise_for_status()
        rutas = response.json()
        if not rutas:
            return "📭 No hay rutas registradas."
        respuesta = "📍 Rutas activas:\n"
        for r in rutas:
            respuesta += f"- Pedido {r['pedido_id']}: {r['destino']} ({r['estado']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar rutas:", e)
        return "No pude consultar las rutas."

def calcular_ruta_gps(origen, destino):
    client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM0YWVkNWE2MmY3MDQ3NzI5OGZlYWE4ZWU2ZTVkNGQ2IiwiaCI6Im11cm11cjY0In0=")
    coords = [origen, destino]
    ruta = client.directions(coords, profile='driving-car', format='geojson')

    resumen = ruta['features'][0]['properties']['summary']
    distancia = resumen['distance'] / 1000
    duracion = resumen['duration'] / 60

    # Extraer coordenadas paso a paso
    pasos = ruta['features'][0]['geometry']['coordinates']  # [[lng, lat], [lng, lat], ...]

    # Convertir a formato Leaflet: [[lat, lng], [lat, lng], ...]
    ruta_formateada = [[p[1], p[0]] for p in pasos]

    return distancia, duracion, ruta_formateada


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

def asignar_ruta_por_direccion(direccion: str, token: str) -> str:
    origen = [-90.5, 14.6]  # Ejemplo: ubicación del centro de distribución
    destino_coords = obtener_coordenadas(direccion)
    if not destino_coords:
        return "❌ No se pudo obtener coordenadas del destino."

    resumen = calcular_ruta_gps(origen, destino_coords)
    return f"🚚 {resumen} | Destino: {direccion}"


# 🌍 Geocodificación inversa con OpenStreetMap
def obtener_direccion_desde_gps(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=16&addressdetails=1"
        headers = {"User-Agent": "RutaAsistente/1.0"}
        response = requests.get(url, headers=headers)
        data = response.json()
        direccion = data.get("display_name", "ubicación desconocida")
        return direccion
    except Exception as e:
        print("❌ Error al obtener dirección:", e)
        return "ubicación desconocida"

# 🗣️ Resumen conversacional de ruta por pedido
def resumen_ruta_pedido(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/rutas/pedido/{pedido_id}", headers=headers)
        response.raise_for_status()
        rutas = response.json()
        if not rutas:
            return f"📭 No hay rutas asignadas al pedido {pedido_id}."

        # Tomamos la última ruta activa (puede ajustarse según lógica real)
        ruta = rutas[-1]
        destino = ruta.get("destino", "desconocido")
        estado = ruta.get("estado", "sin estado")
        tiempo = ruta.get("tiempo_estimado", "desconocido")
        lat = ruta.get("lat_actual")
        lng = ruta.get("lng_actual")

        # Validación defensiva
        if lat is None or lng is None:
            ubicacion = "ubicación no disponible"
        else:
            ubicacion = obtener_direccion_desde_gps(lat, lng)

        return (
            f"📍 El repartidor va por {ubicacion}.\n"
            f"🗺️ Destino final: {destino} | Estado: {estado} | Tiempo estimado: {tiempo}"
        )
    except Exception as e:
        print("❌ Error al generar resumen de ruta:", e)
        return "No pude generar el resumen de la ruta."


# ➕ Asignar ruta a pedido (empleado/admin)
def asignar_ruta(pedido_id: int, destino: str, tiempo_estimado: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "pedido_id": pedido_id,
            "destino": destino,
            "tiempo_estimado": tiempo_estimado
        }
        response = requests.post(RUTAS_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ Ruta asignada al pedido {pedido_id} hacia {destino}."
        elif response.status_code == 404:
            return "⚠️ Pedido no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al asignar ruta:", e)
        return "Error al asignar ruta."

# 🔄 Actualizar ruta (empleado/admin)
def actualizar_ruta(ruta_id: int, destino: str = None, estado: str = None, tiempo_estimado: str = None, token: str = "") -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        if destino: payload["destino"] = destino
        if estado: payload["estado"] = estado
        if tiempo_estimado: payload["tiempo_estimado"] = tiempo_estimado

        response = requests.put(f"{RUTAS_URL}/{ruta_id}/posicion", json=payload, headers=headers)
        if response.status_code == 200:
            return f"🔄 Ruta {ruta_id} actualizada correctamente."
        elif response.status_code == 404:
            return f"⚠️ Ruta {ruta_id} no encontrada."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al actualizar ruta:", e)
        return "Error al actualizar ruta."

# 👁️ Seguimiento de ruta (cliente)
def seguimiento_ruta_cliente(ruta_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{RUTAS_URL}/{ruta_id}/seguimiento", headers=headers)
        if response.status_code == 200:
            r = response.json()
            return f"🧭 Tu pedido viene por {r['destino']} y llegará en {r['tiempo_estimado']}."
        elif response.status_code == 404:
            return "⚠️ Ruta no encontrada."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al consultar seguimiento:", e)
        return "No pude consultar la ruta de tu pedido."

# 📦 Ver rutas por pedido (todos los roles)
def rutas_por_pedido(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{RUTAS_URL}/pedido/{pedido_id}", headers=headers)
        response.raise_for_status()
        rutas = response.json()
        if not rutas:
            return f"📭 No hay rutas asignadas al pedido {pedido_id}."
        respuesta = f"📦 Rutas para el pedido {pedido_id}:\n"
        for r in rutas:
            respuesta += f"- Destino: {r['destino']} | Estado: {r['estado']} | Tiempo estimado: {r['tiempo_estimado']}\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar rutas por pedido:", e)
        return "No pude consultar las rutas de ese pedido."

def cancelar_ruta(ruta_id: int, token: str) -> str:
    return actualizar_ruta(ruta_id, estado="cancelado", token=token)

