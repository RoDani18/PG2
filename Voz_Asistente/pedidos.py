from asyncio.log import logger
from http.client import HTTPException
import requests

import db 
import logging
logger = logging.getLogger(__name__)

# -*- coding: utf-8 -*-

BASE_URL = "http://localhost:8000"
PEDIDOS_URL = f"{BASE_URL}/pedidos"

# 📝 Crear pedido
def crear_pedido(producto: str, cantidad: int, direccion: str, token: str) -> str:
    if not direccion:
        return "❌ No se detectó la dirección. Por favor, especifica zona o ubicación."

    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "producto": producto,
            "cantidad": cantidad,
            "direccion": direccion
        }
        response = requests.post(PEDIDOS_URL, json=payload, headers=headers)

        if response.status_code == 201:
            return f"✅ Pedido de '{producto}' creado con éxito."

        elif response.status_code == 404:
            return f"⚠️ El producto '{producto}' no existe en el inventario."

        else:
            try:
                error_json = response.json()
                detalle = error_json.get("detail") or str(error_json)
            except Exception as e:
                detalle = response.text or f"Error desconocido ({e})"
            print(f"❌ Error al crear pedido: {response.status_code} - {detalle}")
            return f"❌ Error al crear pedido: {detalle}"

    except Exception as e:
        print("❌ Error al crear pedido:", e)
        return f"❌ Error al crear pedido: {str(e)}"


