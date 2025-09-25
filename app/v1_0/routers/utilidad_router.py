from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from typing import List

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.entities import UtilidadListDTO, UtilidadPageDTO, DetalleUtilidadDTO
from app.v1_0.services.utilidad_service import UtilidadService

router = APIRouter(prefix="/utilidades", tags=["Utilidades"])

@router.get(
    "/",
    response_model=UtilidadPageDTO,
    summary="Lista utilidades paginadas"
)
@inject
async def listar_utilidades(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    service: UtilidadService = Depends(
        Provide[ApplicationContainer.api_container.utilidad_service]
    ),
):
    return await service.listar_utilidades(page, db)


@router.get(
    "/venta/{venta_id}",
    response_model=UtilidadListDTO,
    summary="Obtiene la utilidad por venta_id"
)
@inject
async def obtener_por_venta_id(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    service: UtilidadService = Depends(
        Provide[ApplicationContainer.api_container.utilidad_service]
    ),
):
    u = await service.obtener_por_venta_id(venta_id, db)
    if not u:
        raise HTTPException(status_code=404, detail="Utilidad no encontrada para la venta indicada")
    return UtilidadListDTO(id=u.id, venta_id=u.venta_id, utilidad=u.utilidad, fecha=u.fecha)


@router.get(
    "/venta/{venta_id}/detalles",
    response_model=List[DetalleUtilidadDTO],
    summary="Obtiene los detalles de la utilidad por venta_id"
)
@inject
async def obtener_detalles_por_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
    service: UtilidadService = Depends(
        Provide[ApplicationContainer.api_container.utilidad_service]
    ),
):
    detalles = await service.obtener_detalles_por_venta(venta_id, db)
    if not detalles:
        raise HTTPException(status_code=404, detail="No se encontraron detalles para la venta indicada")
    return detalles