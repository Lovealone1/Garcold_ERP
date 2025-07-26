# app/v1_0/routers/venta_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.venta_schema import VentaRequestDTO, VentaResponse

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post(
    "/crear",
    response_model=VentaResponse,
    summary="Registra una nueva venta"
)
@inject
async def crear_venta(
    request: VentaRequestDTO,
    db: AsyncSession = Depends(get_db),
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    if not request.carrito:
        raise HTTPException(status_code=400, detail="El carrito no puede estar vacío")

    detalles = venta_service.agregar_detalle_venta(request.carrito)
    return await venta_service.finalizar_venta(
        cliente_id=request.cliente_id,
        banco_id=request.banco_id,
        estado_id=request.estado_id,
        detalles=detalles,
        db=db
    )

@router.get(
    "/obtener/{venta_id}",
    response_model=VentaResponse,
    summary="Obtiene una venta por su ID"
)
@inject
async def obtener_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    return await venta_service.obtener_venta(venta_id, db=db)

@router.delete(
    "/eliminar/{venta_id}",
    response_model=dict,
    summary="Elimina una venta y revierte inventario y saldos"
)
@inject
async def eliminar_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    await venta_service.eliminar_venta(venta_id, db=db)
    return {"mensaje": f"Venta con ID {venta_id} eliminada correctamente"}
