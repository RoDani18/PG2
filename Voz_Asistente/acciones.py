from Voz_Asistente.inventario import (
    agregar_producto,
    consultar_inventario,
    actualizar_producto,
    eliminar_producto
)
from Voz_Asistente.pedidos import crear_pedido
from Voz_Asistente.rutas import asignar_ruta, obtener_rutas, actualizar_estado_ruta, eliminar_ruta

# --- INVENTARIO ---
def accion_agregar_producto(entidades):
    nombre = entidades.get("producto")
    cantidad = entidades.get("cantidad", 1)
    usuario = entidades.get("usuario", "sistema")
    if nombre:
        resultado = agregar_producto(nombre, cantidad, usuario)
        return resultado
    return "No entendí qué producto agregar."

def accion_consultar_producto(entidades):
    return consultar_inventario()

def accion_actualizar_producto(entidades):
    nombre = entidades.get("producto")
    nueva_cantidad = entidades.get("cantidad")
    usuario = entidades.get("usuario", "sistema")
    if nombre and nueva_cantidad is not None:
        resultado = actualizar_producto(nombre, nueva_cantidad, usuario)
        return resultado
    return "Faltan datos para actualizar el producto."

def accion_eliminar_producto(entidades):
    nombre = entidades.get("producto")
    usuario = entidades.get("usuario", "sistema")
    if nombre:
        resultado = eliminar_producto(nombre, usuario)
        return resultado
    return "No se especificó qué producto eliminar."

def accion_mostrar_inventario(entidades):
    return consultar_inventario()

# --- PEDIDOS ---
def accion_crear_pedido(entidades):
    producto = entidades.get("producto") or entidades.get("nombre")
    direccion = entidades.get("direccion")
    cantidad = entidades.get("cantidad", 1)
    if producto and direccion:
        resultado = crear_pedido(producto, cantidad, direccion)
        return f"Pedido creado con {cantidad} unidad(es) de {producto} para {direccion}." if resultado else "No se pudo crear el pedido."
    return "Faltan datos para crear el pedido."


# --- RUTAS ---
def accion_asignar_ruta(entidades):
    pedido_id = entidades.get("pedido_id")
    direccion = entidades.get("direccion")
    if pedido_id and direccion:
        resultado = asignar_ruta(pedido_id, direccion)
        return f"Ruta asignada al pedido {pedido_id}." if resultado else "No se pudo asignar la ruta."
    return "Faltan datos para asignar la ruta."

def accion_listar_rutas(entidades):
    rutas = obtener_rutas()
    if rutas:
        respuesta = "Rutas registradas:\n"
        for r in rutas:
            respuesta += f"- Ruta {r[0]}: Pedido {r[1]}, Dirección: {r[2]}, Estado: {r[3]}\n"
        return respuesta.strip()
    return "No hay rutas registradas."

def accion_actualizar_estado_ruta(entidades):
    ruta_id = entidades.get("ruta_id")
    nuevo_estado = entidades.get("estado")
    if ruta_id and nuevo_estado:
        resultado = actualizar_estado_ruta(ruta_id, nuevo_estado)
        return f"Estado de la ruta {ruta_id} actualizado a '{nuevo_estado}'." if resultado else "No se pudo actualizar la ruta."
    return "Faltan datos para actualizar la ruta."

def accion_eliminar_ruta(entidades):
    ruta_id = entidades.get("ruta_id")
    if ruta_id:
        resultado = eliminar_ruta(ruta_id)
        return f"Ruta {ruta_id} eliminada correctamente." if resultado else "No se pudo eliminar la ruta."
    return "No se especificó qué ruta eliminar."

# --- GENÉRICAS ---
def accion_saludo(entidades):
    return "¡Hola! ¿En qué puedo ayudarte hoy?"

def accion_despedida(entidades):
    return "Hasta luego. Que tengas un excelente día."

def accion_desconocida(entidades):
    return "Lo siento, no entendí tu solicitud. ¿Podés repetirla con más detalle?"
