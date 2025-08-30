from Voz_Asistente.intencion import detectar_intencion
from Voz_Asistente.entidades import extraer_entidades
from Voz_Asistente.acciones import ejecutar_accion
from Voz_Asistente.logger import guardar_log

def probar_voxia_simulado():
    usuario = input("🧑 Ingresá tu nombre para simular el registro: ").strip()
    if not usuario:
        print("⚠️ Nombre vacío. Cerrando VOXIA.")
        return

    print(f"📋 Registrando usuario: {usuario}")
    ejecutar_accion("registrar_usuario", {}, usuario)

    while True:
        texto = input("\n🗣️ Escribí lo que dirías al asistente (o 'salir' para terminar): ").strip()
        if not texto:
            print("⚠️ No se ingresó texto.")
            continue

        if texto.lower() == "salir":
            print("👋 Cerrando VOXIA. ¡Hasta luego!")
            break

        try:
            intencion, confianza = detectar_intencion(texto)
            if confianza is None:
                confianza = 0.0
            print(f"🔍 Intención detectada: {intencion} (confianza: {confianza:.2f})")
        except Exception as e:
            print(f"❌ Error al detectar intención: {e}")
            continue

        if confianza < 0.6:
            print("🤷 No se entendió bien. Intención poco confiable.")
            continue

        try:
            entidades = extraer_entidades(texto)
            print(f"📦 Entidades extraídas: {entidades}")
        except Exception as e:
            print(f"❌ Error al extraer entidades: {e}")
            entidades = {}

        try:
            respuesta = ejecutar_accion(intencion, entidades, usuario)
            print(f"🗣️ VOXIA responde: {respuesta}")
        except Exception as e:
            print(f"❌ Error al ejecutar acción: {e}")
            respuesta = "Lo siento, ocurrió un error interno."

        guardar_log(texto, intencion, respuesta)
