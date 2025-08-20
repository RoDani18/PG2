import re

def extraer_entidades(texto):
    entidades = {}
    texto = texto.lower()

    productos = ["pepsi", "coca", "coca cola", "agua", "gatorade"]
    for producto in productos:
        if producto in texto:
            entidades["nombre"] = producto
            break

    # Cantidad
    palabras_a_numeros = {
        "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        "diez": 10, "veinte": 20, "cuarenta": 40
    }
    for palabra, numero in palabras_a_numeros.items():
        if palabra in texto:
            entidades["cantidad"] = numero
            break

    cantidad_match = re.search(r"\b(\d+)\b", texto)
    if cantidad_match:
        entidades["cantidad"] = int(cantidad_match.group())

    # Precio
    precio_match = re.search(r"(precio|q|vale|cuesta)\s*([0-9]+)", texto)
    if precio_match:
        entidades["precio"] = int(precio_match.group(2))

    return entidades
