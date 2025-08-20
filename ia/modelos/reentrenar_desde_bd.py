# ia/reentrenar_desde_db.py
import os
from pathlib import Path
import joblib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from ia.modelos.entrenar_modelo import entrenar_desde_base_y_guardar
from ia.modelos.utils import limpiar_texto

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no configurada en .env")

engine = create_engine(DATABASE_URL)

def cargar_dataset():
    # 1) Base estática
    from ia.modelos.entrenar_modelo import cargar_base
    textos, etiquetas = cargar_base()

    # 2) Confirmadas y auto-etiquetadas desde BD
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT texto, COALESCE(intent_final, intent_predicha) AS etiqueta
            FROM interacciones
            WHERE (estado = 'confirmada' OR estado = 'auto')
            AND COALESCE(intent_final, intent_predicha) IS NOT NULL
        """)).fetchall()

    for texto, etiqueta in rows:
        textos.append(limpiar_texto(texto))
        etiquetas.append(etiqueta)
    return textos, etiquetas

def reentrenar():
    textos, etiquetas = cargar_dataset()
    entrenar_desde_base_y_guardar(textos, etiquetas)
    print("✅ Reentrenamiento completado")

if __name__ == "__main__":
    reentrenar()
