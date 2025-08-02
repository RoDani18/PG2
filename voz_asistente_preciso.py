import sounddevice as sd
import queue
import json
import threading
import time
from vosk import Model, KaldiRecognizer
import pyttsx3

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

stop_words = set(stopwords.words('spanish'))

MODEL_PATH = "vosk-model-es-0.42"
SAMPLERATE = 16000
q = queue.Queue()

# 🧠 Entrenamiento
frases = [
    "consultar inventario", "ver inventario", "mostrar inventario",
    "agregar producto coca cola", "insertar producto manzanas cantidad 10",
    "eliminar pedido urgente", "cancelar pedido", "borrar pedido anterior",
    "salir del programa", "cerrar sistema", "terminar aplicación"
]
intenciones = [
    "consultar_inventario", "consultar_inventario", "consultar_inventario",
    "agregar_producto", "agregar_producto",
    "eliminar_pedido", "eliminar_pedido", "eliminar_pedido",
    "salir", "salir", "salir"
]

vectorizador = CountVectorizer()
X = vectorizador.fit_transform(frases)
modelo_intencion = MultinomialNB()
modelo_intencion.fit(X, intenciones)

# 🎧 Captura de audio
def callback(indata, frames, time, status):
    if status:
        print("⚠️ Error de audio:", status)
    q.put(bytes(indata))

# 🗣️ Voz hablada
hablando = threading.Lock()
def hablar(texto):
    def run():
        if hablando.locked():
            return
        with hablando:
            try:
                voz = pyttsx3.init()
                voz.setProperty('rate', 160)
                voz.setProperty('volume', 1.0)
                voz.say(texto)
                voz.runAndWait()
            except Exception as e:
                print("❌ Error al hablar:", e)
    threading.Thread(target=run).start()

# 🔍 Limpiar
def limpiar_texto(texto):
    palabras = texto.lower().split()
    filtradas = [p for p in palabras if p not in stop_words]
    return " ".join(filtradas)

# 🤖 Procesar
def procesar_comando(texto_original):
    texto = limpiar_texto(texto_original.strip())
    print(f">> Reconocido (limpio): {texto}")

    if len(texto.split()) < 2:
        print("⏸️ Ignorado: muy corto.")
        return

    X_test = vectorizador.transform([texto])
    proba = modelo_intencion.predict_proba(X_test)[0]
    idx = proba.argmax()
    confianza = proba[idx]
    intencion = modelo_intencion.classes_[idx]

    print(f"🎯 Confianza: {confianza:.2f} - Intención: {intencion}")

    if confianza < 0.6:
        respuesta = "No entendí ese comando con claridad. ¿Puedes repetirlo?"
        print("🤖 Respuesta:", respuesta)
        hablar(respuesta)
        return

    palabras = texto.split()

    if intencion == "consultar_inventario":
        try:
            from conexion import conectar
            conn = conectar()
            cur = conn.cursor()
            cur.execute("SELECT nombre, cantidad FROM inventario")
            productos = cur.fetchall()
            conn.close()

            if productos:
                respuesta = "Inventario actual: "
                for p in productos:
                    respuesta += f"{p[0]} con {p[1]} unidades. "
            else:
                respuesta = "El inventario está vacío."
        except Exception as e:
            print("❌ Error al consultar inventario:", e)
            respuesta = "No pude acceder al inventario."

    elif intencion == "agregar_producto":
        try:
            idx = palabras.index("producto")
            datos = palabras[idx + 1:]

            if "cantidad" in datos:
                c_idx = datos.index("cantidad")
                nombre = " ".join(datos[:c_idx])
                cantidad_txt = datos[c_idx + 1]
            else:
                nombre = " ".join(datos)
                cantidad_txt = "1"

            # Números escritos
            numeros_texto = {
                "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
                "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
                "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
                "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90,
                "cien": 100
            }

            try:
                cantidad = int(cantidad_txt)
            except ValueError:
                cantidad = numeros_texto.get(cantidad_txt.lower(), 1)

            palabras_invalidas = ["claridad", "puedes", "repetirlo", "inventario", "comando"]
            nombre_limpio = " ".join([p for p in nombre.split() if p not in palabras_invalidas])

            from crud_productos import agregar_producto
            exito = agregar_producto(nombre_limpio, cantidad)

            if exito:
                respuesta = f"Producto '{nombre_limpio}' agregado con cantidad {cantidad}."
            else:
                respuesta = "Hubo un error al guardar el producto."

        except Exception as e:
            print("⚠️ Error al interpretar:", e)
            respuesta = "No pude procesar el producto o la cantidad."

    elif intencion == "eliminar_pedido":
        respuesta = "Pedido eliminado con éxito."

    elif intencion == "salir":
        respuesta = "Saliendo del programa. Hasta luego."
        print("🤖 Respuesta:", respuesta)
        hablar(respuesta)
        time.sleep(3)
        exit()

    else:
        respuesta = "No entendí ese comando."

    print("🤖 Respuesta:", respuesta)
    hablar(respuesta)

# 🚀 Cargar modelo
print("⏳ Cargando modelo de voz...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLERATE)
print("✅ Modelo cargado.")

saludo = (
    "Hola, soy tu asistente. Puedes decir cosas como consultar inventario, "
    "agregar producto seguido del nombre y cantidad, o eliminar pedido. "
    "Para salir, di salir del programa."
)
print("🤖 " + saludo)
hablar(saludo)

# 🔁 Bucle con espera inteligente
print("🎙️ Esperando audio...")

try:
    with sd.RawInputStream(
        samplerate=SAMPLERATE,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        tiempo_silencio = 0
        tiempo_max_espera = 4

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                resultado = json.loads(rec.Result())
                texto = resultado['text']
                if texto:
                    procesar_comando(texto)
                    tiempo_silencio = 0
                else:
                    tiempo_silencio += 1

            time.sleep(0.3)

            if tiempo_silencio >= tiempo_max_espera * 5:
                print("🕓 Tiempo sin voz, escuchando nuevamente...")
                hablar("Estoy escuchando. ¿Qué deseas hacer?")
                tiempo_silencio = 0

except KeyboardInterrupt:
    print("\n🛑 Asistente detenido manualmente.")
except Exception as e:
    print("❌ Error:", str(e))
