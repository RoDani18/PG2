# backend/routers/ia.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.connection import SessionLocal
from backend.config import settings
from backend import models
from ia.modelos.utils import predecir_intencion, recargar_modelo
from ia.modelos.reentrenar_desde_bd import entrenar_modelo
from backend.routers.usuarios import require_roles, get_current_user 
from fastapi import APIRouter
from backend.ia_client import detectar_intencion
from backend.database.connection import SessionLocal 
from word2number import w2n
from Voz_Asistente.inventario import agregar_producto, actualizar_producto, consultar_inventario


router = APIRouter(prefix="/ia", tags=["IA"])

TAU_LOW = settings.TAU_LOW
TAU_HIGH = settings.TAU_HIGH

class TextoEntrada(BaseModel):
    texto: str

@router.post("/probar-ia")
def probar_ia(entrada: TextoEntrada):
    resultado = detectar_intencion(entrada.texto)
    return resultado

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TextoIn(BaseModel):
    texto: str = Field(..., min_length=1, max_length=500)

class PrediccionOut(BaseModel):
    intencion: str
    confianza: float
    interaccion_id: int
    pedir_confirmacion: bool

class FeedbackIn(BaseModel):
    interaccion_id: int
    intent_final: Optional[str] = None
    accion: str = Field(..., pattern="^(confirmar|corregir|descartar)$")
    


@router.post("/predecir", response_model=PrediccionOut)
def predecir(texto_in: TextoIn, 
            db: Session = Depends(get_db),
            user: models.Usuario = Depends(get_current_user)):
    intent, conf = predecir_intencion(texto_in.texto)

    if conf >= TAU_HIGH:
        estado = "auto"
        intent_final = intent
        pedir_confirm = False
    else:
        estado = "pendiente"
        intent_final = None
        pedir_confirm = True if conf >= TAU_LOW else True  # pide confirmación

    inter = models.Interaccion(
        user_id=user.id if user else None,
        texto=texto_in.texto,
        intent_predicha=intent,
        confianza=conf,
        intent_final=intent_final,
        estado=estado
    )
    db.add(inter)
    db.commit()
    db.refresh(inter)

    return PrediccionOut(
        intencion=intent, confianza=conf, interaccion_id=inter.id,
        pedir_confirmacion=pedir_confirm
    )

@router.post("/reentrenar-automatico", status_code=202)
def reentrenar_automatico(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin"))
):
    frases = db.query(models.FraseEntrenamiento).filter(models.FraseEntrenamiento.intencion != "pendiente").all()
    textos = [f.frase for f in frases]
    etiquetas = [f.intencion for f in frases]
    entrenar_modelo(textos, etiquetas)
    recargar_modelo()
    return {"mensaje": "Reentrenamiento automático ejecutado"}

@router.post("/feedback", status_code=204)
def feedback(data: FeedbackIn,
            db: Session = Depends(get_db),
            _: models.Usuario = Depends(require_roles("admin","empleado","cliente"))):
    inter = db.query(models.Interaccion).filter_by(id=data.interaccion_id).first()
    if not inter:
        raise HTTPException(404, "Interacción no encontrada")

    if data.accion == "confirmar":
        inter.estado = "confirmada"
        if not inter.intent_final:
            inter.intent_final = inter.intent_predicha
    elif data.accion == "corregir":
        if not data.intent_final:
            raise HTTPException(400, "Falta intent_final para corrección")
        inter.intent_final = data.intent_final
        inter.estado = "corregida"
    elif data.accion == "descartar":
        inter.estado = "descartada"

    db.commit()
    return

@router.post("/reentrenar", status_code=202)
def reentrenar_modelo(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_roles("admin"))
):
    frases = db.query(models.FraseEntrenamiento).all()
    textos = [f.frase for f in frases]
    etiquetas = [f.intencion for f in frases]

    entrenar_modelo(textos, etiquetas)
    recargar_modelo()
    return {"mensaje": "Modelo reentrenado y recargado"}


