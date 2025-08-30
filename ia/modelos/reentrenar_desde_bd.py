from ia.modelos.entrenar_modelo import entrenar_desde_base_y_guardar, cargar_base
from ia.modelos.utils import limpiar_texto, engine
from sqlalchemy import text

def cargar_dataset():
    textos, etiquetas = [], []

    # Frases manuales
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT frase, intencion FROM frases_entrenamiento
        """)).fetchall()
        for frase, intencion in rows:
            textos.append(limpiar_texto(frase))
            etiquetas.append(intencion)

    # Frases de usuarios
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT frase, COALESCE(intencion, intencion_sugerida) AS etiqueta
            FROM interacciones
            WHERE COALESCE(intencion, intencion_sugerida) IS NOT NULL
        """)).fetchall()
        for frase, etiqueta in rows:
            textos.append(limpiar_texto(frase))
            etiquetas.append(etiqueta)

    return textos, etiquetas


def reentrenar():
    textos, etiquetas = cargar_dataset()
    entrenar_desde_base_y_guardar(textos, etiquetas)
    registrar_version_modelo(len(textos), notas="Reentrenamiento automático")


def registrar_version_modelo(total, origen="frases_entrenamiento + interacciones", notas="Auto"):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO versiones_modelo (total_frases, origen, notas)
            VALUES (:total, :origen, :notas)
        """), {
            "total": total,
            "origen": origen,
            "notas": notas
        })