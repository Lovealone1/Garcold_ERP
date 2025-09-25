# app/v1_0/routers/venta_router.py

from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

# Schemas SOLO para entrada
from app.v1_0.schemas.venta_schema import VentaRequestDTO

# Entidades (salida)
from app.v1_0.entities import VentaListDTO, VentasPageDTO, DetalleVentaViewDTO
from app.v1_0.services.venta_service import VentaService

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.post(
    "/crear",
    response_model=VentaListDTO,
    summary="Registra una nueva venta",
)
@inject
async def crear_venta(
    request: VentaRequestDTO,
    db: AsyncSession = Depends(get_db),
    venta_service: VentaService = Depends(
        Provide[ApplicationContainer.api_container.venta_service]
    ),
):
    if not request.carrito:
        raise HTTPException(status_code=400, detail="El carrito no puede estar vacío")

    # El servicio ahora recibe el carrito crudo y arma los DetalleVentaDTO internamente
    return await venta_service.finalizar_venta(
        cliente_id=request.cliente_id,
        banco_id=request.banco_id,
        estado_id=request.estado_id,
        carrito=[c.model_dump() for c in request.carrito],  # si DetalleCarrito es pydantic
        db=db,
    )


@router.get(
    "/",
    response_model=VentasPageDTO,
    summary="Lista ventas paginadas",
)
@inject
async def listar_ventas(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    venta_service: VentaService = Depends(
        Provide[ApplicationContainer.api_container.venta_service]
    ),
) -> VentasPageDTO:
    return await venta_service.listar_ventas(page=page, db=db)


@router.get(
    "/{venta_id}",
    response_model=VentaListDTO,
    summary="Obtiene una venta por su ID",
)
@inject
async def obtener_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    venta_service: VentaService = Depends(
        Provide[ApplicationContainer.api_container.venta_service]
    ),
) -> VentaListDTO:
    return await venta_service.obtener_venta(venta_id, db=db)


@router.delete(
    "/eliminar/{venta_id}",
    response_model=Dict[str, str],
    summary="Elimina una venta y revierte inventario y saldos",
)
@inject
async def eliminar_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    venta_service: VentaService = Depends(
        Provide[ApplicationContainer.api_container.venta_service]
    ),
):
    await venta_service.eliminar_venta(venta_id, db=db)
    return {"mensaje": f"Venta con ID {venta_id} eliminada correctamente"}

@router.get(
    "/{venta_id}/detalles",
    response_model=List[DetalleVentaViewDTO],
    summary="Lista los detalles de una venta (producto_referencia, cantidad, precio, total)",
)
@inject
async def listar_detalles_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    venta_service: VentaService = Depends(
        Provide[ApplicationContainer.api_container.venta_service]
    ),
) -> List[DetalleVentaViewDTO]:
    return await venta_service.listar_detalles(venta_id=venta_id, db=db)