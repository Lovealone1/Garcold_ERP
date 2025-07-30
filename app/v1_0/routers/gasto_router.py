# app/v1_0/routers/gasto_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.gasto_schema import GastoRequestDTO, GastoResponseDTO
from app.v1_0.entities import GastoDTO

router = APIRouter(
    prefix="/gastos",
    tags=["Gastos"],
)

@router.post(
    "/crear",
    response_model=GastoResponseDTO,
    summary="Registra un nuevo gasto y descuenta su monto del banco"
)
@inject
async def crear_gasto(
    request: GastoRequestDTO,
    db: AsyncSession = Depends(get_db),
    gasto_service=Depends(Provide[ApplicationContainer.api_container.gasto_service])
):
    """
    Registra un gasto según el body y descuenta el monto del banco correspondiente.

    Body:
    - categoria_gasto_id: int
    - banco_id: int
    - monto: float
    - fecha_gasto: date
    """
    gasto_dto = GastoDTO(**request.dict())
    return await gasto_service.crear_gasto(gasto_dto, db=db)


@router.get(
    "/categoria/{categoria_id}",
    response_model=List[GastoResponseDTO],
    summary="Lista todos los gastos de una categoría específica"
)
@inject
async def listar_gastos_por_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    gasto_service=Depends(Provide[ApplicationContainer.api_container.gasto_service])
):
    """
    Recupera todos los gastos para la categoría indicada.
    """
    return await gasto_service.listar_gastos_por_categoria(categoria_id, db=db)


@router.delete(
    "/eliminar/{gasto_id}",
    response_model=dict,
    summary="Elimina un gasto y devuelve su monto al banco"
)
@inject
async def eliminar_gasto(
    gasto_id: int,
    db: AsyncSession = Depends(get_db),
    gasto_service=Depends(Provide[ApplicationContainer.api_container.gasto_service])
):
    """
    Elimina el gasto con el ID dado y devuelve el monto al banco asociado.
    """
    deleted = await gasto_service.eliminar_gasto(gasto_id, db=db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return {"mensaje": f"Gasto con ID {gasto_id} eliminado correctamente"}
