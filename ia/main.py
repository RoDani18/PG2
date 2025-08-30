from fastapi import FastAPI
from pydantic import BaseModel
from ia.modelos.utils import predecir_intencion
from ia.modelos.entidades import extraer_entidades
from ia.modelos.reentrenar_desde_bd import reentrenar
from ia.modelos.utils import _model, _label_encoder
from pydantic import BaseModel
from ia.modelos.utils import recargar_modelo
import threading
import time
from sqlalchemy import text
app = FastAPI(
    title="API de IA Conversacional",
    description="Detecta intenciones, extrae entidades y aprende dinámicamente",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a la API de IA Conversacional!"}

class FraseEntrada(BaseModel):
    texto: str
    usuario: str = "anonimo"

@app.post("/intencion")
def detectar_intencion(frase: FraseEntrada):
    intencion, confianza = predecir_intencion(frase.texto, frase.usuario)
    entidades = extraer_entidades(frase.texto)
    return {
        "intencion": intencion,
        "confianza": confianza,
        "entidades": entidades
    }

@app.post("/reentrenar")
def ejecutar_reentrenamiento():
    reentrenar()
    recargar_modelo()
    return {"mensaje": "✅ Reentrenamiento ejecutado correctamente"}


@app.get("/status")
def status():
    clases = list(_label_encoder.classes_) if _label_encoder else []
    return {
        "modelo_cargado": _model is not None,
        "total_clases": len(clases),
        "intenciones": clases
    }
    
@app.get("/intenciones")
def listar_intenciones():
    clases = list(_label_encoder.classes_) if _label_encoder else []
    return {"intenciones": clases}


class TextoEntrada(BaseModel):
    texto: str

@app.post("/predecir")
def predecir_texto(payload: TextoEntrada):
    from ia.modelos.utils import predecir_intencion
    intencion, confianza = predecir_intencion(payload.texto)
    return {"intencion": intencion, "confianza": confianza}


def loop_reentrenamiento(stop_event):
    while not stop_event.is_set():
        print("🔁 Reentrenando modelo desde BD...")
        try:
            reentrenar()
            recargar_modelo()
            print("✅ Reentrenamiento completado.")
        except Exception as e:
            print(f"❌ Error en reentrenamiento: {e}")
        time.sleep(3600)  # Cada hora

@app.get("/versiones")
def historial_versiones():
    from ia.modelos.utils import engine
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, fecha, total_frases, origen, notas
            FROM versiones_modelo
            ORDER BY fecha DESC
            LIMIT 10
        """)).fetchall()

    versiones = [
        {
            "id": r[0],
            "fecha": r[1].isoformat(),
            "total_frases": r[2],
            "origen": r[3],
            "notas": r[4]
        }
        for r in rows
    ]
    return {"versiones": versiones}

@app.post("/ia/probar-ia")
def probar_ia(frase: FraseEntrada):
    intencion, confianza = predecir_intencion(frase.texto, frase.usuario)
    entidades = extraer_entidades(frase.texto)
    return {
        "intencion": intencion,
        "confianza": confianza,
        "entidades": entidades
    }

stop_event = threading.Event()
threading.Thread(target=loop_reentrenamiento, args=(stop_event,), daemon=True).start()