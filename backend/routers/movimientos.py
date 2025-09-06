from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend import models
from backend.auth.deps import get_db, require_roles
from backend.routers.schemas_movimientos import MovimientoResponse

router = APIRouter()

@router.get("/", response_model=List[MovimientoResponse])
def listar_movimientos(
    db: Session = Depends(get_db),
    user=Depends(require_roles("empleado", "admin"))
):
    return db.query(models.MovimientoInventario).order_by(models.MovimientoInventario.fecha.desc()).all()
