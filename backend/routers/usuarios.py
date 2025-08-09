from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_usuarios():
    return {"mensaje": "Usuarios funcionando correctamente"}
