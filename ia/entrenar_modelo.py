import json
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
import nltk
from nltk.stem import SnowballStemmer
import pickle

# Descargar recursos de NLTK necesarios
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Rutas absolutas
BASE_DIR = os.path.dirname(__file__)
INTENCIONES_PATH = os.path.join(BASE_DIR, 'intenciones.json')
TOKENIZER_PATH = os.path.join(BASE_DIR, 'tokenizer.pkl')
LABELS_PATH = os.path.join(BASE_DIR, 'labels.pkl')
MODEL_PATH = os.path.join(BASE_DIR, 'modelo_entrenado.h5')

# Verificar archivo intenciones
if not os.path.exists(INTENCIONES_PATH):
    raise FileNotFoundError(f"No se encontró el archivo: {INTENCIONES_PATH}")

# Cargar intenciones
with open(INTENCIONES_PATH, encoding='utf-8') as archivo:
    datos = json.load(archivo)

# Inicializar stemmer
stemmer = SnowballStemmer('spanish')

palabras = []
clases = []
documentos = []
ignorar_palabras = ['?', '¿', '!', '.', ',']

# Procesar patrones
for intent in datos['intenciones']:
    for patron in intent['patrones']:
        tokens = nltk.word_tokenize(patron.lower(), language='spanish')
        palabras.extend(tokens)
        documentos.append((tokens, intent['tag']))
        if intent['tag'] not in clases:
            clases.append(intent['tag'])

# Limpiar palabras
palabras = [stemmer.stem(p) for p in palabras if p not in ignorar_palabras]
palabras = sorted(list(set(palabras)))
clases = sorted(list(set(clases)))

# Crear dataset
entrenamiento = []
salida_vacia = [0] * len(clases)

for doc in documentos:
    bolsa = []
    patron_palabras = [stemmer.stem(p.lower()) for p in doc[0]]
    for palabra in palabras:
        bolsa.append(1 if palabra in patron_palabras else 0)
    salida_fila = list(salida_vacia)
    salida_fila[clases.index(doc[1])] = 1
    entrenamiento.append([bolsa, salida_fila])

entrenamiento = np.array(entrenamiento, dtype=object)
train_x = np.array(list(entrenamiento[:, 0]))
train_y = np.array(list(entrenamiento[:, 1]))

# Guardar tokenizer y etiquetas
with open(TOKENIZER_PATH, 'wb') as f:
    pickle.dump(palabras, f)

with open(LABELS_PATH, 'wb') as f:
    pickle.dump(clases, f)

# Crear modelo
modelo = Sequential()
modelo.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
modelo.add(Dropout(0.5))
modelo.add(Dense(64, activation='relu'))
modelo.add(Dropout(0.5))
modelo.add(Dense(len(train_y[0]), activation='softmax'))

# Compilar modelo
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
modelo.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Entrenar modelo
modelo.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# Guardar modelo entrenado
modelo.save(MODEL_PATH)
print(f"✅ Modelo guardado en {MODEL_PATH}")
print(f"✅ Tokenizer guardado en {TOKENIZER_PATH}")
print(f"✅ Etiquetas guardadas en {LABELS_PATH}")
