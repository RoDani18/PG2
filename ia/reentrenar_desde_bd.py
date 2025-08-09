# ia/reentrenar_desde_bd.py

import psycopg2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import numpy as np
from ia.utils import limpiar_texto

# 1. Frases base
frases = [
    "consultar inventario", "ver inventario", "mostrar inventario",
    "agregar producto coca cola", "añadir producto nuevo", "insertar producto manzanas cantidad 10",
    "eliminar pedido urgente", "cancelar pedido", "borrar pedido anterior",
    "salir del programa", "cerrar sistema", "terminar aplicación"
]

intenciones = [
    "consultar_inventario", "consultar_inventario", "consultar_inventario",
    "agregar_producto", "agregar_producto", "agregar_producto",
    "eliminar_pedido", "eliminar_pedido", "eliminar_pedido",
    "salir", "salir", "salir"
]

# 2. Cargar frases nuevas desde la base de datos
def cargar_desde_bd():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="asistentepg",  # Cambia por tu nombre real
            user="postgres",
            password="admin123"
        )
        cur = conn.cursor()
        cur.execute("SELECT frase, intencion_sugerida FROM interacciones WHERE intencion_sugerida != 'pendiente'")
        resultados = cur.fetchall()
        conn.close()
        return [(limpiar_texto(f), i) for f, i in resultados]
    except Exception as e:
        print("❌ Error al conectar con la base de datos:", e)
        return []

# 3. Cargar datos y combinar
frases_nuevas = cargar_desde_bd()
for frase, intencion in frases_nuevas:
    frases.append(frase)
    intenciones.append(intencion)

# 4. Preprocesar
frases_limpias = [limpiar_texto(f) for f in frases]
vectorizador = CountVectorizer()
X = vectorizador.fit_transform(frases_limpias).toarray()

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(intenciones)

# 5. Modelo
modelo = Sequential()
modelo.add(Dense(32, input_shape=(X.shape[1],), activation='relu'))
modelo.add(Dense(16, activation='relu'))
modelo.add(Dense(len(set(y)), activation='softmax'))

modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

modelo.fit(X, y, epochs=100, verbose=1)

# 6. Guardar
modelo.save("ia/modelo_intencion.h5")
joblib.dump(vectorizador, "ia/vectorizador.pkl")
joblib.dump(label_encoder, "ia/label_encoder.pkl")

print("✅ Reentrenamiento completo con nuevas frases.")
