from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.services.estado_service import EstadoService
from app.v1_0.entities import EstadoDTO

router = APIRouter(prefix="/estados", tags=["Estados"])


@router.get(
    "/",
    response_model=List[EstadoDTO],
    summary="Lista todos los estados",
)
@inject
async def listar_estados(
    db: AsyncSession = Depends(get_db),
    estado_service: EstadoService = Depends(
        Provide[ApplicationContainer.api_container.estado_service]
    ),
) -> List[EstadoDTO]:
    try:
        return await estado_service.listar_estados(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando estados: {str(e)}")
