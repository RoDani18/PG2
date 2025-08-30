from Voz_Asistente.acciones import ejecutar_accion
from ia.modelos.entidades import extraer_entidades
from Voz_Asistente.voz import hablar
import time

def simular_comando(texto):
    hablar(f"Tú dijiste: {texto}")
    entidades = extraer_entidades(texto)
    intencion = entidades.get("intencion_forzada", "desconocida")
    respuesta = ejecutar_accion(intencion, entidades)
    hablar(respuesta)
    time.sleep(1)

def test_conversacion_completa():
    # 1. Agregar producto
    r1 = ejecutar_accion("agregar_producto", {"nombre": "Pepsi", "cantidad": 20, "precio":8})
    assert "Pepsi agregado" in r1.lower()

    # 2. Consultar producto
    r2 = ejecutar_accion("consultar_producto", {"nombre": "Pepsi"})
    assert "20" in r2.lower()

    # 3. Actualizar producto
    r3 = ejecutar_accion("actualizar_producto", {"nombre": "Pepsi", "cantidad": 15})
    assert "15" in r3.lower()

    # 4. Eliminar producto
    r4 = ejecutar_accion("eliminar_producto", {"nombre": "Pepsi"})
    assert "eliminado" in r4.lower()

    # 5. Agregar pedido
    pedido = {
        "cliente": "Juan Pérez",
        "productos": [{"nombre": "frijol", "cantidad": 5}],
        "fecha": "2025-08-22"
    }
    r5 = ejecutar_accion("agregar_pedido", pedido)
    assert "pedido registrado" in r5.lower() or "pedido agregado" in r5.lower()

    # 6. Agregar ruta
    ruta = {
        "origen": "Bodega Central",
        "destino": "Zona 10",
        "distancia_km": 12.5,
        "tiempo_estimado_min": 25
    }
    r6 = ejecutar_accion("agregar_ruta", ruta)
    assert "ruta creada" in r6.lower() or "ruta registrada" in r6.lower()

if __name__ == "__main__":
    test_conversacion_completa()
