import pickle
from tensorflow.keras.models import load_model
from ia.utils import predecir_intencion, limpiar_texto

# Cargar modelo, tokenizer y etiquetas
modelo = load_model('ia/modelo.h5')

with open('ia/tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

with open('ia/etiquetas.pkl', 'rb') as f:
    etiquetas = pickle.load(f)  # lista de etiquetas

# Frase de prueba
frase = "¿Puedes agregar un producto?"

# Limpiar texto (igual que en utils)
frase_limpia = limpiar_texto(frase)

# Predecir intención
intencion, confianza = predecir_intencion(frase_limpia, modelo, tokenizer, etiquetas)

print(f"Frase: {frase}")
print(f"Frase limpia: {frase_limpia}")
print(f"Intención predicha: {intencion}")
print(f"Confianza: {confianza:.2f}")
