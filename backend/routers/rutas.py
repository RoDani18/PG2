from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_rutas():
    return {"mensaje": "Rutas funcionando correctamente"}
