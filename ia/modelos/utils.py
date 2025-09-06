import os
from pathlib import Path
import re
import joblib
import numpy as np
from threading import RLock
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from tensorflow.keras.models import load_model

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

BASE_DIR = Path(__file__).resolve().parent.absolute()
MODEL_PATH = BASE_DIR / "modelo_intencion.h5"
VECT_PATH = BASE_DIR / "vectorizador.pkl"
ENC_PATH = BASE_DIR / "label_encoder.pkl"


_model = None
_vectorizer = None
_label_encoder = None
_lock = RLock()

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

def predecir_intencion(texto: str, usuario="anonimo"):
    if not texto or not texto.strip():
        return "desconocida", 0.0

    _ensure_loaded()
    t = limpiar_texto(texto)
    X = _vectorizer.transform([t]).toarray()
    y_proba = _model.predict(X, verbose=0)[0]
    idx = int(np.argmax(y_proba))
    confianza = float(y_proba[idx])
    intent = _label_encoder.inverse_transform([idx])[0]

    if confianza < 0.6:
        registrar_interaccion(usuario, texto, intent, confianza)

    return intent, confianza

def registrar_interaccion(usuario, frase, intencion_sugerida, confianza):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO interacciones (usuario, frase, intencion_sugerida, confianza, fecha)
            VALUES (:usuario, :frase, :intencion_sugerida, :confianza, NOW())
        """), {
            "usuario": usuario,
            "frase": frase,
            "intencion_sugerida": intencion_sugerida,
            "confianza": confianza
        })

def recargar_modelo():
    global _model, _vectorizer, _label_encoder
    with _lock:
        _model = load_model(MODEL_PATH)
        _vectorizer = joblib.load(VECT_PATH)
        _label_encoder = joblib.load(ENC_PATH)
