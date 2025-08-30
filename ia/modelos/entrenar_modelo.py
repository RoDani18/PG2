from pathlib import Path
import json
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
from ia.modelos.utils import limpiar_texto

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELOS_DIR = BASE_DIR / "modelos"
MODELOS_DIR.mkdir(parents=True, exist_ok=True)

INTENCIONES_PATH = Path(__file__).resolve().parent.parent.parent / "intenciones.json"
MODEL_PATH = MODELOS_DIR / "modelo_intencion.h5"
VECT_PATH = MODELOS_DIR / "vectorizador.pkl"
ENC_PATH = MODELOS_DIR / "label_encoder.pkl"

def cargar_base():
    if not INTENCIONES_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {INTENCIONES_PATH}")
    with open(INTENCIONES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    textos, etiquetas = [], []
    for intent in data.get("intenciones", []):
        tag = intent["tag"]
        for p in intent.get("patrones", []):
            textos.append(limpiar_texto(p))
            etiquetas.append(tag)
    return textos, etiquetas

def build_model(input_dim, num_classes):
    model = Sequential([
        Dense(128, activation="relu", input_shape=(input_dim,)),
        Dropout(0.5),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(num_classes, activation="softmax"),
    ])
    model.compile(optimizer=Adam(learning_rate=1e-3),
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"])
    return model

def entrenar_desde_base_y_guardar(textos, etiquetas):
    vect = CountVectorizer(max_features=5000, ngram_range=(1,2))
    X = vect.fit_transform(textos).toarray()
    le = LabelEncoder()
    y = le.fit_transform(etiquetas)

    model = build_model(X.shape[1], len(le.classes_))
    model.fit(X, y, epochs=40, batch_size=32, verbose=1)

    model.save(MODEL_PATH)
    joblib.dump(vect, VECT_PATH)
    joblib.dump(le, ENC_PATH)
