import warnings
warnings.filterwarnings("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import queue
import json
import numpy as np
import random
import re
import sys
import requests
import time
import sounddevice as sd
import pyttsx3
import requests
import csv
from backend.offline import fallback
from vosk import Model, KaldiRecognizer
from ia.modelos.modelo_intencion import detectar_intencion
from ia.modelos.utils import limpiar_texto
from ia.modelos.utils import _ensure_loaded
from ia.modelos.utils import obtener_modelo
from ia.modelos.entidades import extraer_entidades
from datetime import datetime



# ==== RUTAS Y MODELOS ====
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
MODEL_VOSK_PATH = "vosk-model-es-0.42"
API_URL = "http://127.0.0.1:8000"
UMBRAL_CONFIANZA = 0.6
LOG_PATH = "log_asistente.txt"
with open("intenciones.json", encoding="utf-8") as archivo:
    intenciones = json.load(archivo)



# ==== MOTOR DE VOZ ====
voz = pyttsx3.init()
voz.setProperty('rate', 150)

def hablar(texto):
    print(f" {texto}")
    voz.say(texto)
    voz.say("....")
    voz.runAndWait()
    voz.say("....")
    
def iniciar_asistente(reconocedor, stream, engine, detectar_intencion):
    print("🟢 VOXIA está activa. Puedes comenzar a hablar.")

    while True:
        print("🎤 Esperando tu voz...")
        texto_usuario = None

        # Escuchar hasta obtener texto válido
        while not texto_usuario:
            data = stream.read(4000)
            if reconocedor.AcceptWaveform(data):
                resultado = json.loads(reconocedor.Result())
                texto_usuario = resultado.get("text", "").strip()
                if texto_usuario:
                    print(f">> Tú dijiste: {texto_usuario}")
                else:
                    print("⚠️ No detecto audio. ¿Puedes repetirlo?")
                    time.sleep(1.5)

        # Detectar intención
        intencion, confianza = detectar_intencion(texto_usuario)
        print(f"🔍 Intención detectada: {intencion} (confianza: {confianza:.2f})")

        # Validar confianza
        if confianza < 0.6:
            respuesta = "No entendí bien lo que dijiste. ¿Puedes repetirlo?"
        else:
            respuesta = generar_respuesta(intencion)

        # Hablar la respuesta
        print(f">> VOXIA dice: {respuesta}")
        engine.say(respuesta)
        engine.runAndWait()

        # Pequeña pausa antes de volver a escuchar
        time.sleep(2)

def generar_respuesta(intencion):
    respuestas = {
        "saludo": "Hola, ¿cómo estás?",
        "despedida": "Hasta luego, que tengas buen día.",
        "consulta": "Claro, dime qué necesitas.",
        "agradecimiento": "Con gusto, estoy para ayudarte.",
        "error": "No entendí bien, ¿puedes repetirlo?"
    }
    return respuestas.get(intencion, "No estoy seguro de cómo responder a eso.")

# ==== AUDIO ====
q = queue.Queue()
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# ==== CONVERSIÓN DE NÚMEROS ====
NUMEROS_PALABRAS = {
    "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
    "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90,
    "cien": 100
}

def convertir_numero(texto):
    try:
        return int(texto)
    except ValueError:
        return NUMEROS_PALABRAS.get(texto.lower(), None)

def agregar_producto_backend(producto):
    if not backend_activo():
        fallback.guardar_producto(producto["nombre"], producto["cantidad"])
        return f"Guardé {producto['nombre']} con {producto['cantidad']} unidades en modo offline."
    
def backend_activo():
    try:
        response = requests.get(f"{API_URL}/inventario/")
        return response.status_code == 200
    except:
        return False

def ejecutar_accion(intencion, entidades):
    try:
        if intencion == "agregar":
            nombre = entidades.get("nombre")
            cantidad = entidades.get("cantidad", 1)
            precio = entidades.get("precio", 0.0)
            if not nombre:
                return "No entendí qué producto quieres agregar."
            response = requests.post(f"{API_URL}/", params={
                "nombre": nombre,
                "cantidad": cantidad,
                "precio": precio
            })
            return response.json().get("mensaje", "Producto agregado.")

        elif intencion == "buscar":
            nombre = entidades.get("nombre")
            if not nombre:
                return "No entendí qué producto quieres buscar."
            response = requests.get(f"{API_URL}/{nombre}")
            data = response.json()
            if "mensaje" in data:
                return data["mensaje"]
            return f"{data['nombre']} tiene {data['cantidad']} unidades disponibles."

        elif intencion == "actualizar":
            nombre = entidades.get("nombre")
            cantidad = entidades.get("cantidad", 0)
            precio = entidades.get("precio", 0.0)
            if not nombre:
                return "No entendí qué producto quieres actualizar."
            response = requests.put(f"{API_URL}/{nombre}", params={
                "cantidad": cantidad,
                "precio": precio
            })
            return response.json().get("mensaje", "Producto actualizado.")

        elif intencion == "eliminar":
            nombre = entidades.get("nombre")
            if not nombre:
                return "No entendí qué producto quieres eliminar."
            response = requests.delete(f"{API_URL}/{nombre}")
            return response.json().get("mensaje", "Producto eliminado.")

        elif intencion == "salir":
            return "Saliendo del asistente..."

        else:
            return "No reconozco esa acción. Intenta de nuevo."

    except Exception as e:
        print(f"⚠️ Error en ejecutar_accion: {e}")
        return "Ocurrió un error al conectar con el sistema. Intenta más tarde."

def agregar_producto_backend(producto):
    if not backend_activo():
        return "El sistema de inventario no está disponible."
    try:
        response = requests.post(f"{API_URL}/inventario/", params={
            "nombre": producto["nombre"],
            "cantidad": producto["cantidad"]
        })
        if response.status_code == 200:
            return f"He agregado {producto['nombre']} con {producto['cantidad']} unidades."
        else:
            return "No se pudo agregar el producto."
    except:
        return "Error al conectar con el sistema de inventario."
    


def consultar_inventario_backend():
    if not backend_activo():
        return "Parece que el sistema de inventario está apagado o no disponible."
    try:
        response = requests.get(f"{API_URL}/inventario/")
        if response.status_code == 200:
            productos = response.json()
            if not productos:
                return "El inventario está vacío."
            texto = "📦 Inventario actual:\n"
            for p in productos:
                nombre = p.get("nombre", "¿?")
                cantidad = p.get("cantidad", "?")
                precio = p.get("precio", 0.00)
                texto += f"- {nombre}: {cantidad} unidades, Q{precio:.2f} cada uno\n"
            return texto.strip()
        else:
            return "Error al consultar inventario."
    except:
        return "No se pudo conectar al sistema de inventario."


def eliminar_producto_backend(nombre):
    if not backend_activo():
        return "El sistema de inventario no está disponible."
    try:
        response = requests.delete(f"{API_URL}/inventario/{nombre}")
        if response.status_code == 200:
            return f"He eliminado el producto {nombre} del inventario."
        else:
            return f"No se pudo eliminar el producto {nombre}."
    except:
        return "Error al conectar con el sistema de inventario."

def actualizar_producto_backend(nombre, cantidad):
    if not backend_activo():
        return "El sistema de inventario no está disponible."
    try:
        response = requests.put(f"{API_URL}/inventario/{nombre}", params={"cantidad": cantidad})
        if response.status_code == 200:
            return f"He actualizado {nombre} a {cantidad} unidades."
        else:
            return f"No se pudo actualizar el producto {nombre}."
    except:
        return "Error al conectar con el sistema de inventario."

def buscar_producto_backend(nombre):
    if not backend_activo():
        return "El sistema de inventario no está disponible."
    try:
        response = requests.get(f"{API_URL}/inventario/{nombre}")
        if response.status_code == 200:
            producto = response.json()
            return f"{producto['nombre']} tiene {producto['cantidad']} unidades disponibles."
        else:
            return f"No encontré el producto {nombre}."
    except:
        return "Error al conectar con el sistema de inventario."

# ==== EXTRACTORES ====

def extraer_datos_producto(texto):
    texto = texto.lower()

    # Buscar nombre del producto (palabra después de "producto" o "agregar")
    nombre_match = re.search(r"(?:agregar\s+producto\s+|producto\s+|agregar\s+)(\w+)", texto)
    nombre = nombre_match.group(1).capitalize() if nombre_match else None

    # Buscar precio (número después de "precio", "vale", "cuesta")
    precio_match = re.search(r"(?:precio|vale|cuesta)\s+(\w+)", texto)
    precio = convertir_numero(precio_match.group(1)) if precio_match else None

    # Buscar cantidad (número después de "cantidad", "unidades", "hay")
    cantidad_match = re.search(r"(?:cantidad|unidades|hay|de)\s+(\w+)", texto)
    cantidad = convertir_numero(cantidad_match.group(1)) if cantidad_match else None

    if nombre and cantidad is not None:
        return {
            "nombre": nombre,
            "precio": float(precio) if precio is not None else 0.0,
            "cantidad": int(cantidad)
        }
    return None


def extraer_nombre_y_cantidad(texto):
    nombre = re.search(r"(?:producto|nombre)?\s*(\w+)", texto)
    cantidad = re.search(r"(?:cantidad|unidades|a|actualiza)\s*(\w+)", texto)
    nombre_val = nombre.group(1).capitalize() if nombre else None
    cantidad_val = convertir_numero(cantidad.group(1)) if cantidad else None
    return nombre_val, cantidad_val

# ==== EJECUCIÓN DE INTENCIONES ====

def ejecutar_intencion(intencion, texto):
    global ultima_intencion, datos_temporales, esperando_confirmacion

    if intencion == "agregar_producto":
        datos = extraer_datos_producto(texto)
        if datos:
            datos_temporales = datos
            ultima_intencion = intencion
            esperando_confirmacion = True
            respuesta = f"¿Quieres agregar {datos['nombre']} con {datos['cantidad']} unidades?"
        else:
            respuesta = "No entendí bien el producto. Intenta decir nombre, precio y cantidad."

    elif intencion == "consultar_inventario":
        respuesta = consultar_inventario_backend()

    elif intencion == "eliminar_producto":
        nombre, _ = extraer_nombre_y_cantidad(texto)
        respuesta = eliminar_producto_backend(nombre) if nombre else "No entendí qué producto deseas eliminar."

    elif intencion == "actualizar_producto":
        nombre, cantidad = extraer_nombre_y_cantidad(texto)
        if nombre and cantidad is not None:
            respuesta = actualizar_producto_backend(nombre, cantidad)
        else:
            respuesta = "No entendí bien el producto o la cantidad a actualizar."

    elif intencion == "buscar_producto":
        nombre, _ = extraer_nombre_y_cantidad(texto)
        respuesta = buscar_producto_backend(nombre) if nombre else "No entendí qué producto deseas buscar."

    elif intencion == "saludo":
        respuesta = random.choice([
            "Hola, ¿en qué puedo ayudarte?",
            "Saludos, listo para asistirte."
        ])

    elif intencion == "despedida" or intencion == "salir":
        respuesta = "Saliendo del programa. Hasta luego."

    elif intencion in ["afirmacion", "negacion"] and esperando_confirmacion:
        if intencion == "afirmacion":
            respuesta = agregar_producto_backend(datos_temporales)
        else:
            respuesta = "Operación cancelada."

        esperando_confirmacion = False
        datos_temporales = None
        ultima_intencion = None

    else:
        respuesta = "No tengo una acción definida para ese comando aún."

    guardar_log(texto, intencion, respuesta)
    hablar(respuesta)
    return respuesta

# ==== LOG DE INTERACCIONES ====

def guardar_log(texto_usuario, intencion, respuesta):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archivo_csv = "registro_asistente.csv"

    # Crear encabezado si el archivo no existe
    try:
        with open(archivo_csv, "x", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["timestamp", "usuario", "intencion", "respuesta"])
    except FileExistsError:
        pass

    # Agregar nueva fila
    with open(archivo_csv, "a", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([timestamp, texto_usuario, intencion, respuesta])


# ==== CICLO PRINCIPAL ====

def escuchar():
    modelo_voz = Model(MODEL_VOSK_PATH)
    reconocedor = KaldiRecognizer(modelo_voz, 16000)
    reconocedor.SetWords(True)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                        channels=1, callback=callback):
        hablar("Soy tu Asistente virtual VOXIA. Puedes comenzar a hablar.")

        buffer_audio = b""
        tiempo_ultimo_audio = time.time()
        silencio_max = 8  # segundos sin voz

        while True:
            if not q.empty():
                data = q.get()
                buffer_audio += data

                if reconocedor.AcceptWaveform(data):
                    resultado = json.loads(reconocedor.Result())
                    texto = resultado.get("text", "").strip()
                    buffer_audio = b""
                    tiempo_ultimo_audio = time.time()

                    if texto:
                        print(f">> Tú dijiste: {texto}")
                        respuesta = procesar_comando(texto)
                        hablar(respuesta)

                        if "saliendo" in respuesta.lower():
                            hablar("👋 Cerrando el asistente. ¡Hasta luego!")
                            break
                    else:
                        hablar("No escuché nada. Intenta de nuevo.")
            else:
                time.sleep(0.1)

            # Manejo de silencio prolongado
            if time.time() - tiempo_ultimo_audio > silencio_max:
                hablar("No detecto audio. ¿Quieres seguir hablando?")
                tiempo_ultimo_audio = time.time()

def procesar_comando(texto):
    texto_limpio = limpiar_texto(texto)
    intencion, confianza = detectar_intencion(texto_limpio)

    if confianza < UMBRAL_CONFIANZA:
        return "No entendí bien lo que dijiste. ¿Puedes repetirlo?"

    entidades = extraer_entidades(texto_limpio)
    respuesta = ejecutar_accion(intencion, entidades)
    guardar_log(texto, intencion, respuesta)  # si tienes esta función

    return respuesta


# ==== VARIABLES DE ESTADO ====
ultima_intencion = None
datos_temporales = None
esperando_confirmacion = False

# ==== EJECUCIÓN ====
if __name__ == "__main__":
    escuchar()
