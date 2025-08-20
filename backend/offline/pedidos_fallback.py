from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

# Simulación de almacenamiento local en memoria
pedidos_local = []

class Pedido(BaseModel):
    id: str
    cliente: str
    productos: List[str]
    total: float
    fecha: datetime
    sincronizado: bool = False

# Crear un nuevo pedido
def guardar_pedido(cliente: str, productos: List[str], total: float) -> Pedido:
    pedido = Pedido(
        id=str(uuid.uuid4()),
        cliente=cliente,
        productos=productos,
        total=total,
        fecha=datetime.now(),
        sincronizado=False
    )
    pedidos_local.append(pedido)
    return pedido

# Consultar todos los pedidos
def consultar_pedidos() -> List[Pedido]:
    return pedidos_local

# Actualizar un pedido existente
def actualizar_pedido(pedido_id: str, **kwargs) -> Optional[Pedido]:
    for pedido in pedidos_local:
        if pedido.id == pedido_id:
            for key, value in kwargs.items():
                if hasattr(pedido, key):
                    setattr(pedido, key, value)
            return pedido
    return None

# Eliminar un pedido
def eliminar_pedido(pedido_id: str) -> bool:
    global pedidos_local
    pedidos_local = [p for p in pedidos_local if p.id != pedido_id]
    return True

# Listar pedidos no sincronizados
def listar_pedidos_no_sincronizados() -> List[Pedido]:
    return [p for p in pedidos_local if not p.sincronizado]

# Marcar pedido como sincronizado
def marcar_como_sincronizado(pedido_id: str) -> bool:
    for pedido in pedidos_local:
        if pedido.id == pedido_id:
            pedido.sincronizado = True
            return True
    return False
