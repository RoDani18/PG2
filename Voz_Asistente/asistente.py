import warnings
warnings.filterwarnings("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import queue
import json
import random
import re
import sys
import requests
import time
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer

# ==== RUTAS Y MODELOS ====
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
MODEL_VOSK_PATH = "vosk-model-es-0.42"
API_URL = "http://127.0.0.1:8000"
UMBRAL_CONFIANZA = 0.5
LOG_PATH = "log_asistente.txt"

# ==== IMPORTS LOCALES ====
from ia.utils import (
    limpiar_texto,
    cargar_intenciones,
    predecir_intencion,
    modelo as model_intencion,
    vectorizador,
    label_encoder
)

# ==== MOTOR DE VOZ ====
voz = pyttsx3.init()
voz.setProperty('rate', 150)

def hablar(texto):
    print(f"🤖 {texto}")
    voz.say(texto)
    voz.runAndWait()

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

# ==== VERIFICACIÓN DE BACKEND ====
def backend_activo():
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

# ==== FUNCIONES DE BACKEND ====

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
            texto = "Esto es lo que hay en inventario:\n"
            for p in productos:
                texto += f"- {p['nombre']}: {p['cantidad']} unidades\n"
            return texto
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
    nombre = re.search(r"(?:agregar|producto|nombre)?\s*(\w+)", texto)
    precio = re.search(r"(?:precio|vale|cuesta|a)\s*(\w+)", texto)
    cantidad = re.search(r"(?:cantidad|unidades|hay|de)\s*(\w+)", texto)

    if nombre and precio and cantidad:
        nombre_val = nombre.group(1).capitalize()
        precio_val = convertir_numero(precio.group(1))
        cantidad_val = convertir_numero(cantidad.group(1))

        if precio_val is not None and cantidad_val is not None:
            return {
                "nombre": nombre_val,
                "precio": float(precio_val),
                "cantidad": int(cantidad_val)
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

def guardar_log(texto, intencion, respuesta):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"Usuario: {texto}\n")
        f.write(f"Intención: {intencion}\n")
        f.write(f"Asistente: {respuesta}\n")
               f.write("="*40 + "\n")

# ==== CICLO PRINCIPAL ====

def escuchar():
    model = Model(MODEL_VOSK_PATH)
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        hablar("Asistente activado. Puedes comenzar a hablar.")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                resultado = json.loads(rec.Result())
                texto = resultado.get("text", "").strip()
                if texto:
                    texto_limpio = limpiar_texto(texto)
                    X = vectorizador.transform([texto_limpio])
                    y_pred = model_intencion.predict(X)
                    intencion = label_encoder.inverse_transform(y_pred)[0]
                    respuesta = ejecutar_intencion(intencion, texto)

                    if intencion == "salir" or respuesta.startswith("Saliendo"):
                        break

# ==== VARIABLES DE ESTADO ====
ultima_intencion = None
datos_temporales = None
esperando_confirmacion = False

# ==== EJECUCIÓN ====
if __name__ == "__main__":
    escuchar()
