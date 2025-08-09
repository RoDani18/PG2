from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_pedidos():
    return {"mensaje": "Pedidos funcionando correctamente"}
