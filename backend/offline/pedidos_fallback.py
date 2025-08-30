import sqlite3
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent / "offline_sqlite.db"

class Pedido(BaseModel):
    id: str
    usuario_id: int
    producto: str
    cantidad: int
    estado: str
    producto_id: int
    fecha: datetime
    sincronizado: bool = False

def init_pedidos():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                usuario_id INTEGER,
                producto TEXT,
                cantidad INTEGER,
                estado TEXT,
                producto_id INTEGER,
                fecha TEXT,
                sincronizado INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def guardar_pedido(usuario_id: int, producto: str, cantidad: int, estado: str, producto_id: int) -> Pedido:
    pedido = Pedido(
        id=str(uuid.uuid4()),
        usuario_id=usuario_id,
        producto=producto,
        cantidad=cantidad,
        estado=estado,
        producto_id=producto_id,
        fecha=datetime.now(),
        sincronizado=False
    )
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (id, usuario_id, producto, cantidad, estado, producto_id, fecha, sincronizado)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            pedido.id,
            pedido.usuario_id,
            pedido.producto,
            pedido.cantidad,
            pedido.estado,
            pedido.producto_id,
            pedido.fecha.isoformat()
        ))
        conn.commit()
    return pedido

def consultar_pedidos() -> List[Pedido]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario_id, producto, cantidad, estado, producto_id, fecha, sincronizado FROM pedidos")
        rows = cursor.fetchall()
        return [
            Pedido(
                id=row[0],
                usuario_id=row[1],
                producto=row[2],
                cantidad=row[3],
                estado=row[4],
                producto_id=row[5],
                fecha=datetime.fromisoformat(row[6]),
                sincronizado=bool(row[7])
            )
            for row in rows
        ]

def actualizar_pedido(pedido_id: str, **kwargs) -> Optional[Pedido]:
    pedido = consultar_pedido_por_id(pedido_id)
    if not pedido:
        return None

    for key, value in kwargs.items():
        if hasattr(pedido, key):
            setattr(pedido, key, value)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedidos SET usuario_id = ?, producto = ?, cantidad = ?, estado = ?, producto_id = ?, fecha = ?, sincronizado = ?
            WHERE id = ?
        """, (
            pedido.usuario_id,
            pedido.producto,
            pedido.cantidad,
            pedido.estado,
            pedido.producto_id,
            pedido.fecha.isoformat(),
            int(pedido.sincronizado),
            pedido.id
        ))
        conn.commit()
    return pedido

def consultar_pedido_por_id(pedido_id: str) -> Optional[Pedido]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario_id, producto, cantidad, estado, producto_id, fecha, sincronizado FROM pedidos WHERE id = ?", (pedido_id,))
        row = cursor.fetchone()
        if row:
            return Pedido(
                id=row[0],
                usuario_id=row[1],
                producto=row[2],
                cantidad=row[3],
                estado=row[4],
                producto_id=row[5],
                fecha=datetime.fromisoformat(row[6]),
                sincronizado=bool(row[7])
            )
        return None

def eliminar_pedido(pedido_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        conn.commit()
        return cursor.rowcount > 0

def listar_pedidos_no_sincronizados() -> List[Pedido]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario_id, producto, cantidad, estado, producto_id, fecha, sincronizado FROM pedidos WHERE sincronizado = 0")
        rows = cursor.fetchall()
        return [
            Pedido(
                id=row[0],
                usuario_id=row[1],
                producto=row[2],
                cantidad=row[3],
                estado=row[4],
                producto_id=row[5],
                fecha=datetime.fromisoformat(row[6]),
                sincronizado=False
            )
            for row in rows
        ]

def marcar_como_sincronizado(ids: List[str]):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany("UPDATE pedidos SET sincronizado = 1 WHERE id = ?", [(i,) for i in ids])
        conn.commit()

init_pedidos()
