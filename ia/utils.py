import re
import json
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# ==== CARGA DE MODELO Y RECURSOS ====

modelo = load_model('ia/modelo_intencion.h5')  # Asegúrate que este sea el modelo correcto
vectorizador = joblib.load('ia/vectorizador.pkl')
label_encoder = joblib.load('ia/label_encoder.pkl')

# ==== FUNCIONES DE NLP ====

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúüñ\s]', '', texto)
    texto = texto.strip()
    return texto

def cargar_intenciones():
    try:
        with open("ia/intenciones.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error al cargar intenciones: {str(e)}")
        return {}

def predecir_intencion(texto, modelo, vectorizador, label_encoder):
    texto = limpiar_texto(texto)
    secuencia = vectorizador.transform([texto]).toarray()
    prediccion = modelo.predict(secuencia)[0]
    indice = np.argmax(prediccion)
    confianza = prediccion[indice]
    intencion = label_encoder.inverse_transform([indice])[0]
    return intencion, confianza

# ==== FUNCIONES DE INVENTARIO ====

def consultar_inventario():
    try:
        with open("data/inventario.json", "r", encoding="utf-8") as archivo:
            inventario = json.load(archivo)

        if not inventario:
            return "📦 El inventario está vacío."

        respuesta = "📦 Inventario actual:\n"
        for producto in inventario:
            respuesta += f"- {producto['nombre']} (Stock: {producto['stock']})\n"

        return respuesta.strip()

    except FileNotFoundError:
        return "❌ No se encontró el archivo de inventario."
    except Exception as e:
        return f"❌ Error al consultar el inventario: {str(e)}"
