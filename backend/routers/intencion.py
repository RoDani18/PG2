from fastapi import APIRouter, Request
from ia.modelos.utils import predecir_intencion
from ia.modelos.entidades import extraer_entidades

router = APIRouter()

@router.post("/")
async def detectar_intencion(request: Request):
    datos = await request.json()
    texto = datos.get("texto", "").strip()
    usuario = datos.get("usuario", "anonimo")

    intencion, confianza = predecir_intencion(texto, usuario)
    entidades = extraer_entidades(texto)

    return {
        "intencion": intencion,
        "confianza": confianza,
        "entidades": entidades
    }
