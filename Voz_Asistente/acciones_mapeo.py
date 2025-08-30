# Voz_Asistente/acciones_mapeo.py
from Voz_Asistente.acciones import (
    accion_crear_pedido,
    accion_asignar_ruta,
    accion_agregar_producto,
    accion_consultar_producto,
    accion_actualizar_producto,
    accion_eliminar_producto,
    accion_saludo,
    accion_despedida,
    accion_desconocida,
    accion_mostrar_inventario,
    accion_listar_pedidos,
    accion_listar_rutas
)

acciones = {
    "crear_pedido": accion_crear_pedido,
    "agregar_pedido": accion_crear_pedido,
    "asignar_ruta": accion_asignar_ruta,
    "agregar_ruta": accion_asignar_ruta,
    "agregar_producto": accion_agregar_producto,
    "consultar_producto": accion_consultar_producto,
    "actualizar_producto": accion_actualizar_producto,
    "eliminar_producto": accion_eliminar_producto,
    "saludo": accion_saludo,
    "despedida": accion_despedida,
    "desconocida": accion_desconocida,
    "mostrar_inventario": accion_mostrar_inventario,
    "listar_pedidos": accion_listar_pedidos,
    "listar_rutas": accion_listar_rutas
}
