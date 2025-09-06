import requests
import time
import json
from datetime import datetime

# Configuración
URL_IA = "http://localhost:8000/intencion"
URL_BACKEND = "http://localhost:8000/inventarios"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYW5pQGNvcnJlby5jb20iLCJleHAiOjE3NTcwNDkyODN9.Z2f8Zkn5F6lZSzYXlT8r_6Dr7rU61eKe9QZM2AHowFU"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Frases de prueba
frases = [
    {"texto": "Agrega 30 bigcolas al inventario", "esperado": 30, "precio": 1.0},
    {"texto": "Actualiza los bigcolas a 80 unidades", "esperado": 80, "precio": 2.0},
    {"texto": "Actualiza el precio de las bigcolas a 6", "esperado": 6, "precio": 6.0}
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def enviar_a_ia(frase):
    try:
        resp = requests.post(URL_IA, json={"texto": frase, "usuario": "test"}, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"❌ Error al enviar frase a IA: {str(e)}")
        return {}

def ejecutar_accion(intencion, entidades, precio):
    if not entidades:
        log("⚠️ Entidades vacías o no detectadas.")
        return False

    nombre = entidades.get("nombre")
    cantidad = entidades.get("cantidad")
    precio_extraido = entidades.get("precio", precio)

    if not nombre:
        log("⚠️ Falta el nombre del producto.")
        log("📎 Entidades recibidas: " + json.dumps(entidades, indent=2))
        return False

    try:
        if intencion == "agregar_producto":
            if not cantidad or not cantidad.isdigit():
                log("⚠️ Cantidad inválida para agregar.")
                return False
            data = {
                "nombre": nombre,
                "cantidad": int(cantidad),
                "precio": float(precio_extraido)
            }
            resp = requests.post(URL_BACKEND, json=data, headers=HEADERS)

        elif intencion == "actualizar_producto":
            data = {}
            if cantidad and cantidad.isdigit():
                data["cantidad"] = int(cantidad)
            if "precio" in entidades:
                data["precio"] = float(precio_extraido)
            if not data:
                log("⚠️ No hay datos válidos para actualizar.")
                return False
            resp = requests.put(f"{URL_BACKEND}/{nombre}", json=data, headers=HEADERS)

        else:
            log(f"⚠️ Intención no reconocida: {intencion}")
            return False

        log("📤 Payload enviado: " + json.dumps(data))
        log(f"📥 Código de respuesta: {resp.status_code}")
        return resp.status_code in [200, 201]

    except Exception as e:
        log(f"❌ Error al ejecutar acción: {str(e)}")
        return False

def consultar_inventario():
    try:
        resp = requests.get(URL_BACKEND, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"❌ Error al consultar inventario: {str(e)}")
        return []

def verificar_estado(nombre_producto):
    inventario = consultar_inventario()
    for item in inventario:
        if item.get("nombre") == nombre_producto:
            return item.get("cantidad")
    return None

# 🔁 Ejecución de pruebas
for paso, item in enumerate(frases, start=1):
    log(f"\n🔍 Paso {paso}: '{item['texto']}'")
    resp_ia = enviar_a_ia(item["texto"])

    intencion = resp_ia.get("intencion")
    entidades = resp_ia.get("entidades")

    if not intencion or intencion == "desconocida":
        log(f"❌ Intención no válida: {intencion}")
        continue
    else:
        log(f"➡️ Intención detectada: {intencion}")

    if not entidades:
        log("⚠️ No se detectaron entidades.")
        continue
    else:
        log("➡️ Entidades detectadas: " + json.dumps(entidades, indent=2))

    ok = ejecutar_accion(intencion, entidades, item["precio"])
    log(f"✅ Acción ejecutada: {ok}")

    time.sleep(1)
    cantidad_actual = verificar_estado(entidades.get("nombre"))
    log(f"📦 Estado actual de '{entidades.get('nombre')}': {cantidad_actual} (esperado: {item['esperado']})")

# 🧾 Resumen final
log("\n📊 Resumen de inventario:")
inventario = consultar_inventario()
for item in inventario:
    log(f"🧱 {item['nombre']}: {item['cantidad']} unidades")