@router.post("/ejecutar-comando")
def ejecutar_comando(
    entrada: TextoEntrada,
    request: Request, 
    user: models.Usuario = Depends(get_current_user)
):
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    if not token:
        return {"respuesta": "❌ No se pudo obtener el token de autenticación."}

    texto = entrada.texto.lower()
    print(f"🧠 Comando recibido: '{texto}' | Rol: {user.rol}")

    # 🎯 Fallback manual prioritario
    if "cuánto cuesta" in texto or "precio de" in texto:
        intencion = "consultar_precio"
        nombre = texto.replace("cuánto cuesta", "").replace("precio de", "").strip()
        entidades = {"nombre": nombre}
    elif "cuántas unidades" in texto or "cantidad de" in texto or "cuántos productos" in texto:
        intencion = "consultar_cantidad"
        nombre = texto.replace("cuántas unidades", "").replace("cantidad de", "").replace("cuántos productos", "").strip()
        entidades = {"nombre": nombre}
    else:
        try:
            resultado = detectar_intencion(texto)
            intencion = resultado.get("intencion", "").replace(" ", "_").lower()
            entidades = resultado.get("entidades", {})
        except Exception as e:
            return {"respuesta": f"❌ Error al detectar intención: {str(e)}"}

    print(f"🎯 Intención detectada: {intencion} | Entidades: {entidades}")

    nombre = entidades.get("nombre") or entidades.get("producto")
    if nombre:
        nombre = nombre.replace("producto", "").strip()
    cantidad = entidades.get("cantidad")
    precio = entidades.get("precio")

    # 🧪 Fallback defensivo para cantidad y precio
    import re
    if cantidad is None:
        match = re.search(r"cantidad(?: de)? (\d+)", texto)
        if match:
            cantidad = match.group(1)
    if precio is None:
        match = re.search(r"precio(?: de)? (\d+)", texto)
        if match:
            precio = match.group(1)


    # 🧠 Fallback para frases no entendidas
    if not intencion or intencion == "no_entendida":
        db = SessionLocal()
        nueva_frase = models.FraseEntrenamiento(
            frase=texto,
            intencion="pendiente",
            fuente="auto_reentrenamiento",
            nombre=nombre or "",
            precio_real=str(precio) if precio else None,
            cantidad=cantidad if cantidad else None
        )
        db.add(nueva_frase)
        db.commit()
        db.close()
        return {"respuesta": "⚠️ No entendí el comando. Lo guardaré para mejorar."}

    intencion = entidades.get("intencion_forzada") or intencion
    print(f"🔧 Intención final a ejecutar: {intencion}")
    # 🎯 Ejecución por intención
    try:
        from Voz_Asistente import inventario, pedidos

        if intencion == "agregar_producto":
            return {"respuesta": inventario.agregar_producto(nombre, cantidad, precio, token)}

        elif intencion == "actualizar_producto":
            return {"respuesta": inventario.actualizar_producto(nombre, cantidad, precio, token)}

        elif intencion == "eliminar_producto":
            return {"respuesta": inventario.eliminar_producto(nombre, token)}

        elif intencion == "consultar_inventario":
            return {"respuesta": inventario.consultar_inventario(token)}

        elif intencion == "consultar_precio":
            return {"respuesta": inventario.consultar_precio_producto(nombre, token)}

        elif intencion == "consultar_cantidad":
            return {"respuesta": inventario.consultar_cantidad_producto(nombre, token)}

        elif intencion == "consultar_stock_bajo":
            return {"respuesta": inventario.productos_bajo_stock(token)}

        elif intencion == "consultar_inventario_por_cliente":
            if user.rol not in ["admin", "empleado"]:
                return {"respuesta": "⚠️ Solo administradores o empleados pueden consultar inventario por cliente."}
            cliente_id = entidades.get("cliente_id") or entidades.get("cliente")
            if not cliente_id:
                return {"respuesta": "⚠️ No se detectó el cliente para consultar inventario."}
            return {"respuesta": inventario.consultar_inventario_por_cliente(cliente_id, token)}

        elif intencion == "agregar_pedido":
            if user.rol not in ["cliente", "admin"]:
                return {"respuesta": "⚠️ Solo clientes o administradores pueden crear pedidos por voz."}
            
            direccion = entidades.get("direccion")
            if not nombre or not cantidad or not direccion:
                return {"respuesta": "⚠️ Faltan datos para crear el pedido."}
            
            print(f"📦 Ejecutando pedido: producto={nombre}, cantidad={cantidad}, direccion={direccion}")
            return {"respuesta": pedidos.crear_pedido(nombre, int(cantidad), direccion, token)}

        elif intencion == "ver_pedido":
            return {"respuesta": pedidos.ver_pedido(token)}

        elif intencion == "editar_pedido":
            if user.rol not in ["cliente", "admin"]:
                return {"respuesta": "⚠️ Solo clientes o administradores pueden editar pedidos."}
            pedido_id = entidades.get("pedido_id")
            nueva_cantidad = entidades.get("cantidad")
            if not pedido_id or not nueva_cantidad:
                return {"respuesta": "⚠️ Faltan datos para editar el pedido."}
            return {"respuesta": pedidos.modificar_pedido_cliente(pedido_id, int(nueva_cantidad), token)}

        elif intencion == "eliminar_pedido":
            if user.rol not in ["cliente", "admin"]:
                return {"respuesta": "⚠️ Solo clientes o administradores pueden eliminar pedidos."}
            pedido_id = entidades.get("pedido_id")
            if not pedido_id:
                return {"respuesta": "⚠️ No se detectó el ID del pedido a eliminar."}
            return {"respuesta": pedidos.eliminar_pedido(pedido_id, token)}

        elif intencion == "ver_pedido_detallado":
            if user.rol not in ["admin", "empleado"]:
                return {"respuesta": "⚠️ Solo administradores o empleados pueden ver pedidos detallados."}
            pedido_id = entidades.get("pedido_id") or entidades.get("id")
            if not pedido_id:
                return {"respuesta": "⚠️ No se detectó el ID del pedido a consultar."}
            return {"respuesta": pedidos.ver_pedido_por_id(pedido_id, token)}

        elif intencion == "consultar_pedidos_por_cliente":
            if user.rol not in ["admin", "empleado"]:
                return {"respuesta": "⚠️ Solo administradores o empleados pueden consultar pedidos por cliente."}
            cliente_id = entidades.get("cliente_id") or entidades.get("cliente")
            if not cliente_id:
                return {"respuesta": "⚠️ No se detectó el cliente para consultar pedidos."}
            return {"respuesta": pedidos.consultar_pedidos_por_cliente(cliente_id, token)}

        elif intencion == "ver_historial_pedidos":
            if user.rol not in ["admin", "empleado"]:
                return {"respuesta": "⚠️ Solo administradores o empleados pueden ver historial de pedidos por cliente."}
            cliente_id = entidades.get("cliente_id") or entidades.get("cliente")
            if not cliente_id:
                return {"respuesta": "⚠️ No se detectó el cliente para consultar historial."}
            return {"respuesta": pedidos.ver_historial_pedidos(cliente_id, token)}

        elif intencion == "ver_movimientos_inventario":
            if user.rol not in ["admin", "empleado"]:
                return {"respuesta": "⚠️ Solo administradores o empleados pueden ver movimientos de inventario."}
            return {"respuesta": pedidos.ver_movimientos_inventario(token)}

        elif intencion == "descargar_historial_pedidos":
            if user.rol != "admin":
                return {"respuesta": "⚠️ Solo los administradores pueden descargar historial de pedidos."}
            cliente_id = entidades.get("cliente_id") or entidades.get("cliente")
            if not cliente_id:
                return {"respuesta": "⚠️ No se detectó el cliente para generar el historial."}
            return {"respuesta": pedidos.generar_reporte_historial(cliente_id, token)}

        elif intencion == "descargar_reportes_globales":
            if user.rol != "admin":
                return {"respuesta": "⚠️ Solo los administradores pueden descargar reportes globales."}
            periodo = entidades.get("periodo") or "último mes"
            return {"respuesta": pedidos.generar_reporte_global(periodo, token)}
        elif intencion == "actualizar_estado_pedido":
            if user.rol not in ["empleado", "admin"]:
                return {"respuesta": "⚠️ Solo empleados o administradores pueden actualizar el estado de pedidos."}
            pedido_id = entidades.get("pedido_id")
            nuevo_estado = entidades.get("estado")
            if not pedido_id or not nuevo_estado:
                return {"respuesta": "⚠️ Faltan datos para actualizar el estado del pedido."}
            return {"respuesta": pedidos.actualizar_estado_pedido(pedido_id, nuevo_estado, token)}
        
        elif intencion == "ver_ruta":
            pedido_id = entidades.get("pedido_id")
            if not pedido_id:
                return {"respuesta": "⚠️ No se detectó el ID del pedido para consultar la ruta."}

            if user.rol not in ["admin", "empleado", "cliente"]:
                return {"respuesta": "⚠️ Solo clientes, empleados o administradores pueden consultar rutas."}

            from Voz_Asistente import rutas
            return {"respuesta": rutas.resumen_ruta_pedido(pedido_id, token)}

        else:
            return {"respuesta": f"⚠️ Intención '{intencion}' no ejecutable."}

    except Exception as e:
        return {"respuesta": f"❌ Error al ejecutar '{intencion}': {str(e)}"}


    