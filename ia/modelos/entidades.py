import re
import sqlite3

ARTICULOS_INVALIDOS = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

def limpiar_entidad(valor):
    if valor and valor.lower() in ARTICULOS_INVALIDOS:
        return None
    return valor

def convertir_numero(valor):
    mapa = {
        "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
        "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
        "quince": "15", "veinte": "20", "treinta": "30", "cuarenta": "40"
    }
    return mapa.get(valor.lower(), valor)

def extraer_entidades(texto):
    entidades = {}

    # Producto: permite más de una palabra antes de "precio"
    producto = re.search(r"(?:agregar|añadir|insertar|producto)?\s*([\w\s]+?)\s*(?:precio|cantidad|$)", texto)
    if producto:
        entidades["nombre"] = limpiar_entidad(producto.group(1).strip())

    # Precio
    precio = re.search(r"precio\s+(?:de\s+)?(\d+|\w+)", texto)
    if precio:
        entidades["precio"] = convertir_numero(precio.group(1))

    # Cantidad
    cantidad = re.search(r"cantidad\s+(?:de\s+)?(\d+|\w+)", texto)
    if cantidad:
        entidades["cantidad"] = convertir_numero(cantidad.group(1))

    # Cliente
    cliente = re.search(r"(?:para|de parte de)\s+(\w+)", texto)
    if cliente:
        entidades["cliente"] = limpiar_entidad(cliente.group(1))

    # Dirección
    direccion = re.search(r"(?:entregar en|dirección|zona)\s+([\w\s\d]+)", texto)
    if direccion:
        entidades["direccion"] = direccion.group(1)

    # Pedido ID
    pedido_id = re.search(r"pedido\s+(\d+)", texto)
    if pedido_id:
        entidades["pedido_id"] = int(pedido_id.group(1))

    # Estado
    estado = re.search(r"(pendiente|en camino|entregado|cancelado)", texto)
    if estado:
        entidades["estado"] = estado.group(1)

    # Intención forzada
    if "mostrar inventario" in texto or "ver productos" in texto:
        entidades["intencion_forzada"] = "mostrar_inventario"
    if "listar pedidos" in texto or "ver pedidos" in texto:
        entidades["intencion_forzada"] = "listar_pedidos"
    if "listar rutas" in texto or "ver entregas" in texto:
        entidades["intencion_forzada"] = "listar_rutas"

    return entidades
