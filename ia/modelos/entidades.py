import re

from Voz_Asistente import entidades

ARTICULOS_INVALIDOS = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

NUMEROS = {
    "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
    "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
    "quince": "15", "veinte": "20", "treinta": "30", "cuarenta": "40",
    "cincuenta": "50", "setenta": "70", "ochenta": "80", "noventa": "90"
}

PALABRAS_DIRECCION = {
    "zona", "calle", "colonia", "avenida", "bulevar", "manzana",
    "lote", "sector", "residencial", "pasaje", "barrio", "cantón", "aldea"
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
# 🧠 Alias para frases mal dichas
    texto = texto.replace("producto detallado", "pedido detallado")
    # 🧠 Convertir números escritos a dígitos
    for palabra, digito in NUMEROS.items():
        texto = texto.replace(f"pedido {palabra}", f"pedido {digito}")
        texto = texto.replace(f"número {palabra}", f"número {digito}")

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
        # Evitar capturar frases como "estado del pedido"
        if nombre and not re.search(r"estado\s+del\s+pedido", nombre):
            entidades["nombre"] = nombre    


    # 🧾 Cliente
    cliente = re.search(r"(?:cliente|para|de parte de)\s+([\w\s]+)", texto)
    if cliente:
        valor = cliente.group(1).strip().lower()
        if not any(palabra in valor for palabra in PALABRAS_DIRECCION):
            entidades["cliente"] = limpiar_entidad(valor)

    direccion_match = re.search(r"(?:para|en|hacia|entregar en)\s+(zona\s*\d+|[\w\s]+)", texto)
    if direccion_match:
        valor = direccion_match.group(1).strip().lower()
        if any(p in valor for p in PALABRAS_DIRECCION) or "zona" in valor:
            entidades["direccion"] = valor


    # 🆔 Pedido ID
    pedido_id = re.search(r"pedido\s+(\d+)", texto)
    if pedido_id:
        entidades["pedido_id"] = int(pedido_id.group(1))
        
    

    # 🚚 Ruta I# 🧠 Patrón robusto para nombre y cantidad en frases tipo "crear pedido arroz dos unidades"
    pedido_match = re.search(r"(?:crear\s+pedido(?:\s+de)?|agregar\s+pedido(?:\s+de)?|pedido\s+de)\s+([\w\s]+?)\s+(\d+|\w+)\s+(?:unidades|bolsas|sacos)?", texto)
    if pedido_match:
        nombre = limpiar_entidad(pedido_match.group(1))
        cantidad = convertir_numero(pedido_match.group(2))
        if nombre:
            entidades["nombre"] = nombre
            if cantidad and cantidad.isdigit():
                entidades["cantidad"] = cantidad

    # 📦 Estado
    estado = re.search(r"(pendiente|en camino|entregado|cancelado)", texto)
    if estado:
        entidades["estado"] = estado.group(1)
        
    # 🧠 Intención inferida por patrón de pedido
    if "nombre" in entidades and "cantidad" in entidades and "direccion" in entidades:
        entidades["intencion_forzada"] = "agregar_pedido"

                # 🧠 Actualizar estado del pedido
    if re.search(r"(actualizar|cambiar)\s+estado\s+del\s+pedido\s+\d+", texto):
        entidades["intencion_forzada"] = "actualizar_estado_pedido"
        match = re.search(r"pedido\s+(\d+)", texto)
        if "estado del pedido" not in texto and nombre_match:
            nombre = limpiar_entidad(nombre_match.group(1))
            
            if nombre:
                entidades["nombre"] = nombre

        if match:
            entidades["pedido_id"] = int(match.group(1))
        estado_match = re.search(r"(?:a\s+)?(pendiente|en camino|entregado|cancelado)", texto)
        if estado_match:
            entidades["estado"] = estado_match.group(1)

    # 🧠 Eliminar pedido
    if re.search(r"(eliminar|borrar|cancelar)\s+(el\s+)?pedido(\s+número)?\s+\d+", texto):
        entidades["intencion_forzada"] = "eliminar_pedido"
        if entidades.get("intencion_forzada") == "eliminar_pedido":
            entidades.pop("nombre", None)
        match = re.search(r"pedido\s+(número\s+)?(\d+)", texto)
        if match:
            entidades["pedido_id"] = int(match.group(2))


 # 🧠 Editar pedido
    if re.search(r"(editar|modificar|actualizar)\s+pedido\s+\d+", texto):
        entidades["intencion_forzada"] = "editar_pedido"

    # 🆔 ID del pedido
    match = re.search(r"pedido\s+(\d+)", texto)
    if match:
        entidades["pedido_id"] = int(match.group(1))

# 🔢 Cantidad
    if entidades.get("intencion_forzada") == "editar_pedido":
        cantidad_match = re.search(r"(?:cantidad\s+(?:a\s+)?|cambiar\s+cantidad\s+a\s+)(\d+)", texto)
    if cantidad_match:
        entidades["cantidad"] = cantidad_match.group(1)

    # 🛒 Producto
    producto_match = re.search(r"(?:producto|nombre)\s+(?:a\s+)?([\w\s]+)", texto)
    if producto_match:
        producto = limpiar_entidad(producto_match.group(1))
        if producto:
            entidades["producto"] = producto

    # 📍 Dirección
    direccion_match = re.search(r"(?:dirección|entregar en)\s+(?:a\s+)?([\w\s]+)", texto)
    if direccion_match:
        direccion = direccion_match.group(1).strip().lower()
        if any(p in direccion for p in PALABRAS_DIRECCION) or "zona" in direccion:
            entidades["direccion"] = direccion

    # 🧼 Evitar captura errónea de nombre
    nombre = entidades.get("nombre")
    if nombre and re.search(r"estado\s+del\s+pedido", nombre):
        entidades.pop("nombre", None)


    # 🧠 Ver pedido detallado
    if re.search(r"(ver|consultar|mostrar)\s+pedido\s+detallado\s+\d+", texto):
        entidades["intencion_forzada"] = "ver_pedido_detallado"
        match = re.search(r"pedido\s+detallado\s+(\d+)", texto)
        if match:
            entidades["pedido_id"] = int(match.group(1))
            
    # 🧠 Patrón alternativo: "ver pedido 12 detallado"
    if re.search(r"(ver|consultar|mostrar)\s+pedido\s+(\d+)\s+detallado", texto):
        entidades["intencion_forzada"] = "ver_pedido_detallado"
        entidades["pedido_id"] = int(re.search(r"pedido\s+(\d+)", texto).group(1))

    # 🧠 Consultar pedidos por cliente
    if re.search(r"(ver|consultar)\s+pedidos\s+del\s+cliente\s+\d+", texto):
        entidades["intencion_forzada"] = "consultar_pedidos_por_cliente"
        match = re.search(r"cliente\s+(\d+)", texto)
        if match:
            entidades["cliente_id"] = match.group(1)

    # 🧠 Ver historial de pedidos
    if re.search(r"(ver|consultar)\s+historial\s+de\s+pedidos\s+del\s+cliente\s+\d+", texto):
        entidades["intencion_forzada"] = "ver_historial_pedidos"
        match = re.search(r"cliente\s+(\d+)", texto)
        if match:
            entidades["cliente_id"] = match.group(1)

    # 🧠 Descargar historial de pedidos
    if re.search(r"(descargar|generar)\s+historial\s+de\s+pedidos\s+del\s+cliente\s+\d+", texto):
        entidades["intencion_forzada"] = "descargar_historial_pedidos"
        match = re.search(r"cliente\s+(\d+)", texto)
        if match:
            entidades["cliente_id"] = match.group(1)

    # 🧠 Descargar reportes globales
    if re.search(r"(descargar|generar)\s+reporte\s+global(es)?", texto):
        entidades["intencion_forzada"] = "descargar_reportes_globales"
        periodo_match = re.search(r"(último mes|última semana|hoy|ayer|este año)", texto)
        if periodo_match:
            entidades["periodo"] = periodo_match.group(1)

# 🧠 Consultar pedidos por nombre de cliente
    if re.search(r"(ver|consultar)\s+pedidos\s+de\s+([\w\s]+)", texto):
        entidades["intencion_forzada"] = "consultar_pedidos_por_nombre"
        nombre_match = re.search(r"pedidos\s+de\s+([\w\s]+)", texto)
        if nombre_match:
            nombre = limpiar_entidad(nombre_match.group(1))
            if nombre:
                entidades["cliente_nombre"] = nombre

# 🧠 Ver historial por nombre
    if re.search(r"(ver|consultar)\s+historial\s+de\s+pedidos\s+de\s+([\w\s]+)", texto):
        entidades["intencion_forzada"] = "ver_historial_por_nombre"
        nombre_match = re.search(r"pedidos\s+de\s+([\w\s]+)", texto)
        if nombre_match:
            nombre = limpiar_entidad(nombre_match.group(1))
            if nombre:
                entidades["cliente_nombre"] = nombre

    # 🧠 Intención forzada (por contexto)
    if "mostrar inventario" in texto or "ver productos" in texto:
        entidades["intencion_forzada"] = "mostrar_inventario"
    if "listar pedidos" in texto or "ver pedidos" in texto:
        entidades["intencion_forzada"] = "listar_pedidos"
    if "listar rutas" in texto or "ver entregas" in texto:
        entidades["intencion_forzada"] = "listar_rutas"
    # 🧠 Intención robusta para crear pedido
    if ("crear pedido" in texto or "agregar pedido" in texto or "pedido de" in texto) and "nombre" in entidades and "cantidad" in entidades:
        entidades["intencion_forzada"] = "agregar_pedido"
        # 🧠 Intención contextual para ver historial
    if "ver historial de pedidos" in texto or "consultar historial" in texto:
        entidades["intencion_forzada"] = "ver_historial_pedidos"
    # 🧠 Intención contextual para actualizar estado
    if "actualizar estado" in texto or "cambiar estado" in texto:
        entidades["intencion_forzada"] = "actualizar_estado_pedido"

    # 🧠 Intención contextual para modificar pedido
    if "actualizar pedido" in texto or "modificar pedido" in texto:
        entidades["intencion_forzada"] = "editar_pedido"

    # 🧠 Intención contextual para descargar historial
    if "descargar historial de pedidos" in texto or "generar historial" in texto:
        entidades["intencion_forzada"] = "descargar_historial_pedidos"

    # 🧠 Intención contextual para ver movimientos
    if "ver movimientos" in texto or "consultar inventario" in texto or "ver entradas y salidas" in texto:
        entidades["intencion_forzada"] = "ver_movimientos_inventario"

    # 🧠 Intención contextual para ver pedido detallado
    if "ver pedido detallado" in texto or "consultar pedido completo" in texto:
        entidades["intencion_forzada"] = "ver_pedido_detallado"

    # 🧠 Intención contextual para consultar pedidos por cliente
    if "ver pedidos del cliente" in texto or "consultar pedidos del cliente" in texto:
        entidades["intencion_forzada"] = "consultar_pedidos_por_cliente"

    # 🧠 Intención contextual para descargar reportes globales
    if "descargar reportes globales" in texto or "generar reporte global" in texto:
        entidades["intencion_forzada"] = "descargar_reportes_globales"


    return entidades
