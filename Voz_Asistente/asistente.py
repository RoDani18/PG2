from voz import hablar, escuchar
from inventario import autenticar_usuario
import requests
import rutas
import pedidos
import inventario
import time
import sys

ENDPOINT_IA = "http://localhost:9000/ia/probar-ia"

def consultar_ia(texto_usuario, usuario="anonimo"):
    try:
        payload = {"texto": texto_usuario, "usuario": usuario}
        respuesta = requests.post(ENDPOINT_IA, json=payload)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            intencion = datos.get("intencion", "")
            entidades = datos.get("entidades", {})
            confianza = datos.get("confianza", 0)
            print(f"🧠 Intención: {intencion} ({confianza:.2f}) | Entidades: {entidades}")
            return intencion, entidades
        else:
            print(f"❌ Error IA: {respuesta.status_code}")
            return None, {}
    except Exception as e:
        print("❌ Error al conectar con IA:", e)
        return None, {}

def ejecutar_accion(intencion, entidades, auth_token):
    if intencion == "asignar_ruta":
        pedido_id = entidades.get("pedido_id") or input("📝 ID del pedido: ")
        destino = entidades.get("direccion") or input("📍 Dirección de entrega: ")
        tiempo = entidades.get("tiempo_estimado") or "20 minutos"
        return rutas.asignar_ruta(pedido_id, destino, tiempo, auth_token)

    elif intencion == "consultar_rutas":
        return rutas.consultar_rutas(auth_token)

    elif intencion == "consultar_inventario":
        return inventario.consultar_inventario(auth_token)

    elif intencion == "crear_pedido":
        producto = entidades.get("producto") or input("🛒 Producto: ")
        cantidad = entidades.get("cantidad") or int(input("🔢 Cantidad: "))
        return pedidos.crear_pedido(producto, cantidad, auth_token)

    elif intencion == "consultar_pedidos":
        return pedidos.consultar_mis_pedidos(auth_token)

    elif intencion == "seguimiento_pedido":
        ruta_id = entidades.get("ruta_id") or int(input("📍 ID de la ruta: "))
        return rutas.seguimiento_ruta_cliente(ruta_id, auth_token)

    elif intencion == "salir":
        hablar("Hasta pronto.")
        sys.exit()

    return f"No tengo una acción definida para la intención: {intencion}"

def ciclo_asistente():
    email = input("📧 Tu correo: ")
    password = input("🔐 Tu contraseña: ")
    auth_token = autenticar_usuario(email, password)
    if not auth_token:
        hablar("No pude autenticarte.")
        return

    hablar("Hola Dani, estoy listo para ayudarte.")
    while True:
        entrada = escuchar()
        if not entrada:
            continue

        intencion, entidades = consultar_ia(entrada)
        if intencion:
            respuesta = ejecutar_accion(intencion, entidades, auth_token)
            hablar(respuesta)
        else:
            hablar("No entendí bien, ¿podés repetirlo?")

if __name__ == "__main__":
    ciclo_asistente()
