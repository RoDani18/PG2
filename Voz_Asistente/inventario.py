import requests

def consultar_inventario():
    try:
        response = requests.get("http://localhost:8000/inventario")
        inventario = response.json()
        respuesta = "Inventario actual:\n"
        for item in inventario:
            respuesta += f"{item['nombre']}: {item['cantidad']} unidades\n"
        return respuesta
    except Exception as e:
        print("❌ Error al consultar inventario:", e)
        return "No pude consultar el inventario."

def agregar_producto(nombre, cantidad, usuario):
    try:
        response = requests.post("http://localhost:8000/inventario", json={
            "nombre": nombre,
            "cantidad": cantidad,
            "usuario": usuario
        })
        if response.status_code == 200:
            return f"Producto {nombre} agregado con éxito."
        else:
            return "No se pudo agregar el producto."
    except Exception as e:
        print("❌ Error al agregar producto:", e)
        return "Error al agregar producto."
    
def actualizar_producto(nombre, nueva_cantidad, usuario):
    try:
        response = requests.put("http://localhost:8000/inventario", json={
            "nombre": nombre,
            "cantidad": nueva_cantidad,
            "usuario": usuario
        })
        if response.status_code == 200:
            return f"Producto {nombre} actualizado a {nueva_cantidad} unidades."
        else:
            return "No se pudo actualizar el producto."
    except Exception as e:
        print("❌ Error al actualizar producto:", e)
        return "Error al actualizar producto."

def eliminar_producto(nombre, usuario):
    try:
        response = requests.delete("http://localhost:8000/inventario", json={
            "nombre": nombre,
            "usuario": usuario
        })
        if response.status_code == 200:
            return f"Producto {nombre} eliminado correctamente."
        else:
            return "No se pudo eliminar el producto."
    except Exception as e:
        print("❌ Error al eliminar producto:", e)
        return "Error al eliminar producto."

