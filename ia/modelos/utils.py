# ia/utils.py
from pathlib import Path
import re
import joblib
import numpy as np
from threading import RLock
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent
MODELOS_DIR = BASE_DIR / "modelos"
MODEL_PATH = MODELOS_DIR / "modelo_intencion.h5"
VECT_PATH = MODELOS_DIR / "vectorizador.pkl"
ENC_PATH = MODELOS_DIR / "label_encoder.pkl"

_model = None
_vectorizer = None
_label_encoder = None
_lock = RLock()

def obtener_modelo():
    _ensure_loaded()
    return _model

def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def _ensure_loaded():
    global _model, _vectorizer, _label_encoder
    with _lock:
        if _model is None or _vectorizer is None or _label_encoder is None:
            _model = load_model(MODEL_PATH)
            _vectorizer = joblib.load(VECT_PATH)
            _label_encoder = joblib.load(ENC_PATH)

def predecir_intencion(texto: str):
    if not texto or not texto.strip():
        return "desconocida", 0.0
    _ensure_loaded()
    t = limpiar_texto(texto)
    X = _vectorizer.transform([t]).toarray()
    y_proba = _model.predict(X, verbose=0)[0]
    idx = int(np.argmax(y_proba))
    confianza = float(y_proba[idx])
    intent = _label_encoder.inverse_transform([idx])[0]
    return intent, confianza

def cargar_intenciones():
    _ensure_loaded()
    return _model, _vectorizer, _label_encoder

def cargar_intenciones():
    _ensure_loaded()
    return _model, _vectorizer, _label_encoder


def recargar_modelo():
    # Hot-reload seguro
    global _model, _vectorizer, _label_encoder
    with _lock:
        _model = load_model(MODEL_PATH)
        _vectorizer = joblib.load(VECT_PATH)
        _label_encoder = joblib.load(ENC_PATH)
