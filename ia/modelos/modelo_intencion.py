import os
import pickle
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Ruta a la carpeta de modelos
MODELOS_DIR = os.path.dirname(__file__)

# Cargar modelo Keras (.h5)
ruta_modelo = os.path.join(MODELOS_DIR, "modelo_intencion.h5")  
model = load_model(ruta_modelo)

# Cargar vectorizador
ruta_vector = os.path.join(MODELOS_DIR, "vectorizador.pkl")
with open(ruta_vector, "rb") as f:
    vectorizer = pickle.load(f)

# Cargar label encoder
ruta_encoder = os.path.join(MODELOS_DIR, "label_encoder.pkl")
label_encoder = joblib.load(ruta_encoder)

# Función principal
def detectar_intencion(texto):
    
    if not texto.strip():
        return "desconocida", 0.0

    X = vectorizer.transform([texto]).toarray()
    y_proba = model.predict(X)[0]
    confianza = float(np.max(y_proba))
    intencion = label_encoder.inverse_transform([np.argmax(y_proba)])[0]
    return intencion, confianza
