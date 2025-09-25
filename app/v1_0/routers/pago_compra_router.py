# app/v1_0/routers/pago_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.pago_venta_schema import PagoRequestDTO
from app.v1_0.entities import PagoResponseDTO

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)

@router.post(
    "/compras/{compra_id}",
    response_model=PagoResponseDTO,
    summary="Registra un pago sobre una compra a crédito"
)
@inject
async def crear_pago_compra(
    compra_id: int,
    request: PagoRequestDTO,
    db: AsyncSession = Depends(get_db),
    pago_compra_service=Depends(Provide[ApplicationContainer.api_container.pago_compra_service])
):
    """
    Body: { "banco_id": int, "monto": float }
    """
    return await pago_compra_service.crear_pago_compra(
        compra_id=compra_id,
        banco_id=request.banco_id,
        monto=request.monto,
        db=db
    )

@router.get(
    "/compras/{compra_id}",
    response_model=List[PagoResponseDTO],
    summary="Lista todos los pagos de una compra"
)
@inject
async def listar_pagos_compra(
    compra_id: int,
    db: AsyncSession = Depends(get_db),
    pago_compra_service=Depends(Provide[ApplicationContainer.api_container.pago_compra_service])
):
    return await pago_compra_service.listar_pagos_compra(compra_id, db=db)

@router.delete(
    "/compras/{pago_id}",
    response_model=dict,
    summary="Elimina un pago de compra por su ID"
)
@inject
async def eliminar_pago_compra(
    pago_id: int,
    db: AsyncSession = Depends(get_db),
    pago_compra_service=Depends(Provide[ApplicationContainer.api_container.pago_compra_service])
):
    """
    - pago_id: ID del registro de pago de compra a eliminar.
    """
    deleted = await pago_compra_service.eliminar_pago_compra(pago_id, db=db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return {"mensaje": f"Pago {pago_id} eliminado correctamente"}
