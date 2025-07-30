# app/v1_0/routers/pago_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.pago_venta_schema import PagoRequestDTO, PagoResponseDTO

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)

@router.post(
    "/ventas/{venta_id}",
    response_model=PagoResponseDTO,
    summary="Registra un pago sobre una venta a crédito"
)
@inject
async def crear_pago_venta(
    venta_id: int,
    request: PagoRequestDTO,
    db: AsyncSession = Depends(get_db),
    pago_venta_service=Depends(Provide[ApplicationContainer.api_container.pago_venta_service])
):
    """
    Body: { "banco_id": int, "monto": float }
    """
    return await pago_venta_service.crear_pago_venta(
        venta_id=venta_id,
        banco_id=request.banco_id,
        monto=request.monto,
        db=db
    )

@router.get(
    "/ventas/{venta_id}",
    response_model=List[PagoResponseDTO],
    summary="Lista todos los pagos de una venta"
)
@inject
async def listar_pagos_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    pago_venta_service=Depends(Provide[ApplicationContainer.api_container.pago_venta_service])
):
    return await pago_venta_service.listar_pagos_venta(venta_id, db=db)


@router.delete(
    "/ventas/{pago_id}",
    response_model=dict,
    summary="Elimina un pago de venta por su ID"
)
@inject
async def eliminar_pago_venta(
    pago_id: int,
    db: AsyncSession = Depends(get_db),
    pago_venta_service=Depends(Provide[ApplicationContainer.api_container.pago_venta_service])
):
    """
    - pago_id: ID del registro de pago de venta a eliminar.
    """
    deleted = await pago_venta_service.eliminar_pago_venta(pago_id, db=db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return {"mensaje": f"Pago {pago_id} eliminado correctamente"}
