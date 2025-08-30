from voz import escuchar, hablar, hablar_por_lineas
from Voz_Asistente.intencion import procesar_comando
from Voz_Asistente.acciones import ejecutar_accion
from registro import guardar_log
from datetime import datetime
import time

ACTIVADO = True
ultimo_texto = ""
ultimo_intencion = ""
ultimo_entidades = {}


def iniciar_asistente():
    hablar("Voxia está en espera. Decí 'Voxia' para activarla.", pausa=1)

    while True:
        try:
            texto = escuchar()

            if not texto:
                continue

            if "voxia apágate" in texto:
                hablar("Desactivando asistente. Hasta luego.")
                break

            if "voxia" in texto and not ACTIVADO:
                ACTIVADO = True
                hablar("Sí, te escucho...", pausa=1)
                continue

            if ACTIVADO:
                if texto in ["sí", "hazlo", "confirmar"] and ultimo_intencion:
                    ultimo_entidades["usuario"] = "usuario_actual"  
                    ultimo_entidades["frase"] = ultimo_texto
                    ultimo_entidades["confianza"] = 1.0  
                    ultimo_entidades["intencion_sugerida"] = ultimo_intencion
                    respuesta = ejecutar_accion(ultimo_intencion, ultimo_entidades)
                    intencion = ultimo_intencion
                else:
                    respuesta, intencion = procesar_comando(texto)
                    ultimo_texto = texto
                    ultimo_intencion = intencion
                    from ia.modelos.entidades import extraer_entidades
                    ultimo_entidades = extraer_entidades(texto)
                    ultimo_entidades["usuario"] = "usuario_actual"
                    ultimo_entidades["frase"] = texto
                    ultimo_entidades["confianza"] = 1.0
                    ultimo_entidades["intencion_sugerida"] = intencion
                    respuesta = ejecutar_accion(intencion, ultimo_entidades)

                if "\n" in respuesta:
                    hablar_por_lineas(respuesta)
                else:
                    hablar(respuesta, pausa=2)

                guardar_log(texto, intencion, respuesta)

                if intencion == "despedida":
                    hablar("Cerrando sesión. Que tengas una excelente noche.", pausa=2)
                    break

                ACTIVADO = False
                hablar("Voxia está en espera. Decí 'Voxia' para activarla.", pausa=1)

        except KeyboardInterrupt:
            hablar("Interrupción detectada. Cerrando el asistente.", pausa=2)
            break

        except Exception as e:
            print("❌ Error inesperado:", e)
            hablar("Ocurrió un error. Intentemos de nuevo.", pausa=2)
            time.sleep(1)

if __name__ == "__main__":
    iniciar_asistente()
