from voz import hablar, escuchar
import requests
import rutas
import time
import sys

ENDPOINT_IA = "http://localhost:9000/ia/probar-ia"  # Ajustá el puerto si usás otro

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

def ejecutar_accion(intencion, entidades):
    if intencion == "asignar_ruta":
        pedido_id = entidades.get("pedido_id") or input("📝 ID del pedido: ")
        direccion = entidades.get("direccion") or input("📍 Dirección de entrega: ")
        exito = rutas.asignar_ruta(pedido_id, direccion)
        return "Ruta asignada correctamente." if exito else "No se pudo asignar la ruta."

    elif intencion == "listar_rutas":
        lista = rutas.obtener_rutas()
        return f"Hay {len(lista)} rutas registradas." if lista else "No hay rutas disponibles."

    elif intencion == "salir":
        hablar("Hasta pronto.")
        sys.exit()

    return f"No tengo una acción definida para la intención: {intencion}"

def ciclo_asistente():
    hablar("Hola Dani, estoy listo para ayudarte.")
    while True:
        entrada = escuchar()
        if not entrada:
            continue

        intencion, entidades = consultar_ia(entrada)
        if intencion:
            respuesta = ejecutar_accion(intencion, entidades)
            hablar(respuesta)
        else:
            hablar("No entendí bien, ¿podés repetirlo?")

if __name__ == "__main__":
    ciclo_asistente()
