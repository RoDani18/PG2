import os
import joblib
import pickle
from sqlalchemy import text
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from ia.modelos.utils import engine, limpiar_texto

# 📁 Carpeta de modelos
MODELOS_DIR = "modelos"
os.makedirs(MODELOS_DIR, exist_ok=True)

# 🧹 Eliminar modelos anteriores
def limpiar_modelos_anteriores():
    for archivo in os.listdir(MODELOS_DIR):
        if archivo.endswith(".h5") or archivo.endswith(".pkl"):
            os.remove(os.path.join(MODELOS_DIR, archivo))

# 📥 Cargar frases desde BD
def cargar_dataset():
    textos, etiquetas = [], []
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT frase, intencion FROM frases_entrenamiento
            WHERE intencion IS NOT NULL
        """)).fetchall()
        for frase, intencion in rows:
            textos.append(limpiar_texto(frase))
            etiquetas.append(intencion)
    return textos, etiquetas

# 🧠 Entrenamiento
def entrenar_modelo(textos, etiquetas):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textos).toarray()

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(etiquetas)
    y_cat = to_categorical(y)

    model = Sequential([
        Dense(64, input_dim=X.shape[1], activation='relu'),
        Dense(32, activation='relu'),
        Dense(y_cat.shape[1], activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y_cat, epochs=30, verbose=1)

    # 💾 Guardar artefactos
    model.save(os.path.join(MODELOS_DIR, "modelo_intencion.h5"))
    joblib.dump(label_encoder, os.path.join(MODELOS_DIR, "label_encoder.pkl"))
    with open(os.path.join(MODELOS_DIR, "vectorizador.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    return len(textos)

# 🗂️ Registrar versión
def registrar_version(total):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO versiones_modelo (fecha, total_frases, origen, notas)
            VALUES (CURRENT_TIMESTAMP, :total, 'frases_entrenamiento', 'Reentrenamiento automático')
        """), {"total": total})

# 🚀 Reentrenamiento completo
def reentrenar():
    limpiar_modelos_anteriores()
    textos, etiquetas = cargar_dataset()
    total = entrenar_modelo(textos, etiquetas)
    registrar_version(total)
    return total

# 🧪 Ejecución directa
if __name__ == "__main__":
    total = reentrenar()
    print(f"✅ Reentrenamiento completado con {total} frases.")
