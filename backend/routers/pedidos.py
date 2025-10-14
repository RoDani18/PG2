from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import models
from backend.auth.deps import get_db, require_roles, get_current_user
from backend.routers.schemas_pedidos import MovimientoInventarioResponse, PedidoConRuta, PedidoCreate, PedidoUpdate, PedidoResponse
import logging
from backend.routers.schemas_pedidos import PedidoResumen
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PedidoResponse])
def listar_todos(
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    return db.query(models.Pedido).all()

@router.get("/mios", response_model=List[PedidoResumen])
def listar_mios(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pedidos = db.query(models.Pedido).filter(models.Pedido.usuario_id == user.id).all()
    respuesta = []
    for p in pedidos:
        usuario_nombre = db.query(models.Usuario).filter_by(id=p.usuario_id).first().username
        fecha_formateada = p.fecha.strftime("%d/%m/%Y %H:%M")
        resumen = PedidoResumen(
            id=p.id,
            usuario=usuario_nombre,
            producto=p.producto,
            cantidad=p.cantidad,
            estado=p.estado,
            fecha=fecha_formateada,
            direccion=p.direccion
        )
        respuesta.append(resumen)
    return respuesta

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido_in: PedidoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("cliente","admin"))
):
    logger.info(f"📥 Pedido recibido: producto={pedido_in.producto}, cantidad={pedido_in.cantidad}, direccion={pedido_in.direccion}, usuario={user.id}")
    # ✅ Validar que el producto exista
    producto = db.query(models.Producto).filter_by(nombre=pedido_in.producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 📝 Crear el pedido si el producto existe
    pedido = models.Pedido(
        usuario_id=user.id,
        producto=pedido_in.producto,
        producto_id=producto.id,  # ✅ ← ESTE ES EL CAMBIO
        cantidad=pedido_in.cantidad,
        direccion=pedido_in.direccion,
        estado="pendiente"
    )
    
    logger.info(f"📥 Pedido recibido: producto={pedido_in.producto}, cantidad={pedido_in.cantidad}, direccion={pedido_in.direccion}, usuario={user.id}")
    db.add(pedido)
    try:
        db.commit()
        db.refresh(pedido)
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en pedido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    return pedido


@router.put("/{pedido_id}", response_model=PedidoResponse)
def actualizar_pedido(
    pedido_id: int,
    pedido_upd: PedidoUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    estado_anterior = ped.estado
    estado_nuevo = pedido_upd.estado

    for field, value in pedido_upd.dict(exclude_unset=True).items():
        setattr(ped, field, value)

    # 🧮 Actualizar inventario si cambia el estado
    if estado_nuevo and estado_nuevo != estado_anterior:
        producto = db.query(models.Producto).filter_by(nombre=ped.producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if estado_nuevo == "entregado":
            if producto.cantidad < ped.cantidad:
                raise HTTPException(status_code=400, detail="Inventario insuficiente para entregar el pedido")
            producto.cantidad -= ped.cantidad

            # 📝 Registrar salida en movimientos
            mov = models.MovimientoInventario(
                producto_id=producto.id,
                tipo="salida",
                cantidad=ped.cantidad,
                pedido_id=ped.id
            )
            db.add(mov)

        elif estado_nuevo == "cancelado":
            producto.cantidad += ped.cantidad

            # 📝 Registrar entrada en movimientos
            mov = models.MovimientoInventario(
                producto_id=producto.id,
                tipo="entrada",
                cantidad=ped.cantidad,
                pedido_id=ped.id
            )
            db.add(mov)

    try:
        db.commit()
        db.refresh(ped)
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en pedido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    return ped

@router.put("/cliente/{pedido_id}", response_model=PedidoResponse)
def cliente_modifica_pedido(
    pedido_id: int,
    pedido_upd: PedidoUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("cliente"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id, usuario_id=user.id).first()
    if not ped:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if ped.estado != "pendiente":
        raise HTTPException(status_code=400, detail="Solo puedes modificar pedidos pendientes")

    for field, value in pedido_upd.dict(exclude_unset=True).items():
        setattr(ped, field, value)

    db.commit()
    db.refresh(ped)
    return ped

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("cliente", "empleado", "admin"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if user.rol == "cliente" and ped.usuario_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes eliminar pedidos de otro usuario")

    db.delete(ped)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en pedido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    return None

@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido_por_id(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    ped = db.query(models.Pedido).filter_by(id=pedido_id).first()
    if not ped:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return ped

@router.get("/cliente/{cliente_id}", response_model=List[PedidoResponse])
def pedidos_por_cliente(cliente_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "empleado"))):
    return db.query(models.Pedido).filter_by(usuario_id=cliente_id).all()

@router.get("/historial/{cliente_id}", response_model=List[PedidoResponse])
def historial_pedidos(cliente_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "empleado"))):
    return db.query(models.Pedido).filter_by(usuario_id=cliente_id).order_by(models.Pedido.fecha.desc()).all()

@router.get("/reportes/globales")
def generar_reporte_global(periodo: str = "último mes", db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    # Simulación de filtro por periodo
    pedidos = db.query(models.Pedido).filter(models.Pedido.fecha >= calcular_fecha_desde(periodo)).all()
    return {"mensaje": f"Reporte generado para {periodo}", "total": len(pedidos)}

def calcular_fecha_desde(periodo: str):
    from datetime import datetime, timedelta
    ahora = datetime.utcnow()
    if periodo == "último mes":
        return ahora - timedelta(days=30)
    elif periodo == "último trimestre":
        return ahora - timedelta(days=90)
    elif periodo == "último año":
        return ahora - timedelta(days=365)
    return ahora - timedelta(days=30)  # Por defecto, último mes

@router.get("/movimientos", response_model=List[MovimientoInventarioResponse])
def ver_movimientos(db: Session = Depends(get_db), user=Depends(require_roles("admin", "empleado"))):
    return db.query(models.MovimientoInventario).order_by(models.MovimientoInventario.fecha.desc()).all()


@router.get("/pedido/{pedido_id}/detalle_completo", response_model=PedidoConRuta)
def detalle_completo(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter_by(id=pedido_id).first()
    ruta = db.query(models.Ruta).filter_by(pedido_id=pedido_id).order_by(models.Ruta.id.desc()).first()
    if not pedido or not ruta:
        raise HTTPException(404, "Pedido o ruta no encontrada")
    return {"pedido": pedido, "ruta": ruta}
