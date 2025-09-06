import re

ARTICULOS_INVALIDOS = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

NUMEROS = {
    "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
    "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
    "quince": "15", "veinte": "20", "treinta": "30", "cuarenta": "40",
    "cincuenta": "50", "setenta": "70", "ochenta": "80", "noventa": "90"
}

def convertir_numero(valor):
    if not valor:
        return None
    valor = valor.lower()
    return NUMEROS.get(valor, valor)

def limpiar_entidad(valor):
    if not valor:
        return None
    valor = valor.strip().lower()
    return None if valor in ARTICULOS_INVALIDOS else valor

def extraer_entidades(texto):
    texto = texto.lower()
    entidades = {}

    # 🧮 Cantidad
    cantidad_match = re.search(r"(?:cantidad\s*[:=]?\s*|agrega\s*|actualiza\s*|añade\s*|modifica\s*)?(\d+|\w+)\s+(?:unidades|bolsas|sacos|bultos)?", texto)
    if cantidad_match:
        cantidad = convertir_numero(cantidad_match.group(1))
        if cantidad and cantidad.isdigit():
            entidades["cantidad"] = cantidad
            
        # 🧮 Cantidad alternativa: "actualiza X a 80 unidades"
    actualiza_match = re.search(r"(?:actualiza|modifica|cambia)\s+(?:las\s+)?(?:bolsas|sacos|bultos|unidades)?\s+de\s+([\w\s]+)\s+(?:a\s+)?(\d+)", texto)
    if actualiza_match:
        nombre = limpiar_entidad(actualiza_match.group(1))
        cantidad = actualiza_match.group(2)
        if nombre:
            entidades["nombre"] = nombre
            if cantidad.isdigit():
                entidades["cantidad"] = cantidad

    # 🧮 Patrón flexible: "agrega 20 pepsis"
    flex_match = re.search(r"(?:agrega|añade|registra|inserta)\s+(\d+)\s+([\w\s]+)", texto)
    if flex_match:
        cantidad = flex_match.group(1)
        nombre = limpiar_entidad(flex_match.group(2))
        if cantidad.isdigit():
            entidades["cantidad"] = cantidad
            if nombre:
                entidades["nombre"] = nombre
                
    # 🧮 "actualiza las pepsis a 80 unidades"
    actualiza_cantidad = re.search(r"(?:actualiza|modifica|cambia)\s+(?:las\s+)?([\w\s]+)\s+(?:a\s+)?(\d+)\s+(?:unidades)?", texto)
    if actualiza_cantidad:
        nombre = limpiar_entidad(actualiza_cantidad.group(1))
        cantidad = actualiza_cantidad.group(2)
        if nombre:
            entidades["nombre"] = nombre
            if cantidad.isdigit():
                entidades["cantidad"] = cantidad

    # 💰 "actualiza el precio de pepsis a 5"
    actualiza_precio = re.search(
    r"(?:actualiza|modifica|cambia)\s+(?:el\s+)?precio\s+(?:de\s+)?(?:las\s+)?(?:bolsas\s+de\s+)?([\w\s]+)\s+(?:a\s+)?(\d+(\.\d+)?)",
    texto)
    if actualiza_precio:
        nombre = limpiar_entidad(actualiza_precio.group(1))
        precio = float(actualiza_precio.group(2))
        if nombre:
            entidades["nombre"] = nombre
            entidades["precio"] = precio

    # 💰 Precio
    precio_match = re.search(r"(?:precio\s*[:=]?\s*)(\d+(\.\d+)?)", texto)
    if precio_match:
        entidades["precio"] = float(precio_match.group(1))

    # 🧱 Nombre del producto (más flexible)
    nombre_match = re.search(r"(?:agrega|actualiza|añade|modifica)?\s*(?:\d+|\w+)?\s*(?:unidades|bolsas|sacos|bultos)?\s*(?:de\s+)?([\w\s]+?)(?:\s+(?:al|en|con|a|para|precio|cantidad)|$)", texto)
    if nombre_match:
        nombre = limpiar_entidad(nombre_match.group(1))
        if nombre:
            entidades["nombre"] = nombre

    # 🧾 Cliente
    cliente = re.search(r"(?:cliente|para|de parte de)\s+([\w\s]+)", texto)
    if cliente:
        entidades["cliente"] = limpiar_entidad(cliente.group(1))

    # 📍 Dirección
    direccion = re.search(r"(?:zona|dirección|entregar en)\s+([\w\s\d]+)", texto)
    if direccion:
        entidades["direccion"] = direccion.group(1).strip()

    # 🆔 Pedido ID
    pedido_id = re.search(r"pedido\s+(\d+)", texto)
    if pedido_id:
        entidades["pedido_id"] = int(pedido_id.group(1))

    # 📦 Estado
    estado = re.search(r"(pendiente|en camino|entregado|cancelado)", texto)
    if estado:
        entidades["estado"] = estado.group(1)

    # 🧠 Intención forzada (por contexto)
    if "mostrar inventario" in texto or "ver productos" in texto:
        entidades["intencion_forzada"] = "mostrar_inventario"
    if "listar pedidos" in texto or "ver pedidos" in texto:
        entidades["intencion_forzada"] = "listar_pedidos"
    if "listar rutas" in texto or "ver entregas" in texto:
        entidades["intencion_forzada"] = "listar_rutas"

    return entidades
