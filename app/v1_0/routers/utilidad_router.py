from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.utilidad_schema import UtilidadListDTO
from app.v1_0.services.utilidad_service import UtilidadService

router = APIRouter(prefix="/utilidades", tags=["Utilidades"])


@router.get(
    "/",
    response_model=List[UtilidadListDTO],
    summary="Lista todas las utilidades paginadas"
)
@inject
async def listar_utilidades(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    service: UtilidadService = Depends(
        Provide[ApplicationContainer.api_container.utilidad_service]
    )
):
    try:
        utilidades = await service.listar_utilidades(page, db)
    except HTTPException:
        raise
    return [
        UtilidadListDTO(
            id=u.id,
            venta_id=u.venta_id,
            utilidad=u.utilidad,
            fecha=u.fecha
        )
        for u in utilidades
    ]


@router.get(
    "/rango",
    response_model=List[UtilidadListDTO],
    summary="Lista utilidades por rango de fechas paginadas"
)
@inject
async def listar_utilidades_por_rango(
    fecha_inicio: datetime = Query(..., description="Fecha inicial (YYYY-MM-DDTHH:MM:SS)"),
    fecha_fin:    datetime = Query(..., description="Fecha final (YYYY-MM-DDTHH:MM:SS)"),
    page:         int      = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    service: UtilidadService = Depends(
        Provide[ApplicationContainer.api_container.utilidad_service]
    )
):
    try:
        utilidades = await service.listar_utilidades_por_rango(fecha_inicio, fecha_fin, page, db)
    except HTTPException:
        raise
    return [
        UtilidadListDTO(
            id=u.id,
            venta_id=u.venta_id,
            utilidad=u.utilidad,
            fecha=u.fecha
        )
        for u in utilidades
    ]
