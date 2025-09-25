from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from datetime import datetime

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.entities import TransaccionPageDTO, TransaccionListDTO, TransaccionResponseDTO

router = APIRouter(
    prefix="/transacciones",
    tags=["Transacciones"],
)

@router.post(
    "/crear",
    response_model=TransaccionListDTO,
    summary="Registra una nueva transacción y ajusta el saldo del banco"
)
@inject
async def crear_transaccion(
    banco_id: int,
    tipo_id: int,
    monto: float,
    descripcion: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor que cero")

    return await transaccion_service.crear_transaccion(
        banco_id=banco_id,
        tipo_id=tipo_id,
        monto=monto,
        descripcion=descripcion,
        db=db
    )

@router.delete(
    "/eliminar/{transaccion_id}",
    response_model=dict,
    summary="Elimina una transacción manual y, si es de tipo Retiro/Ingreso, revierte saldo"
)
@inject
async def eliminar_transaccion(
    transaccion_id: int,
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    deleted = await transaccion_service.eliminar_transaccion_manual(
        transaccion_id=transaccion_id, db=db
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return {"mensaje": f"Transacción con ID {transaccion_id} eliminada correctamente"}

@router.get(
    "/",
    response_model=TransaccionPageDTO,
    summary="Lista todas las transacciones (paginado, 10 por página)"
)
@inject
async def listar_transacciones(
    page: int = Query(1, ge=1, description="Número de página (1-based)"),
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    return await transaccion_service.listar_transacciones(page, db)