# 📋 Consultar pedidos del usuario autenticado
def consultar_mis_pedidos(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{PEDIDOS_URL}/mios", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return "📭 No tienes pedidos registrados."
        respuesta = "📋 Tus pedidos:\n"
        for p in pedidos:
            respuesta += (
                f"- Pedido {p['id']}: {p['producto']} ({p['cantidad']}) - {p['estado']} "
                f"- Producto ID: {p['producto_id']} - Fecha: {p['fecha']}\n"
            )
        return respuesta
    except Exception as e:
        print("❌ Error al consultar pedidos:", e)
        return "No pude consultar tus pedidos."


# 📋 Consultar todos los pedidos (empleado/admin)
def consultar_todos_pedidos(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(PEDIDOS_URL, headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return "📭 No hay pedidos registrados."
        respuesta = "📋 Pedidos registrados:\n"
        for p in pedidos:
            respuesta += f"- {p['producto']}: {p['cantidad']} unidades ({p['estado']}) - Producto ID: {p['producto_id']} - Fecha: {p['fecha']}\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar todos los pedidos:", e)
        return "No pude consultar los pedidos."

# 🔄 Actualizar estado de pedido
def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"estado": nuevo_estado}
        response = requests.put(f"{PEDIDOS_URL}/{pedido_id}", json=payload, headers=headers)
        if response.status_code == 200:
            return f"🔄 Pedido {pedido_id} actualizado a estado '{nuevo_estado}'."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al actualizar pedido:", e)
        return "Error al actualizar pedido."
    


# 🗑️ Eliminar pedido
def eliminar_pedido(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{PEDIDOS_URL}/{pedido_id}", headers=headers)
        if response.status_code == 204:
            return f"🗑️ Pedido {pedido_id} eliminado correctamente."
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para eliminar este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al eliminar pedido:", e)
        return "Error al eliminar pedido."

def ver_pedido_por_id(pedido_id: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{PEDIDOS_URL}/{pedido_id}", headers=headers)
        if response.status_code == 200:
            p = response.json()
            return f"""📦 Pedido {p['id']}:
- Producto: {p['producto']}
- Producto ID: {p['producto_id']}
- Cantidad: {p['cantidad']}
- Estado: {p['estado']}
- Fecha: {p['fecha']}
- Usuario ID: {p['usuario_id']}"""
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para ver este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al consultar pedido por ID:", e)
        return "Error al consultar pedido."


def modificar_pedido_cliente(pedido_id: int, nueva_cantidad: int, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"cantidad": nueva_cantidad}
        response = requests.put(f"{PEDIDOS_URL}/cliente/{pedido_id}", json=payload, headers=headers)
        if response.status_code == 200:
            return f"✏️ Pedido {pedido_id} actualizado a {nueva_cantidad} unidades."
        elif response.status_code == 400:
            return "⚠️ Solo puedes modificar pedidos que están pendientes."
        elif response.status_code == 403:
            return "⚠️ No tienes permiso para modificar este pedido."
        elif response.status_code == 404:
            return f"⚠️ Pedido {pedido_id} no encontrado."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        print("❌ Error al modificar pedido:", e)
        return "Error al modificar pedido."


def ver_movimientos_inventario(token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/movimientos", headers=headers)
        response.raise_for_status()
        movimientos = response.json()
        if not movimientos:
            return "📭 No hay movimientos registrados."
        respuesta = "📊 Movimientos de inventario:\n"
        for m in movimientos:
            respuesta += f"- Producto ID {m['producto_id']}: {m['tipo']} de {m['cantidad']} unidades (Pedido {m['pedido_id']})\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar movimientos:", e)
        return "No pude consultar los movimientos."
    
def ver_pedido(token: str) -> str:
    return consultar_mis_pedidos(token)

def consultar_pedidos_por_cliente(cliente_id: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/pedidos/cliente/{cliente_id}", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return f"📭 El cliente {cliente_id} no tiene pedidos registrados."
        respuesta = f"📋 Pedidos del cliente {cliente_id}:\n"
        for p in pedidos:
            respuesta += (
                f"- Pedido {p['id']}: {p['producto']} ({p['cantidad']}) - {p['estado']} "
                f"- Producto ID: {p['producto_id']} - Fecha: {p['fecha']}\n"
            )
        return respuesta
    except Exception as e:
        print("❌ Error al consultar pedidos por cliente:", e)
        return "Error al consultar pedidos por cliente."


def ver_historial_pedidos(cliente_id: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/pedidos/historial/{cliente_id}", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return f"📭 El cliente {cliente_id} no tiene historial de pedidos."
        respuesta = f"📋 Historial de pedidos del cliente {cliente_id}:\n"
        for p in pedidos:
            respuesta += (
                f"- Pedido {p['id']}: {p['producto']} ({p['cantidad']}) - {p['estado']} "
                f"- Fecha: {p['fecha']} - Producto ID: {p['producto_id']}\n"
            )
        return respuesta
    except Exception as e:
        print("❌ Error al consultar historial de pedidos:", e)
        return "Error al consultar historial de pedidos."


def generar_reporte_historial(cliente_id: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/pedidos/historial/{cliente_id}", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return f"📭 El cliente {cliente_id} no tiene historial de pedidos."

        # Simulación de generación de archivo (PDF, CSV, etc.)
        # Aquí podrías guardar en disco, enviar por correo, o devolver un enlace
        print(f"📄 Generando reporte para cliente {cliente_id} con {len(pedidos)} pedidos...")

        return f"📄 Reporte de historial de pedidos del cliente {cliente_id} generado correctamente."
    except Exception as e:
        print("❌ Error al generar reporte de historial:", e)
        return "Error al generar reporte de historial."

def generar_reporte_global(periodo: str, token: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/pedidos/reporte?periodo={periodo}", headers=headers)
        response.raise_for_status()
        pedidos = response.json()
        if not pedidos:
            return f"📭 No hay pedidos registrados en el periodo '{periodo}'."

        print(f"📄 Generando reporte global de pedidos para el periodo '{periodo}' con {len(pedidos)} registros...")

        return f"📄 Reporte global de pedidos para el periodo '{periodo}' generado correctamente."
    except Exception as e:
        print("❌ Error al generar reporte global:", e)
        return "Error al generar reporte global."
def ver_reporte_pedidos(periodo: str, token: str) -> str:
    return generar_reporte_global(periodo, token)   

def modificar_pedido(pedido_id: int, nueva_cantidad: int, token: str) -> str:
    return modificar_pedido_cliente(pedido_id, nueva_cantidad, token)

