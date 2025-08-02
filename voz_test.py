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
nltk.download('stopwords')  # Solo la primera vez

stop_words = set(stopwords.words('spanish'))

MODEL_PATH = "vosk-model-es-0.42"
SAMPLERATE = 16000
q = queue.Queue()

# 🧠 Más frases = más precisión
frases = [
    "consultar inventario", "ver inventario", "muéstrame el inventario", "qué hay disponible",
    "puedo ver lo que hay", "quiero consultar", "consultar productos",

    "agregar producto coca cola", "añade producto nuevo", "insertar artículo manzanas",
    "añadir producto pepsi", "quiero agregar un producto", "introduce un nuevo artículo",

    "eliminar pedido urgente", "cancelar pedido", "borrar pedido anterior",
    "anula el último pedido", "cancelar una orden", "eliminar orden",

    "salir del programa", "cerrar sistema", "terminar aplicación", "ya no quiero seguir", "salir"
]
intenciones = [
    "consultar_inventario", "consultar_inventario", "consultar_inventario", "consultar_inventario",
    "consultar_inventario", "consultar_inventario", "consultar_inventario",

    "agregar_producto", "agregar_producto", "agregar_producto",
    "agregar_producto", "agregar_producto", "agregar_producto",

    "eliminar_pedido", "eliminar_pedido", "eliminar_pedido",
    "eliminar_pedido", "eliminar_pedido", "eliminar_pedido",

    "salir", "salir", "salir", "salir", "salir"
]

# 🎓 Entrenamiento del clasificador
vectorizador = CountVectorizer()
X = vectorizador.fit_transform(frases)
modelo_intencion = MultinomialNB()
modelo_intencion.fit(X, intenciones)

# 🎧 Captura de audio
def callback(indata, frames, time, status):
    if status:
        print("⚠️ Error de audio:", status)
    q.put(bytes(indata))

# 🗣️ Voz sin errores
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

# 🔍 Limpiar entrada
def limpiar_texto(texto):
    palabras = texto.lower().split()
    filtradas = [p for p in palabras if p not in stop_words]
    return " ".join(filtradas)

# 🤖 Procesar lo que diga el usuario
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
        respuesta = "Mostrando el inventario actual."
    elif intencion == "agregar_producto":
        try:
            idx = palabras.index("producto")
            nombre = " ".join(palabras[idx+1:]) or "sin nombre"
        except ValueError:
            nombre = "desconocido"
        respuesta = f"Producto '{nombre}' agregado correctamente."
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

# 🚀 Inicio
print("⏳ Cargando modelo de voz...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLERATE)
print("✅ Modelo cargado.")

saludo = (
    "Hola, soy tu asistente. Puedes decir cosas como consultar inventario, "
    "agregar producto Coca Cola o eliminar pedido. Para salir, di salir del programa."
)
print("🤖 " + saludo)
hablar(saludo)

# 🔁 Escuchar comandos
try:
    with sd.RawInputStream(samplerate=SAMPLERATE, blocksize=16000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                resultado = json.loads(rec.Result())
                texto = resultado['text']
                if texto:
                    procesar_comando(texto)
except KeyboardInterrupt:
    print("\n🛑 Asistente detenido manualmente.")
except Exception as e:
    print("❌ Error:", str(e))
