# -*- coding: utf-8 -*-
print("🧪 Iniciando pruebas de extracción de entidades...")

try:
    from modelos.entidades import extraer_entidades
except Exception as e:
    print(f"❌ Error al importar 'extraer_entidades': {e}")
    exit()

# Lista de casos de prueba
casos = [
    {
        "frase": "agrega coca cola precio veinte cantidad cinco",
        "esperado": {"nombre": "coca cola", "precio": "20", "cantidad": "5"}
    },
    {
        "frase": "insertar producto galletas precio quince cantidad ocho",
        "esperado": {"nombre": "galletas", "precio": "15", "cantidad": "8"}
    },
    {
        "frase": "nuevo producto yogurt precio ocho cantidad doce",
        "esperado": {"nombre": "yogurt", "precio": "8", "cantidad": "doce"}
    },
    {
        "frase": "añadir jabón",
        "esperado": {"nombre": "jabón"}
    },
    {
        "frase": "precio diez cantidad cinco",
        "esperado": {"precio": "10", "cantidad": "5"}
    },
    {
        "frase": "producto manzanas",
        "esperado": {"nombre": "manzanas"}
    }
]

# Ejecutar pruebas
fallos = 0
for i, caso in enumerate(casos, start=1):
    frase = caso["frase"]
    esperado = caso["esperado"]
    print(f"\n🔍 Caso {i}: '{frase}'")

    try:
        resultado = extraer_entidades(frase)
        print(f"➡️ Resultado: {resultado}")
        assert all(resultado.get(k) == v for k, v in esperado.items()), f"❌ Fallo en caso {i}"
        print("✅ Prueba superada")
    except AssertionError as ae:
        print(str(ae))
        fallos += 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        fallos += 1

# Resumen
print("\n📊 Resumen de pruebas:")
print(f"✅ Éxitos: {len(casos) - fallos}")
print(f"❌ Fallos: {fallos}")
